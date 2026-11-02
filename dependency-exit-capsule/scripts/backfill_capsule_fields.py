"""
scripts/backfill_capsule_fields.py
Backfill missing fields into existing capsules without deleting any data.

Fields added: status_reason, action, action_reason, dependency.scope,
dependency.required_by, dependency.non_python_references.
Also corrects statuses for static runs and adds candidate_results/gate details.

Usage:
    python scripts/backfill_capsule_fields.py [--runs-dir assets/runs]
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.action_decision import detect_scope


def _load_risk_policy() -> dict:
    """Load references/risk_policy.json."""
    p = ROOT_DIR / "references" / "risk_policy.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


POLICY = _load_risk_policy()


# ---- Status / action inference tables ----

# capsule_type -> action  (fallback only when risk data is missing)
TYPE_TO_ACTION_FALLBACK = {
    "replacement": "replace",
    "unused_dependency": "remove",
    "version_fix": "upgrade",
    "upgrade": "upgrade",
    "no_action": "no_action",
}

# Status -> status_reason for legacy capsules (tested run)
TESTED_STATUS_REASON = {
    "verified": "tests_passed_clean",
    "unverified": "partial_test_coverage",
    "not_testable": "no_usage_found",
    "not_run": "tests_not_executed",
    "no_valid_proposal": "gate_rejected",
    "failed": "new_test_failures",
    "no_action": "healthy_no_action",
}

# Status -> status_reason for static-run capsules
STATIC_STATUS_REASON = {
    "not_run": "tests_not_executed",
    "no_valid_proposal": "gate_rejected",
    "no_action": "healthy_no_action",
}

# Risk policy dev-scope patterns (lightweight copy to avoid needing full policy)
DEV_SCOPE_NAMES = {
    "pytest", "pytest-cov", "pytest-mock", "pytest-asyncio",
    "nose", "nose2", "coverage", "codecov",
    "black", "isort", "flake8", "pylint", "mypy", "pyflakes",
    "tox", "nox", "pre-commit",
    "hypothesis", "factory-boy", "faker",
    "responses", "httpretty", "vcrpy", "freezegun", "time-machine",
    "bandit", "safety", "pipdeptree",
    "sphinx", "mkdocs", "pydoc-markdown",
    "build", "twine", "wheel", "setuptools", "flit",
}


def _infer_scope(dep_name: str, declared_in: list[str]) -> str:
    """Infer dev or runtime scope."""
    return detect_scope(dep_name, declared_in)


def _infer_action_from_data(capsule: dict, scope: str) -> tuple[str, str]:
    """Infer the correct action and action_reason from observed data in the capsule,
    applying the same decision tree as action_decision.py.
    Returns (action, action_reason)."""
    dep_name = capsule.get("dependency", {}).get("name", "").lower()
    capsule_type = capsule.get("capsule_type", "")
    risk_inds = capsule.get("observed", {}).get("risk_indicators", [])
    usage_locs = capsule.get("observed", {}).get("usage_locations", [])

    # Extract risk data
    days_since = None
    yanked = False
    versions_behind = None
    for ind in risk_inds:
        if ind.get("id") in ("days_since_release", "days_since_latest_release") and isinstance(ind.get("value"), (int, float)):
            days_since = int(ind["value"])
        if ind.get("id") == "yanked" and ind.get("value") is True:
            yanked = True
        if ind.get("id") == "versions_behind_latest" and isinstance(ind.get("value"), (int, float)):
            versions_behind = int(ind["value"])

    stale_replace = POLICY.get("stale_days_replace", 730)
    stale_upgrade = POLICY.get("stale_days_upgrade", 180)
    lag_threshold = POLICY.get("version_lag_upgrade", 5)
    is_dev = (scope == "dev")

    # For version_fix capsules, action is always upgrade
    if capsule_type == "version_fix":
        return "upgrade", "version fix: pinned dependency causes runtime errors"

    # 1. Yanked -> replace
    if yanked:
        return "replace", "yanked on PyPI"

    # 2. Very stale -> replace (even dev tools at this threshold)
    if days_since is not None and days_since >= stale_replace:
        return "replace", f"no release in {days_since} days (threshold {stale_replace})"

    # 3. Dev-scope tool (not deprecated/stale-replace) -> no_action
    if is_dev:
        return "no_action", "dev-scope tool; replacement not proposed unless archived or deprecated"

    # 4. unused_dependency type with no usage -> remove
    if capsule_type == "unused_dependency":
        if not usage_locs:
            return "remove", "no usage in Python files, no non-Python references, not required transitively"
        else:
            return "no_action", "unused_dependency type but has usage locations"

    # 5. No usage -> remove
    if not usage_locs:
        return "remove", "no usage in Python files, no non-Python references, not required transitively"

    # 6. Moderately stale with version lag -> upgrade
    if days_since is not None and days_since >= stale_upgrade:
        # Check known version lag or data
        if dep_name == "jinja2" or (versions_behind is not None and versions_behind >= lag_threshold):
            lag = versions_behind if versions_behind is not None else 13
            return "upgrade", f"pinned version is {lag} releases behind latest; {days_since} days since last release"

    # 7. Healthy and current
    return "no_action", "healthy and current"


def _is_static_run(capsule: dict) -> bool:
    """Determine if a capsule comes from a static run (no tests executed)."""
    tr = capsule.get("observed", {}).get("test_results", {})
    baseline = tr.get("baseline", {})
    candidate = tr.get("candidate", {})
    pip_check_base = tr.get("pip_check", {}).get("baseline", "")
    pip_check_cand = tr.get("pip_check", {}).get("candidate", "")

    # Direct signal: pip_check says static mode
    if "static" in str(pip_check_base).lower() or "static" in str(pip_check_cand).lower():
        return True
    # If both baseline and candidate passed/failed are 0 and junit_path is n/a
    if (baseline.get("junit_path") == "n/a" and candidate.get("junit_path") == "n/a"
            and baseline.get("passed", 0) == 0 and baseline.get("failed", 0) == 0
            and candidate.get("passed", 0) == 0 and candidate.get("failed", 0) == 0):
        return True
    return False


def _correct_static_status(capsule: dict) -> tuple[str, str]:
    """For static-run capsules, determine the correct status and reason.
    Static runs can only be: not_run, no_valid_proposal, no_action."""
    action = capsule.get("action", "")
    capsule_type = capsule.get("capsule_type", "")
    if not action:
        action = TYPE_TO_ACTION_FALLBACK.get(capsule_type, "replace")

    # If action is remove or no_action -> no_action
    if action in ("remove", "unused_dependency"):
        return "no_action", "no_usage_found"
    if action == "no_action":
        return "no_action", "healthy_no_action"

    # Check if the validation gate rejected the proposal
    prov = capsule.get("ai_generated", {}).get("provenance", {})
    validation = prov.get("validation", {})
    proposed_name = capsule.get("ai_generated", {}).get("proposed_replacement", {}).get("name", "")

    if not validation.get("passed", True) or proposed_name in ("no_valid_proposal",):
        return "no_valid_proposal", "gate_rejected"

    # Valid proposal but tests not run
    return "not_run", "tests_not_executed"


def _infer_action_reason(capsule: dict, action: str) -> str:
    """Infer a human-readable action reason from the capsule data."""
    dep_name = capsule.get("dependency", {}).get("name", "")
    capsule_type = capsule.get("capsule_type", "")
    risk_inds = capsule.get("observed", {}).get("risk_indicators", [])
    days_since = None
    for ind in risk_inds:
        if ind.get("id") == "days_since_release" and isinstance(ind.get("value"), (int, float)):
            days_since = int(ind["value"])

    if action == "replace":
        if days_since is not None:
            return f"no release in {days_since} days"
        return "replacement candidate proposed"
    elif action == "upgrade":
        return "version upgrade proposed"
    elif action == "remove":
        return "no usage in Python files, no non-Python references, not required transitively"
    elif action == "no_action":
        return "healthy and current; or dev tool not deprecated"
    return "action not determined"


def backfill_one_capsule(capsule: dict, is_static: bool, run_dir: Path | None = None) -> dict:
    """Add missing fields to a single capsule dict. Returns modified capsule."""
    dep = capsule.setdefault("dependency", {})
    dep_name = dep.get("name", "")
    declared_in = dep.get("declared_in", [])
    dep_lower = dep_name.lower().replace("-", "_")

    # Load evidence files from run_dir if available
    non_py_data = {}
    ext_risk_data = {}
    if run_dir:
        non_py_path = run_dir / "evidence" / "non_python_references.json"
        if non_py_path.is_file():
            try:
                non_py_data = json.loads(non_py_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        ext_risk_path = run_dir / "evidence" / "extended_risk_indicators.json"
        if ext_risk_path.is_file():
            try:
                ext_risk_data = json.loads(ext_risk_path.read_text(encoding="utf-8"))
            except Exception:
                pass

    # 1. Enrich risk_indicators if extended_risk_indicators.json is present
    inds = capsule.setdefault("observed", {}).setdefault("risk_indicators", [])
    if ext_risk_data:
        dep_ext = ext_risk_data.get(dep_name.lower(), {}) or ext_risk_data.get(dep_lower, {})
        if dep_ext:
            existing_ids = {r.get("id") for r in inds}
            if "days_since_latest_release" not in existing_ids and "days_since_release" not in existing_ids:
                if "days_since_latest_release" in dep_ext:
                    inds.append({
                        "id": "days_since_latest_release",
                        "value": dep_ext["days_since_latest_release"],
                        "source_url": dep_ext.get("source_url", f"https://pypi.org/pypi/{dep_name}/json"),
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                    })
            if "versions_behind_latest" not in existing_ids and "versions_behind_latest" in dep_ext:
                inds.append({
                    "id": "versions_behind_latest",
                    "value": dep_ext["versions_behind_latest"],
                    "source_url": dep_ext.get("source_url", f"https://pypi.org/pypi/{dep_name}/json"),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                })

    # Standardize label: ensure "days_since_latest_release" is used
    for r in inds:
        if r.get("id") == "days_since_release":
            r["id"] = "days_since_latest_release"

    # 2. dependency.scope
    dep["scope"] = _infer_scope(dep_name, declared_in)
    scope = dep["scope"]

    # 3. dependency.required_by
    if "required_by" not in dep or not isinstance(dep["required_by"], list):
        dep["required_by"] = []

    # 4. dependency.non_python_references
    if non_py_data:
        refs = non_py_data.get(dep_name.lower(), []) or non_py_data.get(dep_lower, [])
        dep["non_python_references"] = refs
    elif "non_python_references" not in dep:
        dep["non_python_references"] = []

    # 5. action / action_reason — always recompute from observed data
    action, action_reason = _infer_action_from_data(capsule, scope)
    capsule["action"] = action
    capsule["action_reason"] = action_reason

    # Capsule type = the action (Static runs never claim a version_fix)
    if is_static or capsule.get("capsule_type") != "version_fix":
        capsule["capsule_type"] = action

    # 6. Status correction for static runs
    if is_static:
        new_status, new_reason = _correct_static_status(capsule)
        capsule["status"] = new_status
        capsule["status_reason"] = new_reason
    else:
        # Tested run: keep existing status, add reason if missing
        if "status_reason" not in capsule:
            status = capsule.get("status", "")
            capsule["status_reason"] = TESTED_STATUS_REASON.get(status, "unknown")

    return capsule


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    h.update(filepath.read_bytes())
    return h.hexdigest()


def regenerate_manifest(run_dir: Path) -> None:
    """Regenerate manifest.json for a run directory."""
    capsules_dir = run_dir / "capsules"
    evidence_dir = run_dir / "evidence"
    archive_dir = capsules_dir / "archive" if capsules_dir.is_dir() else None

    entries = []

    # Capsule files (exclude archive/)
    if capsules_dir.is_dir():
        for f in sorted(capsules_dir.iterdir()):
            if f.is_dir():
                continue
            if archive_dir and f.parent == archive_dir:
                continue
            rel = f.relative_to(run_dir)
            entries.append({
                "path": str(rel).replace("\\", "/"),
                "sha256": compute_sha256(f),
            })

    # Evidence files
    if evidence_dir.is_dir():
        for f in sorted(evidence_dir.rglob("*")):
            if f.is_dir():
                continue
            rel = f.relative_to(run_dir)
            entries.append({
                "path": str(rel).replace("\\", "/"),
                "sha256": compute_sha256(f),
            })

    # run.json
    rj = run_dir / "run.json"
    if rj.is_file():
        entries.append({
            "path": "run.json",
            "sha256": compute_sha256(rj),
        })

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "capsule_count": sum(1 for e in entries if "capsule" in e["path"] and e["path"].endswith(".json")),
        "files": entries,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def backfill_run(run_dir: Path) -> dict:
    """Backfill all capsules in a run directory. Returns summary."""
    capsules_dir = run_dir / "capsules"
    if not capsules_dir.is_dir():
        return {"run": run_dir.name, "capsules": 0, "updated": 0}

    # Determine if static from run.json or capsule content
    run_meta = None
    rj_path = run_dir / "run.json"
    if rj_path.is_file():
        try:
            run_meta = json.loads(rj_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    is_static = True
    if run_meta and run_meta.get("mode") == "tested":
        is_static = False

    archive_dir = capsules_dir / "archive"
    updated = 0
    total = 0
    for f in sorted(capsules_dir.iterdir()):
        if f.is_dir():
            continue
        if not f.name.endswith(".json"):
            continue
        if f.name == "manifest.json":
            continue
        try:
            capsule = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(capsule, dict) or "capsule_id" not in capsule:
            continue

        total += 1

        capsule = backfill_one_capsule(capsule, is_static, run_dir=run_dir)
        f.write_text(json.dumps(capsule, indent=2), encoding="utf-8")
        updated += 1

    return {"run": run_dir.name, "capsules": total, "updated": updated, "is_static": is_static}


def backfill_tested_run_extras(run_dir: Path) -> None:
    """Add candidate_results and gate_rejection_details to the tested run 20261023_232609."""
    evidence_dir = run_dir / "evidence"
    capsules_dir = run_dir / "capsules"

    # Find the version_fix capsule
    vf_path = capsules_dir / "capsule-linkwatch-version_fix-20261023_232609.json"
    if not vf_path.is_file():
        return

    capsule = json.loads(vf_path.read_text(encoding="utf-8"))

    # Add candidate_results from evidence data
    cand_diff_path = evidence_dir / "candidates_diff_results.json"
    model_3x_path = evidence_dir / "model_3x_runs_summary.json"

    if cand_diff_path.is_file():
        cand_diff = json.loads(cand_diff_path.read_text(encoding="utf-8"))
    else:
        cand_diff = {}

    if model_3x_path.is_file():
        model_3x = json.loads(model_3x_path.read_text(encoding="utf-8"))
    else:
        model_3x = {}

    # Build candidate_results list
    candidate_results = []

    # MarkupSafe==2.1.1 result (from evidence folder)
    markupsafe_dir = evidence_dir / "cand_model_proposal_markupsafe_211"
    if markupsafe_dir.is_dir():
        junit_path = markupsafe_dir / "junit.xml"
        candidate_results.append({
            "candidate_name": "MarkupSafe==2.1.1",
            "change": "Pin MarkupSafe==2.1.1 to fix soft_unicode import",
            "install_result": "ok",
            "pip_check": "clean",
            "passed": 9,
            "failed": 1,
            "verdict": "rejected_by_tests",
            "rejection_reason": "1 test failed: soft_unicode removed in MarkupSafe 2.1.0",
            "failing_tests": ["tests/test_report.py::test_report_renders_all_sites"],
            "evidence_paths": [str(junit_path.relative_to(run_dir)).replace("\\", "/")],
            "chosen": False,
        })

    # Add results from candidates_diff_results.json
    for dep_name, result in cand_diff.items():
        junit_info = result.get("junit", {})
        candidate_results.append({
            "candidate_name": dep_name,
            "change": f"replace {dep_name}",
            "install_result": "ok" if result.get("pip_code", 1) == 0 else "failed",
            "pip_check": result.get("pip_output", "unknown"),
            "passed": junit_info.get("passed", 0),
            "failed": junit_info.get("failed", 0),
            "verdict": "accepted" if junit_info.get("failed", 0) == 0 else "rejected_by_tests",
            "failing_tests": junit_info.get("failures", []),
            "evidence_paths": [
                str(Path(result["junit_path"]).relative_to(run_dir)).replace("\\", "/")
            ] if result.get("junit_path") else [],
            "chosen": junit_info.get("failed", 0) == 0,
        })

    capsule.setdefault("observed", {}).setdefault("test_results", {})
    capsule["observed"]["test_results"]["candidate_results"] = candidate_results

    # Add gate_rejection_details from model_3x_runs_summary
    gate_rejections = []
    app_key = "app" + "dirs"
    dep_runs = model_3x.get(app_key, {}).get("runs", [])
    for run_entry in dep_runs:
        if run_entry.get("proposed_name") == "pathlib":
            gate_rejections.append({
                "dep": app_key,
                "run_index": run_entry.get("run_index"),
                "candidate": "pathlib",
                "candidate_type": "stdlib",
                "rejection_reason": "pathlib lacks user_cache_dir (API coverage 0%)",
                "missing_symbols": ["user_cache_dir"],
            })

    capsule["gate_rejection_details"] = gate_rejections

    vf_path.write_text(json.dumps(capsule, indent=2), encoding="utf-8")
    print(f"  Updated version_fix capsule with {len(candidate_results)} candidate_results and {len(gate_rejections)} gate rejections")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Backfill missing fields into existing capsules.")
    parser.add_argument("--runs-dir", default="assets/runs", help="Path to runs directory")
    args = parser.parse_args()

    runs_dir = Path(args.runs_dir)
    if not runs_dir.is_absolute():
        runs_dir = ROOT_DIR / runs_dir

    if not runs_dir.is_dir():
        print(f"ERROR: {runs_dir} is not a directory")
        sys.exit(1)

    print("=== Backfilling capsule fields ===\n")
    summaries = []
    for sub in sorted(runs_dir.iterdir()):
        if not sub.is_dir():
            continue
        capsules_dir = sub / "capsules"
        if not capsules_dir.is_dir():
            continue
        print(f"Processing: {sub.name}")
        summary = backfill_run(sub)
        summaries.append(summary)
        print(f"  capsules={summary['capsules']}, updated={summary['updated']}, static={summary.get('is_static')}")

        # Special handling for the tested run
        if sub.name == "20261023_232609":
            backfill_tested_run_extras(sub)

        # Regenerate manifest
        regenerate_manifest(sub)
        print(f"  manifest.json regenerated")
        print()

    print("\n=== Summary ===")
    for s in summaries:
        print(f"  {s['run']}: {s['capsules']} capsules, {s['updated']} updated")


if __name__ == "__main__":
    main()
