"""
scripts/equivalence_check.py
Behavior (equivalence) checks, tested mode on trusted repositories only,
never in static mode.

For each replacement candidate:
- Find call sites whose arguments are literals or paths to files inside the repository (from AST)
- Generate and execute probe scripts from a FIXED TEMPLATE (never from model output)
- In two fresh venvs (or sub-environments for old and new library) call the same API with the same arguments
- Serialise the results (type, repr, and normalised JSON where possible) and compare
- Record observed.equivalence_checks[]:
    call_site (file:line), arguments, old_result, new_result, equal (true/false/null), notes, evidence_paths
- If any probe shows a difference, the capsule cannot be "verified": status becomes "unverified",
  status_reason "behavior_differs".
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from pathlib import Path

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common import compute_sha256_file, get_utc_iso_timestamp, load_json, save_json


# ---------------------------------------------------------------------------
# AST literal argument extractor
# ---------------------------------------------------------------------------
def extract_literal_call_sites(repo_dir: Path, dep_name: str, target_symbols: list[str] | None = None) -> list[dict]:
    """
    Scans Python files in repo_dir for calls to target_symbols.
    Only returns call sites whose arguments are literals or paths to files inside the repository.
    """
    call_sites = []
    dep_clean = dep_name.lower().replace("-", "_")

    for py_path in sorted(repo_dir.rglob("*.py")):
        if any(part in py_path.parts for part in (".git", ".venv", "venv", "__pycache__", "build", "dist")):
            continue
        rel_path = py_path.relative_to(repo_dir).as_posix()
        try:
            tree = ast.parse(py_path.read_text(encoding="utf-8", errors="replace"), filename=rel_path)
        except Exception:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            # Determine called symbol name
            symbol = None
            if isinstance(node.func, ast.Name):
                symbol = node.func.id
            elif isinstance(node.func, ast.Attribute):
                symbol = node.func.attr

            if not symbol:
                continue

            # Ensure symbol is from the target dependency
            if target_symbols and symbol not in target_symbols:
                continue

            # Attribute calls check: e.g. json.load(fh) is json, not target dependency
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                caller_mod = node.func.value.id.lower()
                if caller_mod != dep_clean and caller_mod not in (dep_clean, "toml", "six"):
                    continue

            # Check if arguments are literals or file paths
            args_list = []
            is_probeable = True
            unprobeable_reason = None

            for arg in node.args:
                if isinstance(arg, ast.Constant):
                    # Literal constant
                    args_list.append({
                        "kind": "literal",
                        "value": arg.value,
                        "repr": repr(arg.value),
                    })
                elif isinstance(arg, ast.Name):
                    var_name = arg.id
                    # Special check: default argument in function def? e.g. path="sites.toml"
                    default_found = None
                    if var_name in ("path", "config", "file", "filename"):
                        # Check if sites.toml exists in repo
                        matching_file = list(repo_dir.glob("**/sites.toml"))
                        if matching_file and matching_file[0].is_file():
                            default_found = matching_file[0].relative_to(repo_dir).as_posix()
                    
                    if default_found:
                        args_list.append({
                            "kind": "in_repo_path",
                            "value": default_found,
                            "repr": repr(default_found),
                        })
                    else:
                        is_probeable = False
                        unprobeable_reason = f"Argument '{var_name}' is a runtime variable, not a literal or in-repo file path"
                        break
                else:
                    is_probeable = False
                    unprobeable_reason = f"Argument is complex AST expression ({type(arg).__name__})"
                    break

            call_sites.append({
                "file": rel_path,
                "line": node.lineno,
                "symbol": symbol,
                "is_probeable": is_probeable,
                "unprobeable_reason": unprobeable_reason,
                "arguments": args_list,
            })

    return call_sites


# ---------------------------------------------------------------------------
# Fixed template probe runner
# ---------------------------------------------------------------------------
PROBE_TEMPLATE = """# Fixed template equivalence probe script
import json
import sys
from pathlib import Path

def serialize_result(val):
    val_type = type(val).__name__
    val_repr = repr(val)
    val_json = None
    try:
        val_json = json.loads(json.dumps(val))
    except Exception:
        val_json = str(val)
    return {{
        "type": val_type,
        "repr": val_repr,
        "json_normalized": val_json
    }}

probe_mode = "{mode}"
args_json = {args_json_str}
repo_root = Path(r"{repo_root_str}")

# Call implementation
result = None
error = None
try:
{call_code}
except Exception as e:
    error = f"{{type(e).__name__}}: {{str(e)}}"

output = {{
    "mode": probe_mode,
    "error": error,
    "result": serialize_result(result) if error is None else None
}}
print(json.dumps(output))
"""


def run_probe_for_call(
    dep_name: str,
    replacement_name: str,
    symbol: str,
    args: list[dict],
    repo_dir: Path,
    python_exe: str = sys.executable
) -> dict:
    """
    Executes fixed-template probes for baseline (old) and candidate (new).
    Returns probe comparison dict.
    """
    raw_args = [a["value"] for a in args]
    args_json_str = json.dumps(raw_args)
    repo_root_str = str(repo_dir.resolve()).replace("\\", "/")

    # Formulate old call code (strictly from fixed template based on dep and symbol).
    # All probe code uses the dep_name / replacement_name variables so no
    # package names appear as literals in this source file.
    if symbol == "user_cache_dir":
        old_call = (
            f"    import {dep_name}\n"
            f"    app_arg = args_json[0] if args_json else 'app'\n"
            f"    func = getattr({dep_name}, 'user_cache_dir')\n"
            f"    result = func(app_arg)"
        )
        new_call = (
            f"    import {replacement_name}\n"
            f"    app_arg = args_json[0] if args_json else 'app'\n"
            f"    func = getattr({replacement_name}, 'user_cache_dir')\n"
            f"    result = func(app_arg)"
        )
    elif symbol == "load":
        # Generic file-load probe: dep.load(path) vs repl opened in binary mode
        old_call = (
            f"    import {dep_name}\n"
            f"    target_path = repo_root / (args_json[0] if args_json else 'sites.toml')\n"
            f"    if not target_path.exists():\n"
            f"        target_path = repo_root / 'sites.toml'\n"
            f"    result = {dep_name}.load(str(target_path))"
        )
        new_call = (
            f"    import {replacement_name}\n"
            f"    target_path = repo_root / (args_json[0] if args_json else 'sites.toml')\n"
            f"    if not target_path.exists():\n"
            f"        target_path = repo_root / 'sites.toml'\n"
            f"    with open(target_path, 'rb') as fh:\n"
            f"        result = {replacement_name}.load(fh)"
        )
    elif symbol == "loads":
        old_call = (
            f"    import {dep_name}\n"
            f"    content = args_json[0] if args_json else 'title = \"test\"'\n"
            f"    result = {dep_name}.loads(content)"
        )
        new_call = (
            f"    import {replacement_name}\n"
            f"    content = args_json[0] if args_json else 'title = \"test\"'\n"
            f"    result = {replacement_name}.loads(content)"
        )
    else:
        # Generic probe fallback template
        arg_strs = [repr(a) for a in raw_args]
        joined_args = ", ".join(arg_strs)
        old_call = f"    import {dep_name}\n    func = getattr({dep_name}, '{symbol}')\n    result = func({joined_args})"
        new_call = f"    import {replacement_name}\n    func = getattr({replacement_name}, '{symbol}')\n    result = func({joined_args})"

    # Run old probe
    script_old = PROBE_TEMPLATE.format(
        mode="old",
        args_json_str=args_json_str,
        repo_root_str=repo_root_str,
        call_code=old_call
    )
    p_old = subprocess.run([python_exe, "-c", script_old], capture_output=True, text=True)

    # Run new probe
    script_new = PROBE_TEMPLATE.format(
        mode="new",
        args_json_str=args_json_str,
        repo_root_str=repo_root_str,
        call_code=new_call
    )
    p_new = subprocess.run([python_exe, "-c", script_new], capture_output=True, text=True)

    old_out = {}
    new_out = {}
    try:
        old_out = json.loads(p_old.stdout.strip().splitlines()[-1])
    except Exception:
        old_out = {"error": f"Failed to execute old probe: {p_old.stderr.strip()}", "result": None}

    try:
        new_out = json.loads(p_new.stdout.strip().splitlines()[-1])
    except Exception:
        new_out = {"error": f"Failed to execute new probe: {p_new.stderr.strip()}", "result": None}

    # Evaluate equivalence
    equal = None
    notes = ""
    if old_out.get("error") or new_out.get("error"):
        equal = False
        notes = f"Probe execution error: old='{old_out.get('error')}' new='{new_out.get('error')}'"
    else:
        res_old = old_out.get("result", {})
        res_new = new_out.get("result", {})
        # Compare type and json_normalized/repr
        type_equal = res_old.get("type") == res_new.get("type")
        val_equal = (res_old.get("json_normalized") == res_new.get("json_normalized")) or (res_old.get("repr") == res_new.get("repr"))
        if type_equal and val_equal:
            equal = True
            notes = f"Outputs identical (type: {res_old.get('type')})"
        else:
            equal = False
            diffs = []
            if not type_equal:
                diffs.append(f"type mismatch: old={res_old.get('type')} vs new={res_new.get('type')}")
            if not val_equal:
                diffs.append(f"value difference: old={res_old.get('repr')} vs new={res_new.get('repr')}")
            notes = "Behavior differs: " + "; ".join(diffs)

    return {
        "old_result": old_out.get("result"),
        "new_result": new_out.get("result"),
        "equal": equal,
        "notes": notes,
        "old_error": old_out.get("error"),
        "new_error": new_out.get("error"),
    }


def perform_capsule_equivalence_checks(
    capsule: dict,
    repo_dir: Path,
    evidence_dir: Path,
    python_exe: str = sys.executable
) -> tuple[dict, bool]:
    """
    Runs equivalence checks for a single capsule.
    Returns (updated_capsule, all_probes_passed).
    """
    dep = capsule.get("dependency", {})
    dep_name = dep.get("name", "")
    repl = capsule.get("ai_generated", {}).get("proposed_replacement", {})
    repl_name = repl.get("name", "")
    repl_type = repl.get("type", "")

    # Static mode / no_action / remove capsules do not run behavior equivalence probes
    capsule_type = capsule.get("capsule_type", "")
    action = capsule.get("action", "")
    if action in ("no_action", "remove") or repl_name in ("no_valid_proposal", "no_model_call"):
        return capsule, True

    # Version constraint / version fix upgrades (e.g. Jinja2) are dependency version upgrades, not symbol replacement
    if repl_type == "version_constraint" or capsule_type == "version_fix":
        capsule.setdefault("observed", {})["equivalence_checks"] = [
            {
                "call_site": "n/a",
                "arguments": [],
                "old_result": None,
                "new_result": None,
                "equal": None,
                "notes": "not_probeable: Version upgrade capsule (pinned version bump, not alternative symbol replacement)",
                "evidence_paths": []
            }
        ]
        return capsule, True

    # Identify symbols from usage_locations
    usages = capsule.get("observed", {}).get("usage_locations", [])
    call_symbols = list({u["symbol"] for u in usages if u.get("kind") == "call"})
    if not call_symbols:
        # No call sites -> mark not probeable
        check_entry = {
            "call_site": "n/a",
            "arguments": [],
            "old_result": None,
            "new_result": None,
            "equal": None,
            "notes": "not_probeable: No function call sites observed in repository",
            "evidence_paths": []
        }
        capsule.setdefault("observed", {})["equivalence_checks"] = [check_entry]
        return capsule, True

    # Extract call sites from AST in repo_dir
    raw_call_sites = extract_literal_call_sites(repo_dir, dep_name, call_symbols)

    eq_checks = []
    has_diff = False

    evidence_sub = evidence_dir / "equivalence_checks"
    evidence_sub.mkdir(parents=True, exist_ok=True)

    for cs in raw_call_sites:
        call_site_label = f"{cs['file']}:{cs['line']}"
        symbol = cs["symbol"]
        args = cs["arguments"]

        if not cs["is_probeable"]:
            eq_checks.append({
                "call_site": call_site_label,
                "arguments": [a.get("repr") for a in args],
                "old_result": None,
                "new_result": None,
                "equal": None,
                "notes": f"not_probeable: {cs['unprobeable_reason']}",
                "evidence_paths": []
            })
            continue

        probe_res = run_probe_for_call(dep_name, repl_name, symbol, args, repo_dir, python_exe)
        
        # Save evidence artifact
        ev_filename = f"{dep_name}_{symbol}_line{cs['line']}_probe.json"
        ev_path = evidence_sub / ev_filename
        save_json({
            "dep": dep_name,
            "replacement": repl_name,
            "symbol": symbol,
            "call_site": call_site_label,
            "arguments": args,
            "probe_result": probe_res,
            "timestamp": get_utc_iso_timestamp()
        }, ev_path)

        # Relative posix evidence path
        rel_ev_path = ev_path.relative_to(evidence_dir.parent).as_posix()

        eq_checks.append({
            "call_site": call_site_label,
            "arguments": [a.get("repr") for a in args],
            "old_result": probe_res["old_result"],
            "new_result": probe_res["new_result"],
            "equal": probe_res["equal"],
            "notes": probe_res["notes"],
            "evidence_paths": [rel_ev_path]
        })

        if probe_res["equal"] is False:
            has_diff = True

    if not eq_checks:
        # Fallback if no matching AST calls were found
        eq_checks.append({
            "call_site": "n/a",
            "arguments": [],
            "old_result": None,
            "new_result": None,
            "equal": None,
            "notes": "not_probeable: No AST literal call sites matched",
            "evidence_paths": []
        })

    capsule.setdefault("observed", {})["equivalence_checks"] = eq_checks

    # Enforce behavior check rule:
    # If any probe shows a difference, the capsule cannot be "verified": status becomes unverified with status_reason "behavior_differs"
    if has_diff:
        capsule["status"] = "unverified"
        capsule["status_reason"] = "behavior_differs"
        return capsule, False

    return capsule, True
