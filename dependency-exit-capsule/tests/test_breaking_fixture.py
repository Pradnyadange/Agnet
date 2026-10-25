"""
Negative-control test: sample_repo_breaking fixture.

The fixture repo uses ``toml.load(path)`` where the file is opened with
``open(path, "r")`` (text mode).  The stubbed model proposes replacing
``toml`` with ``tomllib`` (Python 3.11+ stdlib) and edits the import line.

``tomllib.load()`` requires a **binary-mode** file object, so the patched
code raises ``TypeError`` when the test calls ``load_config``, which causes
the test to fail.

Assertions:
  - baseline passes the fixture test
  - candidate fails the fixture test after the patch is applied
  - ``new_failures`` contains ``test_load_config_reads_toml_file``
  - ``determine_status()`` returns ``"failed"``
  - a capsule dict with ``status="failed"`` and ``run_label="fixture demo"``
    is produced

No real model call is made; the proposal is injected directly.
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Project-root on sys.path so that scripts/ and viewer/ are importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_diff_tests import apply_candidate_patch, run_in_repo, parse_junit_xml
from scripts.build_capsule import determine_status
from scripts.common import get_utc_iso_timestamp

BREAKING_REPO = PROJECT_ROOT / "tests" / "fixtures" / "sample_repo_breaking"

# ---------------------------------------------------------------------------
# The stubbed model proposal:
# Replace "import toml" with "import tomllib as toml"  (the standard-library
# tomllib requires binary-mode file objects, but the test opens in text mode)
# ---------------------------------------------------------------------------
STUBBED_PROPOSAL = {
    "proposed_replacement": {"name": "tomllib", "type": "stdlib"},
    "migration_steps": [
        "Replace `import toml` with `import tomllib as toml`.",
        "Open files in binary mode: `open(path, 'rb')` instead of `open(path, 'r')`.",
    ],
    "suggested_tests": ["test_load_config_reads_toml_file"],
    "gap_analysis": [
        "tomllib.load() requires a binary-mode file object; text-mode usage will raise TypeError."
    ],
    "structured_edits": [
        {
            "file": "breaking_pkg/loader.py",
            "old_text": "import toml",
            "new_text": "import tomllib as toml",
        }
        # Intentionally NOT fixing the open() call to text mode → test must break
    ],
    "provenance": {
        "provider": "rule_based_knowledge_base",
        "model_id": "stubbed_for_test",
        "model_license_name": "N/A",
        "model_card_url": "N/A",
        "prompt_sha256": "N/A",
        "raw_response_path": "N/A",
        "secret_redactions_count": 0,
        "trust_check": {"skipped": True, "needs_human_review": False},
        "validation": {
            "passed": True,
            "api_coverage": 1.0,
            "rejected_candidates": [],
        },
    },
}


# ---------------------------------------------------------------------------
# Helper: build a minimal but valid capsule dict from diff results
# ---------------------------------------------------------------------------
def build_test_capsule(
    dep: str,
    repo_name: str,
    baseline_res: dict,
    candidate_res: dict,
    new_failures: list[str],
    status: str,
    run_label: str,
) -> dict:
    base_j = baseline_res["junit_summary"]
    cand_j = candidate_res["junit_summary"]
    pip_ok = candidate_res["pip_exit_code"] == 0

    return {
        "schema_version": "2.0.0",
        "capsule_id": f"capsule-{repo_name}-{dep}-fixture-demo",
        "generated_at": get_utc_iso_timestamp(),
        "capsule_type": "replacement",
        "run_label": run_label,
        "target_repo": {
            "name": repo_name,
            "url": "file://fixture",
            "commit_sha": "n/a",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        "maintenance_problem": "toml is unmaintained; stdlib tomllib is the successor.",
        "dependency": {
            "name": dep,
            "declared_specifier": "toml",
            "declared_in": ["requirements.txt"],
        },
        "observed": {
            "risk_indicators": [],
            "scan": {"files_scanned": 1, "dynamic_imports": []},
            "usage_locations": [
                {
                    "file": "breaking_pkg/loader.py",
                    "line": 1,
                    "symbol": "load",
                    "kind": "call",
                    "covered_by_tests": True,
                }
            ],
            "test_results": {
                "baseline": {
                    "passed": base_j["passed"],
                    "failed": base_j["failed"],
                    "junit_path": baseline_res["junit_path"],
                },
                "candidate": {
                    "passed": cand_j["passed"],
                    "failed": cand_j["failed"],
                    "junit_path": candidate_res["junit_path"],
                },
                "new_failures": new_failures,
                "pip_check": {
                    "baseline": baseline_res["pip_check"],
                    "candidate": candidate_res["pip_check"],
                },
            },
            "evidence": [],
            "trust_check": {"skipped": True, "needs_human_review": False},
            "secret_redactions_count": 0,
        },
        "ai_generated": {
            "proposed_replacement": STUBBED_PROPOSAL["proposed_replacement"],
            "migration_steps": STUBBED_PROPOSAL["migration_steps"],
            "suggested_tests": STUBBED_PROPOSAL["suggested_tests"],
            "gap_analysis": STUBBED_PROPOSAL["gap_analysis"],
            "provenance": STUBBED_PROPOSAL["provenance"],
        },
        "status": status,
        "limitations": [
            "Fixture demo only; no real model call was made.",
            "This capsule is intentionally 'failed' to validate the negative control.",
        ],
    }


# ---------------------------------------------------------------------------
# Main test
# ---------------------------------------------------------------------------
def test_breaking_fixture_pipeline_produces_failed_capsule(tmp_path):
    """
    Run the breaking fixture through the diff-test pipeline with a stubbed
    model that proposes tomllib as toml (without fixing the open() call).

    Expected outcome:
    - Baseline: test passes (toml handles text-mode fine)
    - Candidate: test fails (tomllib requires binary mode)
    - new_failures == ['tests/test_loader.py::test_load_config_reads_toml_file'] or similar
    - determine_status() == 'failed'
    - Capsule dict has status == 'failed' and run_label == 'fixture demo'
    """
    assert BREAKING_REPO.is_dir(), f"Fixture not found: {BREAKING_REPO}"

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()

    repo_a = tmp_path / "env_a_baseline"
    repo_b = tmp_path / "env_b_candidate"

    # Copy fixture repo to both environments
    shutil.copytree(
        BREAKING_REPO,
        repo_a,
        ignore=shutil.ignore_patterns(".git", ".venv", "venv", "__pycache__"),
    )
    shutil.copytree(
        BREAKING_REPO,
        repo_b,
        ignore=shutil.ignore_patterns(".git", ".venv", "venv", "__pycache__"),
    )

    # --- Baseline run (must pass) ---
    baseline_res = run_in_repo(repo_a, evidence_dir, "baseline")
    base_j = baseline_res["junit_summary"]

    assert base_j["passed"] >= 1, (
        f"Baseline should pass at least 1 test but got: passed={base_j['passed']}, "
        f"failed={base_j['failed']}.  pytest output:\n"
        + (evidence_dir / "baseline_pytest_output.txt").read_text(encoding="utf-8", errors="replace")
    )
    assert base_j["failed"] == 0, (
        f"Baseline should have 0 failures but got {base_j['failed']}."
    )

    # --- Apply breaking patch (import line only, NOT the open() call) ---
    ok, msg = apply_candidate_patch(
        repo_b,
        STUBBED_PROPOSAL,
        "toml",
        allowed_files={"breaking_pkg/loader.py"},
    )
    assert ok is True, f"apply_candidate_patch failed unexpectedly: {msg}"

    # Verify the patch was applied
    patched = (repo_b / "breaking_pkg" / "loader.py").read_text(encoding="utf-8")
    assert "import tomllib as toml" in patched, "Patch not applied to loader.py"
    # The open() call still uses text mode → tomllib will raise TypeError at runtime
    assert 'open(path, "r"' in patched, (
        "Expected the text-mode open() to remain in the patched file so the test breaks."
    )

    # --- Candidate run (must fail) ---
    candidate_res = run_in_repo(repo_b, evidence_dir, "candidate")
    cand_j = candidate_res["junit_summary"]

    # Identify new failures (tests that were passing before but fail now)
    baseline_tc = base_j["test_cases"]
    candidate_tc = cand_j["test_cases"]
    new_failures = [
        name
        for name, status in candidate_tc.items()
        if status in ("failed", "error")
        and baseline_tc.get(name) not in ("failed", "error")
    ]

    assert len(new_failures) >= 1, (
        f"Expected at least 1 new failure after applying the breaking patch, got 0.\n"
        f"candidate test_cases: {candidate_tc}\n"
        f"candidate pytest output:\n"
        + (evidence_dir / "candidate_pytest_output.txt").read_text(encoding="utf-8", errors="replace")
    )

    # The specific test that should break is test_load_config_reads_toml_file
    assert any(
        "test_load_config_reads_toml_file" in f for f in new_failures
    ), (
        f"Expected 'test_load_config_reads_toml_file' in new_failures, got: {new_failures}"
    )

    # --- determine_status must return 'failed' ---
    pip_clean = candidate_res["pip_exit_code"] == 0
    usage_locations = [
        {
            "file": "breaking_pkg/loader.py",
            "line": 1,
            "symbol": "load",
            "kind": "call",
            "covered_by_tests": True,
        }
    ]
    status = determine_status(
        baseline_passed=base_j["passed"],
        candidate_passed=cand_j["passed"],
        new_failures=new_failures,
        pip_check_clean=pip_clean,
        usage_locations=usage_locations,
        api_coverage=1.0,
    )
    assert status == "failed", (
        f"Expected status='failed' but got '{status}'.  "
        f"new_failures={new_failures}, pip_clean={pip_clean}"
    )

    # --- Build capsule dict and verify run_label and status ---
    capsule = build_test_capsule(
        dep="toml",
        repo_name="sample_repo_breaking",
        baseline_res=baseline_res,
        candidate_res=candidate_res,
        new_failures=new_failures,
        status=status,
        run_label="fixture demo",
    )

    assert capsule["status"] == "failed"
    assert capsule["run_label"] == "fixture demo"

    # Verify new_failures is recorded in the capsule
    capsule_failures = capsule["observed"]["test_results"]["new_failures"]
    assert any(
        "test_load_config_reads_toml_file" in f for f in capsule_failures
    ), f"Capsule new_failures missing expected test name: {capsule_failures}"

    # Sanity: capsule serialises to JSON without error
    capsule_json = json.dumps(capsule, indent=2)
    round_trip = json.loads(capsule_json)
    assert round_trip["status"] == "failed"
    assert round_trip["run_label"] == "fixture demo"


# ---------------------------------------------------------------------------
# Additional unit test: count_capsule_statuses handles 'fixture demo' capsule
# ---------------------------------------------------------------------------
def test_count_capsule_statuses_includes_failed_fixture():
    """
    Verifies that count_capsule_statuses counts a fixture-demo capsule with
    status='failed' correctly.  This exercises the viewer counting logic with
    a real 'failed' capsule alongside the other five statuses.
    """
    from viewer.data import count_capsule_statuses

    capsules = [
        {"capsule_id": "c1", "status": "verified", "run_label": "linkwatch"},
        {"capsule_id": "c2", "status": "unverified", "run_label": "linkwatch"},
        {"capsule_id": "c3", "status": "not_run", "run_label": "linkwatch"},
        {"capsule_id": "c4", "status": "not_testable", "run_label": "linkwatch"},
        {"capsule_id": "c5", "status": "no_valid_proposal", "run_label": "linkwatch"},
        {"capsule_id": "c6", "status": "failed", "run_label": "fixture demo"},
    ]

    counts = count_capsule_statuses(capsules)

    # All six statuses present
    assert counts["verified"] == 1
    assert counts["unverified"] == 1
    assert counts["not_run"] == 1
    assert counts["not_testable"] == 1
    assert counts["no_valid_proposal"] == 1
    assert counts["failed"] == 1

    # Sum == len(capsules)
    assert sum(counts.values()) == len(capsules)
