"""Patch test_pipeline.py to handle determine_status returning a tuple."""
from pathlib import Path

f = Path("tests/test_pipeline.py")
content = f.read_text(encoding="utf-8")

OLD_FN = '''\
def test_status_determination_rules():
    # Verified case: clean pip, all covered, api_cov=1.0, baseline and cand pass
    status_ver = determine_status(
        baseline_passed=5,
        candidate_passed=5,
        new_failures=[],
        pip_check_clean=True,
        usage_locations=[{"file": "a.py", "line": 10, "kind": "call", "covered_by_tests": True}],
        api_coverage=1.0
    )
    assert status_ver == "verified"

    # Unverified case: call site not covered
    status_unv = determine_status(
        baseline_passed=5,
        candidate_passed=5,
        new_failures=[],
        pip_check_clean=True,
        usage_locations=[{"file": "a.py", "line": 10, "kind": "call", "covered_by_tests": False}],
        api_coverage=1.0
    )
    assert status_unv == "unverified"

    # Failed case: new failures present
    status_fail = determine_status(
        baseline_passed=5,
        candidate_passed=4,
        new_failures=["test_something_broke"],
        pip_check_clean=True,
        usage_locations=[{"file": "a.py", "line": 10, "kind": "call", "covered_by_tests": True}],
        api_coverage=1.0
    )
    assert status_fail == "failed"

    # not_run case: user did not opt in
    status_nr = determine_status(
        baseline_passed=0,
        candidate_passed=0,
        new_failures=[],
        pip_check_clean=True,
        usage_locations=[{"file": "a.py", "line": 10, "kind": "call", "covered_by_tests": False}],
        api_coverage=1.0,
        opted_in_tests=False
    )
    assert status_nr == "not_run"

    # no_valid_proposal case
    status_nvp = determine_status(
        baseline_passed=5,
        candidate_passed=5,
        new_failures=[],
        pip_check_clean=True,
        usage_locations=[{"file": "a.py", "line": 10, "kind": "call", "covered_by_tests": True}],
        api_coverage=1.0,
        proposal_valid=False
    )
    assert status_nvp == "no_valid_proposal"

    # unused_dependency: stays unverified without passed candidate tests, verified when passed
    status_unused_unv = determine_status(
        baseline_passed=0,
        candidate_passed=0,
        new_failures=[],
        pip_check_clean=True,
        usage_locations=[],
        api_coverage=1.0,
        is_unused_dep=True
    )
    assert status_unused_unv == "not_testable"

    status_unused_ver = determine_status(
        baseline_passed=5,
        candidate_passed=5,
        new_failures=[],
        pip_check_clean=True,
        usage_locations=[],
        api_coverage=1.0,
        is_unused_dep=True
    )
    assert status_unused_ver == "verified"
'''

NEW_FN = '''\
def test_status_determination_rules():
    """determine_status returns (status, status_reason); test every branch."""

    # --- Tested runs (tests_executed=True, the default) ---

    # Verified: clean pip, all covered, api_cov=1.0, baseline and candidate pass
    status, reason = determine_status(
        baseline_passed=5, candidate_passed=5, new_failures=[],
        pip_check_clean=True,
        usage_locations=[{"file": "a.py", "line": 10, "kind": "call", "covered_by_tests": True}],
        api_coverage=1.0,
    )
    assert status == "verified", f"expected verified, got {status}"
    assert reason == "tests_passed_clean"

    # Unverified: call site not covered
    status, reason = determine_status(
        baseline_passed=5, candidate_passed=5, new_failures=[],
        pip_check_clean=True,
        usage_locations=[{"file": "a.py", "line": 10, "kind": "call", "covered_by_tests": False}],
        api_coverage=1.0,
    )
    assert status == "unverified", f"expected unverified, got {status}"
    assert reason == "partial_test_coverage"

    # Failed: new failures present
    status, reason = determine_status(
        baseline_passed=5, candidate_passed=4, new_failures=["test_something_broke"],
        pip_check_clean=True,
        usage_locations=[{"file": "a.py", "line": 10, "kind": "call", "covered_by_tests": True}],
        api_coverage=1.0,
    )
    assert status == "failed", f"expected failed, got {status}"
    assert reason == "new_test_failures"

    # not_run: user did not opt in
    status, reason = determine_status(
        baseline_passed=0, candidate_passed=0, new_failures=[],
        pip_check_clean=True,
        usage_locations=[{"file": "a.py", "line": 10, "kind": "call", "covered_by_tests": False}],
        api_coverage=1.0, opted_in_tests=False,
    )
    assert status == "not_run", f"expected not_run, got {status}"
    assert reason == "tests_not_executed"

    # no_valid_proposal
    status, reason = determine_status(
        baseline_passed=5, candidate_passed=5, new_failures=[],
        pip_check_clean=True,
        usage_locations=[{"file": "a.py", "line": 10, "kind": "call", "covered_by_tests": True}],
        api_coverage=1.0, proposal_valid=False,
    )
    assert status == "no_valid_proposal", f"expected no_valid_proposal, got {status}"
    assert reason == "gate_rejected"

    # not_testable: no tests exist and is_unused_dep with 0 pass counts
    status, reason = determine_status(
        baseline_passed=0, candidate_passed=0, new_failures=[],
        pip_check_clean=True, usage_locations=[], api_coverage=1.0, is_unused_dep=True,
    )
    assert status == "not_testable", f"expected not_testable, got {status}"

    # verified for unused_dep when tests pass
    status, reason = determine_status(
        baseline_passed=5, candidate_passed=5, new_failures=[],
        pip_check_clean=True, usage_locations=[], api_coverage=1.0, is_unused_dep=True,
    )
    assert status == "verified", f"expected verified, got {status}"

    # --- Static runs (tests_executed=False) ---

    # Static + valid proposal for replace action -> not_run
    status, reason = determine_status(
        baseline_passed=0, candidate_passed=0, new_failures=[],
        pip_check_clean=True,
        usage_locations=[{"file": "a.py", "line": 10, "kind": "call", "covered_by_tests": False}],
        api_coverage=1.0, proposal_valid=True, tests_executed=False, action="replace",
    )
    assert status == "not_run", f"static replace -> expected not_run, got {status}"
    assert reason == "tests_not_executed"

    # Static + gate rejected -> no_valid_proposal
    status, reason = determine_status(
        baseline_passed=0, candidate_passed=0, new_failures=[],
        pip_check_clean=True, usage_locations=[], api_coverage=0.0,
        proposal_valid=False, tests_executed=False, action="replace",
    )
    assert status == "no_valid_proposal", f"static gate-rejected -> expected no_valid_proposal, got {status}"
    assert reason == "gate_rejected"

    # Static + no_action -> no_action
    status, reason = determine_status(
        baseline_passed=0, candidate_passed=0, new_failures=[],
        pip_check_clean=True, usage_locations=[], api_coverage=1.0,
        tests_executed=False, action="no_action",
    )
    assert status == "no_action", f"static no_action -> expected no_action, got {status}"

    # Static + remove -> no_action (reason: no_usage_found)
    status, reason = determine_status(
        baseline_passed=0, candidate_passed=0, new_failures=[],
        pip_check_clean=True, usage_locations=[], api_coverage=1.0,
        tests_executed=False, action="remove",
    )
    assert status == "no_action", f"static remove -> expected no_action, got {status}"
    assert reason == "no_usage_found"


def test_count_capsule_statuses_all_six():
    """count_capsule_statuses must tally one capsule of each known status; sum == len(capsules)."""
    from viewer.data import count_capsule_statuses

    capsules = [
        {"capsule_id": "c1", "status": "verified"},
        {"capsule_id": "c2", "status": "unverified"},
        {"capsule_id": "c3", "status": "not_run"},
        {"capsule_id": "c4", "status": "not_testable"},
        {"capsule_id": "c5", "status": "no_valid_proposal"},
        {"capsule_id": "c6", "status": "failed"},
        {"capsule_id": "c7", "status": "no_action"},       # static-run status
        {"capsule_id": "c8", "status": "totally_unknown"}, # must go to 'other', not lost
    ]
    counts = count_capsule_statuses(capsules)

    assert counts["verified"] == 1
    assert counts["unverified"] == 1
    assert counts["not_run"] == 1
    assert counts["not_testable"] == 1
    assert counts["no_valid_proposal"] == 1
    assert counts["failed"] == 1
    assert counts["no_action"] == 1
    assert counts["other"] == 1

    total = sum(counts.values())
    assert total == len(capsules), f"counts should sum to {len(capsules)}, got {total}"

'''

if OLD_FN not in content:
    print("ERROR: old function text not found in file!")
    import sys; sys.exit(1)

new_content = content.replace(OLD_FN, NEW_FN, 1)
f.write_text(new_content, encoding="utf-8")
print("Patched successfully")
