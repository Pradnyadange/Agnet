"""
tests/test_phase3_stage_a.py
Tests for Phase 3 Stage A:
- Maintainer exports:
    * Patch applies cleanly to fixture repository with git apply --check
    * No local paths or sensitive paths in exports
    * Static run exports state that tests were not run
- Behavior (equivalence) checks:
    * Equivalent fixture yields equal=True, status verified
    * Differing behavior fixture (e.g. str vs Path or text vs binary) yields equal=False,
      status unverified with status_reason='behavior_differs'
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.export_capsule import export_capsule, sanitize_text, build_unified_diff
from scripts.equivalence_check import perform_capsule_equivalence_checks, extract_literal_call_sites, run_probe_for_call


def test_export_patch_applies_cleanly_to_fixture(tmp_path):
    """Verify that export_capsule creates a patch that applies cleanly with git apply --check."""
    fixture_repo = PROJECT_ROOT / "tests" / "fixtures" / "sample_repo"
    assert fixture_repo.is_dir()

    # Create a git repo inside tmp_path
    repo_copy = tmp_path / "repo"
    shutil.copytree(fixture_repo, repo_copy)
    subprocess.run(["git", "init"], cwd=repo_copy, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_copy, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_copy, capture_output=True, check=True)
    subprocess.run(["git", "add", "."], cwd=repo_copy, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo_copy, capture_output=True, check=True)

    # Synthetic capsule
    capsule = {
        "schema_version": "2.0.0",
        "capsule_id": "capsule-sample-toml-test",
        "generated_at": "2026-11-03T00:00:00Z",
        "capsule_type": "replace",
        "action": "replace",
        "action_reason": "stale dependency",
        "status": "verified",
        "status_reason": "tests_passed_clean",
        "target_repo": {
            "name": "sample_repo",
            "url": "https://github.com/example/sample_repo",
            "commit_sha": "abc1234",
            "python_version": "3.12"
        },
        "dependency": {
            "name": "toml",
            "declared_specifier": "==0.10.2",
            "declared_in": ["requirements.txt", "pyproject.toml"]
        },
        "observed": {
            "risk_indicators": [],
            "scan": {"files_scanned": 2, "dynamic_imports": []},
            "usage_locations": [{"file": "sample_pkg/core.py", "line": 5, "symbol": "loads", "kind": "call", "covered_by_tests": True}],
            "test_results": {
                "baseline": {"passed": 2, "failed": 0, "junit_path": "evidence/junit.xml"},
                "candidate": {"passed": 2, "failed": 0, "junit_path": "evidence/junit.xml"},
                "new_failures": [],
                "pip_check": {"baseline": "clean", "candidate": "clean"}
            },
            "evidence": []
        },
        "ai_generated": {
            "proposed_replacement": {"name": "tomllib", "type": "stdlib"},
            "migration_steps": ["Replace import toml with import tomllib"],
            "suggested_tests": ["test_loads"],
            "gap_analysis": ["read only"],
            "provenance": {"provider": "test", "model_id": "test_model"}
        },
        "limitations": ["none"]
    }

    run_dir = tmp_path / "run"
    capsules_dir = run_dir / "capsules"
    capsules_dir.mkdir(parents=True)
    cap_file = capsules_dir / "capsule-sample-toml-test.json"
    cap_file.write_text(json.dumps(capsule, indent=2), encoding="utf-8")

    res = export_capsule(cap_file, run_dir, repo_dir=repo_copy)
    patch_p = run_dir / res["files"][0]
    assert patch_p.is_file()

    # Apply check
    apply_res = subprocess.run(["git", "apply", "--check", "--ignore-whitespace", str(patch_p.resolve())], cwd=repo_copy, capture_output=True, text=True)
    assert apply_res.returncode == 0, f"git apply --check failed: {apply_res.stderr}"


def test_export_no_local_paths_and_static_statement(tmp_path):
    """Verify that export files have no local absolute paths and static runs explicitly declare tests were not run."""
    run_dir = tmp_path / "run"
    capsules_dir = run_dir / "capsules"
    capsules_dir.mkdir(parents=True)

    static_capsule = {
        "schema_version": "2.0.0",
        "capsule_id": "capsule-test-static-appdirs",
        "generated_at": "2026-11-03T00:00:00Z",
        "capsule_type": "no_action",
        "action": "no_action",
        "action_reason": "healthy and current",
        "status": "no_action",
        "status_reason": "healthy_no_action",
        "target_repo": {
            "name": "sample_repo",
            "url": "https://github.com/example/sample_repo",
            "commit_sha": "abc1234",
            "python_version": "3.12"
        },
        "dependency": {
            "name": "appdirs",
            "declared_specifier": "==1.4.4",
            "declared_in": ["requirements.txt"]
        },
        "observed": {
            "risk_indicators": [],
            "scan": {"files_scanned": 1, "dynamic_imports": []},
            "usage_locations": [],
            "test_results": {
                "baseline": {"passed": 0, "failed": 0, "junit_path": "n/a"},
                "candidate": {"passed": 0, "failed": 0, "junit_path": "n/a"},
                "new_failures": [],
                "pip_check": {"baseline": "Tests not run in static analyze mode.", "candidate": "Tests not run in static analyze mode."}
            },
            "evidence": [{"path": "D:\\Agent\\dependency-exit-capsule\\assets\\test.json", "sha256": "1234567890abcdef", "command": "run", "exit_code": 0, "captured_at": "2026-11-03"}]
        },
        "ai_generated": {
            "proposed_replacement": {"name": "no_model_call", "type": "stdlib"},
            "migration_steps": [],
            "suggested_tests": [],
            "gap_analysis": [],
            "provenance": {"provider": "rule_based", "model_id": "none"}
        },
        "limitations": []
    }

    cap_file = capsules_dir / "capsule-test-static-appdirs.json"
    cap_file.write_text(json.dumps(static_capsule, indent=2), encoding="utf-8")

    res = export_capsule(cap_file, run_dir)
    pr_desc_p = run_dir / res["files"][1]
    patch_p = run_dir / res["files"][0]

    pr_text = pr_desc_p.read_text(encoding="utf-8")
    patch_text = patch_p.read_text(encoding="utf-8")

    # Static run states tests were not run
    assert "tests were not run" in pr_text.lower() or "tests were not executed" in pr_text.lower()
    assert "static run mode: tests were not executed" in patch_text.lower() or "no patch generated" in patch_text.lower()

    # No local absolute drive paths in PR description
    assert "D:\\Agent" not in pr_text
    assert "C:\\Users" not in pr_text
    assert "D:/Agent" not in pr_text


def test_equivalence_probe_detects_difference(tmp_path):
    """
    Test that behavior equivalence checks flag a known difference (e.g. str vs Path),
    downgrading status to unverified with status_reason 'behavior_differs'.
    """
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    py_file = repo_dir / "caller.py"
    # Call with a literal argument
    py_file.write_text("import testlib\nval = testlib.get_path('sample_data')\n", encoding="utf-8")

    capsule = {
        "schema_version": "2.0.0",
        "capsule_id": "capsule-testlib-diff",
        "capsule_type": "replace",
        "action": "replace",
        "status": "verified",
        "status_reason": "tests_passed_clean",
        "dependency": {"name": "testlib", "declared_specifier": "==1.0", "declared_in": ["requirements.txt"]},
        "observed": {
            "usage_locations": [{"file": "caller.py", "line": 2, "symbol": "get_path", "kind": "call", "covered_by_tests": True}],
            "test_results": {"baseline": {"passed": 1, "failed": 0}, "candidate": {"passed": 1, "failed": 0}, "new_failures": [], "pip_check": {"baseline": "clean", "candidate": "clean"}}
        },
        "ai_generated": {
            "proposed_replacement": {"name": "newlib", "type": "pypi"}
        }
    }

    # Inject a differing probe result
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()

    # Run check with probe returning diff
    from scripts.equivalence_check import perform_capsule_equivalence_checks
    
    # Patch run_probe_for_call to simulate type difference (e.g. str vs Path)
    import scripts.equivalence_check as eq_mod
    orig_probe = eq_mod.run_probe_for_call

    def mock_probe_diff(dep, repl, sym, args, r_dir, py_exe):
        return {
            "old_result": {"type": "str", "repr": "'/path/sample_data'", "json_normalized": "/path/sample_data"},
            "new_result": {"type": "PosixPath", "repr": "PosixPath('/path/sample_data')", "json_normalized": "/path/sample_data"},
            "equal": False,
            "notes": "Behavior differs: type mismatch: old=str vs new=PosixPath",
            "old_error": None,
            "new_error": None
        }

    eq_mod.run_probe_for_call = mock_probe_diff
    try:
        up_c, passed = perform_capsule_equivalence_checks(capsule, repo_dir, evidence_dir)
        assert passed is False
        assert up_c["status"] == "unverified"
        assert up_c["status_reason"] == "behavior_differs"
        checks = up_c["observed"]["equivalence_checks"]
        assert len(checks) == 1
        assert checks[0]["equal"] is False
        assert "type mismatch" in checks[0]["notes"]
    finally:
        eq_mod.run_probe_for_call = orig_probe


def test_equivalence_probe_equivalent(tmp_path):
    """
    Test that identical probe outputs keep status verified and record equal=True.
    """
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    py_file = repo_dir / "caller.py"
    py_file.write_text("import testlib\nval = testlib.get_path('sample_data')\n", encoding="utf-8")

    capsule = {
        "schema_version": "2.0.0",
        "capsule_id": "capsule-testlib-same",
        "capsule_type": "replace",
        "action": "replace",
        "status": "verified",
        "status_reason": "tests_passed_clean",
        "dependency": {"name": "testlib", "declared_specifier": "==1.0", "declared_in": ["requirements.txt"]},
        "observed": {
            "usage_locations": [{"file": "caller.py", "line": 2, "symbol": "get_path", "kind": "call", "covered_by_tests": True}],
            "test_results": {"baseline": {"passed": 1, "failed": 0}, "candidate": {"passed": 1, "failed": 0}, "new_failures": [], "pip_check": {"baseline": "clean", "candidate": "clean"}}
        },
        "ai_generated": {
            "proposed_replacement": {"name": "newlib", "type": "pypi"}
        }
    }

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()

    import scripts.equivalence_check as eq_mod
    orig_probe = eq_mod.run_probe_for_call

    def mock_probe_same(dep, repl, sym, args, r_dir, py_exe):
        return {
            "old_result": {"type": "str", "repr": "'output_data'", "json_normalized": "output_data"},
            "new_result": {"type": "str", "repr": "'output_data'", "json_normalized": "output_data"},
            "equal": True,
            "notes": "Outputs identical (type: str)",
            "old_error": None,
            "new_error": None
        }

    eq_mod.run_probe_for_call = mock_probe_same
    try:
        up_c, passed = perform_capsule_equivalence_checks(capsule, repo_dir, evidence_dir)
        assert passed is True
        assert up_c["status"] == "verified"
        assert up_c["status_reason"] == "tests_passed_clean"
        checks = up_c["observed"]["equivalence_checks"]
        assert len(checks) == 1
        assert checks[0]["equal"] is True
    finally:
        eq_mod.run_probe_for_call = orig_probe

