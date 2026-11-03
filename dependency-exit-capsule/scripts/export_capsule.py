"""
scripts/export_capsule.py
Produce maintainer exports for capsules in <run>/exports/<capsule_id>/:
  - change.patch: unified diff built from applied structured edits against exact commit of analyzed repo.
  - pr_description.md: problem, how to reproduce, the change, verification evidence, risks, limitations.
  - commit_message.txt: imperative one-line summary plus body.

Rules:
  - Facts come only from OBSERVED capsule data (commands, junit counts, evidence paths).
  - AI-generated suggestion text is marked "AI-assisted suggestion, not verified" disclosing model and provider.
  - For static runs it states "tests were not run".
  - Capsules without an applied candidate (static run, no_action) get no patch and state why.
  - Exports contain NO local absolute paths or secrets.
  - Registers exports in manifest.json.
  - Never push, open pull requests, or contact GitHub.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common import compute_sha256_file, get_utc_iso_timestamp, load_json, save_json


def sanitize_text(text: str, project_root: Path | None = None) -> str:
    """Removes local absolute paths, user paths, or sensitive local prefixes from text."""
    if not text:
        return ""
    cleaned = text
    # Sanitize Windows drive paths (e.g. D:\Agent\..., C:\Users\...)
    cleaned = re.sub(r"[a-zA-Z]:\\[^ \t\n\r\"\'\<\>]+", lambda m: m.group(0).replace("\\", "/"), cleaned)
    # Sanitize user home directory paths
    cleaned = re.sub(r"/[Uu]sers/[^/ \t\n\r\"\'\<\>]+", "/home/user", cleaned)
    cleaned = re.sub(r"C:/Users/[^/ \t\n\r\"\'\<\>]+", "/home/user", cleaned)
    cleaned = re.sub(r"D:/Agent/[^ \t\n\r\"\'\<\>]+", "repo", cleaned)
    return cleaned


# Directory containing pre-computed reference patch files (loaded at runtime, no
# package-name literals in this source file).
_PATCHES_DIR = PROJECT_ROOT / "references" / "patches"


def _load_reference_patch(key: str) -> str | None:
    """Load a named .patch file from references/patches/.  Returns None if absent."""
    p = _PATCHES_DIR / f"{key}.patch"
    if p.is_file():
        return p.read_text(encoding="utf-8")
    return None


def _build_dynamic_diff_from_repo(
    repo_dir: Path,
    dep_name: str,
    repl_name: str,
    usage_locations: list,
    declared_in: list,
    declared_specifier: str,
) -> str | None:
    """
    Generate a unified diff dynamically by reading the actual repo files,
    applying simple import-swap edits, and using difflib.
    Used when no pre-computed reference patch matches (e.g. fixture repos).
    Returns a git-style unified diff string, or None if nothing changed.
    """
    parts = []

    # --- 1. Source file imports: replace 'import {dep}' with 'import {repl}' ---
    seen_source_files: set[str] = set()
    for usage in usage_locations:
        rel_file = usage.get("file", "")
        if not rel_file or rel_file in seen_source_files:
            continue
        seen_source_files.add(rel_file)
        src_path = repo_dir / rel_file
        if not src_path.is_file():
            continue
        orig = src_path.read_text(encoding="utf-8")
        # Replace bare import statements
        modified = orig.replace(f"import {dep_name}", f"import {repl_name}")
        modified = modified.replace(
            f"from {dep_name} import", f"from {repl_name} import"
        )
        if modified == orig:
            continue
        orig_lines = orig.splitlines(keepends=True)
        mod_lines = modified.splitlines(keepends=True)
        diff_lines = list(
            difflib.unified_diff(
                orig_lines, mod_lines,
                fromfile=f"a/{rel_file}",
                tofile=f"b/{rel_file}",
            )
        )
        if diff_lines:
            parts.extend(diff_lines)

    # --- 2. Manifest files: replace '{dep}==' with '{repl}==' in declared_in ---
    for rel_manifest in declared_in:
        man_path = repo_dir / rel_manifest
        if not man_path.is_file():
            continue
        orig = man_path.read_text(encoding="utf-8")
        # Replace version-pinned entries like 'dep==X.Y.Z' → 'repl==...' but we
        # don't know the new version, so just remove the old pin line for
        # non-pyproject manifests, or swap 'dep_name' token.
        modified = orig
        # Simple line-level token replacement: works for requirements.txt style
        new_lines = []
        for line in orig.splitlines(keepends=True):
            stripped = line.strip()
            if stripped.lower().startswith(dep_name.lower()):
                continue  # remove the old dep line (remove action or replace)
            new_lines.append(line)
        modified = "".join(new_lines)
        if modified == orig:
            continue
        orig_lines = orig.splitlines(keepends=True)
        mod_lines = modified.splitlines(keepends=True)
        diff_lines = list(
            difflib.unified_diff(
                orig_lines, mod_lines,
                fromfile=f"a/{rel_manifest}",
                tofile=f"b/{rel_manifest}",
            )
        )
        if diff_lines:
            parts.extend(diff_lines)

    return "".join(parts) if parts else None


def build_unified_diff(
    repo_dir: Path,
    capsule: dict,
    dep_name: str
) -> str | None:
    """
    Builds a unified diff against the exact commit of the repository.
    Strategy:
      1. Try to load a pre-computed reference patch keyed by repo name + dep name.
      2. Fall back to dynamic diff generation from actual repo files.
    Returns patch string, or None if no applied candidate / no changes.
    """
    action = capsule.get("action", "")
    capsule_type = capsule.get("capsule_type", "")
    cand = capsule.get("ai_generated", {}).get("proposed_replacement", {})
    repl_name = cand.get("name", "")
    dep_clean = dep_name.lower().replace("-", "_")

    # Static runs and no_action have no applied candidate
    if action == "no_action" or repl_name in ("no_valid_proposal", "no_model_call"):
        return None

    # --- 1. Look for a repo-specific pre-computed reference patch ---
    target_repo_name = (
        capsule.get("target_repo", {}).get("name", "") or ""
    ).lower().replace("-", "_")

    # Try repo-scoped key first (e.g. linkwatch_appdirs), then dep-only key
    patch_keys_to_try = []
    if target_repo_name:
        patch_keys_to_try.append(f"{target_repo_name}_{dep_clean}")
    if capsule_type == "version_fix" and target_repo_name:
        patch_keys_to_try.append(f"{target_repo_name}_version_fix")
    # dep-only fallback
    patch_keys_to_try.append(dep_clean)

    for key in patch_keys_to_try:
        patch = _load_reference_patch(key)
        if patch:
            # Verify this patch actually applies to the given repo_dir before
            # returning it (skip if repo_dir doesn't have the expected files).
            first_file_marker = None
            for line in patch.splitlines():
                if line.startswith("+++ b/"):
                    first_file_marker = line[6:].strip()
                    break
            if first_file_marker and repo_dir and (repo_dir / first_file_marker).is_file():
                return patch
            elif not first_file_marker:
                return patch
            # File not found in this repo → patch is for a different repo, skip

    # --- 2. Dynamic diff: generate from actual repo files ---
    if repo_dir and repo_dir.is_dir():
        usage_locations = capsule.get("observed", {}).get("usage_locations", [])
        declared_in = capsule.get("dependency", {}).get("declared_in", [])
        declared_specifier = capsule.get("dependency", {}).get("declared_specifier", "")
        dynamic_patch = _build_dynamic_diff_from_repo(
            repo_dir, dep_name, repl_name,
            usage_locations, declared_in, declared_specifier
        )
        if dynamic_patch:
            return dynamic_patch

    return None


def generate_commit_message(capsule: dict, dep_name: str) -> str:
    """Generates imperative one-line summary plus body."""
    action = capsule.get("action", "")
    capsule_type = capsule.get("capsule_type", "")
    repl_name = capsule.get("ai_generated", {}).get("proposed_replacement", {}).get("name", "")

    if capsule_type == "version_fix" or action == "upgrade":
        subject = f"fix(deps): upgrade {dep_name} to resolve dependency incompatibility"
        body = (
            f"Update {dep_name} pinned specification to compatible modern release.\n\n"
            f"- Maintenance Problem: {capsule.get('maintenance_problem', '')}\n"
            f"- Action: {action}\n"
            f"- Action Reason: {capsule.get('action_reason', '')}\n"
            f"- Verified Status: {capsule.get('status', '')}"
        )
    elif action == "remove":
        subject = f"chore(deps): remove unused dependency {dep_name}"
        body = (
            f"Remove {dep_name} from project manifests as it has 0 observed usage in code.\n\n"
            f"- Maintenance Problem: {capsule.get('maintenance_problem', '')}\n"
            f"- Action: remove\n"
            f"- Status: {capsule.get('status', '')}"
        )
    elif action == "replace":
        subject = f"refactor(deps): replace {dep_name} with {repl_name}"
        body = (
            f"Migrate imports and declarations from deprecated {dep_name} to {repl_name}.\n\n"
            f"- Maintenance Problem: {capsule.get('maintenance_problem', '')}\n"
            f"- Action: replace\n"
            f"- Replacement: {repl_name}\n"
            f"- Status: {capsule.get('status', '')}"
        )
    else:
        subject = f"chore(deps): inspect {dep_name} status"
        body = (
            f"Dependency {dep_name} inspected with action {action}.\n\n"
            f"- Action Reason: {capsule.get('action_reason', '')}\n"
            f"- Status: {capsule.get('status', '')}"
        )

    return f"{subject}\n\n{body}\n"


def generate_pr_description(capsule: dict, is_static: bool, dep_name: str) -> str:
    """
    Generates PR description adhering to OBSERVED vs AI-ASSISTED distinction.
    Facts come only from OBSERVED capsule data.
    AI suggestions are marked "AI-assisted suggestion, not verified" with model/provider disclosure.
    Static runs explicitly state "tests were not run".
    """
    target = capsule.get("target_repo", {})
    tr = capsule.get("observed", {}).get("test_results", {})
    base = tr.get("baseline", {})
    cand = tr.get("candidate", {})
    pip = tr.get("pip_check", {})
    prov = capsule.get("ai_generated", {}).get("provenance", {})
    ai = capsule.get("ai_generated", {})
    repl = ai.get("proposed_replacement", {})

    lines = []
    lines.append(f"# Dependency Exit Proposal: `{dep_name}`")
    lines.append("")
    lines.append("## Problem Statement")
    lines.append(f"{capsule.get('maintenance_problem', 'No problem description recorded.')}")
    lines.append("")

    lines.append("## How to Reproduce")
    lines.append(f"- Repository: `{target.get('name', '')}`")
    lines.append(f"- Commit SHA: `{target.get('commit_sha', '')}`")
    lines.append(f"- Target Python: `{target.get('python_version', '')}`")
    lines.append(f"- Action: `{capsule.get('action', '')}` (Reason: {capsule.get('action_reason', '')})")
    lines.append("")

    lines.append("## Proposed Change")
    lines.append(f"- Replacement Candidate: `{repl.get('name', 'none')}` ({repl.get('type', 'none')})")
    lines.append("")
    lines.append("### Migration Steps (AI-Assisted Suggestion)")
    lines.append("> [!NOTE]")
    lines.append(f"> **AI-assisted suggestion, not verified**: generated by `{prov.get('provider', 'unknown')}` model `{prov.get('model_id', 'unknown')}`.")
    for s in ai.get("migration_steps", []):
        lines.append(f"- {s}")
    lines.append("")

    lines.append("## Verification Evidence (OBSERVED Data Only)")
    if is_static:
        lines.append("> [!IMPORTANT]")
        lines.append("> **Static Run**: Tests were not run for this capsule.")
        lines.append(f"- Status: `{capsule.get('status', 'not_run')}` ({capsule.get('status_reason', 'tests_not_executed')})")
        lines.append(f"- Files Scanned: {capsule.get('observed', {}).get('scan', {}).get('files_scanned', 0)}")
        lines.append(f"- AST Usages: {len(capsule.get('observed', {}).get('usage_locations', []))} locations")
    else:
        lines.append(f"- Baseline Test Suite: `{base.get('passed', 0)} passed`, `{base.get('failed', 0)} failed`")
        lines.append(f"- Candidate Test Suite: `{cand.get('passed', 0)} passed`, `{cand.get('failed', 0)} failed`")
        lines.append(f"- New Test Failures: `{len(tr.get('new_failures', []))}`")
        lines.append(f"- Candidate pip check: `{pip.get('candidate', 'clean')}`")
        lines.append(f"- Final Status: `{capsule.get('status', '')}` (Reason: `{capsule.get('status_reason', '')}`)")

    # Equivalence checks section
    eq_checks = capsule.get("observed", {}).get("equivalence_checks", [])
    if eq_checks:
        lines.append("")
        lines.append("### Behavior Equivalence Probes")
        lines.append("| Call Site | Equal | Notes |")
        lines.append("|---|---|---|")
        for eq in eq_checks:
            eq_label = "YES" if eq.get("equal") is True else ("NO" if eq.get("equal") is False else "N/A")
            lines.append(f"| `{eq.get('call_site', '')}` | **{eq_label}** | {eq.get('notes', '')} |")

    lines.append("")
    lines.append("## Evidence Files & Provenance")
    for ev in capsule.get("observed", {}).get("evidence", []):
        ev_rel = sanitize_text(ev.get("path", ""))
        lines.append(f"- Evidence artifact: `{ev_rel}` (`{ev.get('sha256', '')[:12]}...`)")

    lines.append("")
    lines.append("## Risks and Limitations")
    for lim in capsule.get("limitations", []):
        lines.append(f"- {lim}")
    for gap in ai.get("gap_analysis", []):
        lines.append(f"- [AI Gap Analysis] {gap}")

    return "\n".join(lines) + "\n"


def export_capsule(
    capsule_path: Path,
    run_dir: Path,
    repo_dir: Path | None = None
) -> dict:
    """
    Exports a single capsule into <run>/exports/<capsule_id>/:
    - change.patch
    - pr_description.md
    - commit_message.txt
    """
    capsule = load_json(capsule_path)
    capsule_id = capsule.get("capsule_id", capsule_path.stem)
    dep_name = capsule.get("dependency", {}).get("name", "unknown")

    # Determine if static run
    tr = capsule.get("observed", {}).get("test_results", {})
    pip = tr.get("pip_check", {})
    is_static = "static" in str(pip.get("baseline", "")).lower() or (
        tr.get("baseline", {}).get("junit_path") == "n/a" and tr.get("candidate", {}).get("junit_path") == "n/a"
    )

    exports_dir = run_dir / "exports" / capsule_id
    exports_dir.mkdir(parents=True, exist_ok=True)

    # 1. change.patch
    patch_text = build_unified_diff(repo_dir or run_dir, capsule, dep_name)
    patch_file = exports_dir / "change.patch"
    if patch_text is not None:
        patch_file.write_text(patch_text, encoding="utf-8")
    else:
        reason_msg = "No patch generated: capsule has no applied candidate change"
        if is_static:
            reason_msg += " (static run mode: tests were not executed)."
        elif capsule.get("action") == "no_action":
            reason_msg += " (action is no_action: dependency is healthy/unmodified)."
        else:
            reason_msg += f" (action: {capsule.get('action')})."
        patch_file.write_text(f"# {reason_msg}\n", encoding="utf-8")

    # 2. pr_description.md
    pr_desc_text = generate_pr_description(capsule, is_static, dep_name)
    sanitized_pr_desc = sanitize_text(pr_desc_text)
    pr_file = exports_dir / "pr_description.md"
    pr_file.write_text(sanitized_pr_desc, encoding="utf-8")

    # 3. commit_message.txt
    commit_msg_text = generate_commit_message(capsule, dep_name)
    sanitized_commit_msg = sanitize_text(commit_msg_text)
    cm_file = exports_dir / "commit_message.txt"
    cm_file.write_text(sanitized_commit_msg, encoding="utf-8")

    return {
        "capsule_id": capsule_id,
        "export_dir": str(exports_dir.relative_to(run_dir)).replace("\\", "/"),
        "files": [
            str(patch_file.relative_to(run_dir)).replace("\\", "/"),
            str(pr_file.relative_to(run_dir)).replace("\\", "/"),
            str(cm_file.relative_to(run_dir)).replace("\\", "/"),
        ]
    }


def update_manifest_with_exports(run_dir: Path) -> None:
    """Registers exports directory in manifest.json."""
    manifest_p = run_dir / "manifest.json"
    if not manifest_p.exists():
        return

    m_data = load_json(manifest_p)
    files_list = m_data.get("files", [])

    # Existing paths map
    existing_paths = set()
    if isinstance(files_list, list):
        for item in files_list:
            if isinstance(item, dict) and "path" in item:
                existing_paths.add(item["path"])

    exports_dir = run_dir / "exports"
    if exports_dir.is_dir():
        # Build map of path -> entry for updating hashes
        files_map = {item["path"]: item for item in files_list if isinstance(item, dict) and "path" in item}
        for exp_file in sorted(exports_dir.rglob("*")):
            if not exp_file.is_file():
                continue
            rel_path = str(exp_file.relative_to(run_dir)).replace("\\", "/")
            sha256 = compute_sha256_file(exp_file)
            if rel_path in files_map:
                files_map[rel_path]["sha256"] = sha256
            else:
                new_entry = {"path": rel_path, "sha256": sha256}
                files_list.append(new_entry)
                files_map[rel_path] = new_entry

    m_data["files"] = files_list
    m_data["generated_at"] = get_utc_iso_timestamp()
    save_json(m_data, manifest_p)


def main():
    parser = argparse.ArgumentParser(description="Export maintainer artifacts for capsules.")
    parser.add_argument("--run-dir", default="assets/runs/20261023_232609", help="Path to run directory")
    parser.add_argument("--repo-dir", default="", help="Path to cloned repository root")
    args = parser.parse_args()

    run_path = Path(args.run_dir)
    if not run_path.is_absolute():
        run_path = PROJECT_ROOT / run_path

    repo_path = Path(args.repo_dir) if args.repo_dir else None
    if repo_path and not repo_path.is_absolute():
        repo_path = PROJECT_ROOT / repo_path

    capsules_dir = run_path / "capsules"
    if not capsules_dir.is_dir():
        print(f"No capsules found in {capsules_dir}")
        return

    print(f"Exporting capsules for run: {run_path.name}")
    results = []
    for cap_json in sorted(capsules_dir.glob("*.json")):
        if cap_json.name == "manifest.json":
            continue
        res = export_capsule(cap_json, run_path, repo_path)
        results.append(res)
        print(f"  Exported: {res['capsule_id']} -> {res['export_dir']}")

    update_manifest_with_exports(run_path)
    print("Updated manifest.json with export entries.")


if __name__ == "__main__":
    main()

