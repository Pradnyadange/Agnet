import json
import sys
from pathlib import Path
import pytest
import jsonschema

from scripts.common import compute_sha256_file, compute_sha256_text
from scripts.map_usage import map_repo_usage
from scripts.scan_risk import parse_requirements_file, parse_pyproject
from scripts.propose_replacement import run_validation_gate, load_rule_based_fallback
from scripts.run_diff_tests import parse_junit_xml
from scripts.build_capsule import determine_status
from scripts.verify_capsule import verify_manifest

SAMPLE_REPO_DIR = Path("tests/fixtures/sample_repo")
REFERENCES_DIR = Path("references")
SCHEMA_PATH = REFERENCES_DIR / "capsule-schema.json"

def test_requirements_and_pyproject_parsing():
    reqs = parse_requirements_file(SAMPLE_REPO_DIR / "requirements.txt")
    assert "toml" in reqs
    assert "appdirs" in reqs

    pyproj = parse_pyproject(SAMPLE_REPO_DIR / "pyproject.toml")
    assert "toml" in pyproj
    assert "appdirs" in pyproj

def test_ast_usage_mapping():
    usage = map_repo_usage(SAMPLE_REPO_DIR, "toml")
    assert usage["files_scanned"] == 2
    assert len(usage["usage_locations"]) >= 1
    # Check that call to loads was captured
    call_sites = [u for u in usage["usage_locations"] if u["kind"] == "call"]
    assert any(c["symbol"] == "loads" for c in call_sites)

def test_validation_gate_stdlib():
    proposal = {
        "proposed_replacement": {"name": "tomllib", "type": "stdlib"}
    }
    is_valid, cov, rejected, reason = run_validation_gate(proposal, ["loads"], "3.14.6")
    assert is_valid is True
    assert cov == 1.0

def test_validation_gate_invalid_candidate():
    proposal = {
        "proposed_replacement": {"name": "non_existent_fake_lib_12345", "type": "pypi"}
    }
    is_valid, cov, rejected, reason = run_validation_gate(proposal, ["do_something"], "3.14.6")
    assert is_valid is False
    assert len(rejected) > 0

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

def test_placeholder_sha_refusal():
    import subprocess
    res = subprocess.run(
        [sys.executable, "scripts/build_capsule.py", "--dep", "toml", "--commit-sha", "a1b2c3d4e5f678901234567890abcdef12345678"],
        capture_output=True,
        text=True
    )
    assert res.returncode != 0
    assert "placeholder" in res.stderr.lower() or "refusal" in res.stderr.lower()

def test_structured_patching_and_boundary_checks(tmp_path):
    from scripts.run_diff_tests import apply_candidate_patch
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    py_file = repo_dir / "main.py"
    py_file.write_text("import old_pkg\nprint('hello')\n", encoding="utf-8")
    
    proposal = {
        "proposed_replacement": {"name": "new_pkg", "type": "stdlib"},
        "structured_edits": [
            {
                "file": "main.py",
                "old_text": "import old_pkg",
                "new_text": "import new_pkg as old_pkg"
            }
        ]
    }
    
    # Boundary check passes when file is in allowed_files
    ok, msg = apply_candidate_patch(repo_dir, proposal, "old_pkg", allowed_files={"main.py"})
    assert ok is True
    assert "import new_pkg as old_pkg" in py_file.read_text(encoding="utf-8")

    # Boundary check fails when edit touches an unobserved file
    proposal_unobserved = {
        "proposed_replacement": {"name": "new_pkg", "type": "stdlib"},
        "structured_edits": [
            {
                "file": "main.py",
                "old_text": "import new_pkg as old_pkg",
                "new_text": "import rogue_pkg"
            }
        ]
    }
    ok_b, msg_b = apply_candidate_patch(repo_dir, proposal_unobserved, "old_pkg", allowed_files={"other.py"})
    assert ok_b is False
    assert "boundary" in msg_b.lower()

def test_banned_literals_in_scripts():
    import re
    # Scan all .py files in scripts/ (excluding tests and references)
    scripts_dir = Path("scripts")
    # Package names (hardcoded branches), model names, and claims
    banned_tokens = [
        "qwen", "llama", "gemma", "production tested", "zero outbound", "guaranteed",
        "appdirs", "platformdirs"
    ]
    # Allowlist: tomllib is python 3.11+ standard library module, pyproject.toml is manifest filename
    allowlist = {"tomllib", "pyproject.toml", "top_level.txt"}
    
    violations = []
    for py_file in scripts_dir.glob("*.py"):
        content = py_file.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(content.splitlines(), start=1):
            line_lower = line.lower()
            for token in banned_tokens:
                # Whole-token regex pattern
                pattern = rf"\b{re.escape(token)}\b"
                if re.search(pattern, line_lower):
                    # Check if line contains an allowlisted token that explains the match
                    is_allowed = any(al in line_lower for al in allowlist if token in al)
                    if not is_allowed:
                        violations.append(f"{py_file.name}:{line_no} contains banned token '{token}': {line.strip()}")
                    
    assert len(violations) == 0, "\n".join(violations)

def test_capsule_schema_validation():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    capsules = list(Path("assets/capsules").glob("*.json"))
    assert len(capsules) > 0
    for c_path in capsules:
        capsule_data = json.loads(c_path.read_text(encoding="utf-8"))
        jsonschema.validate(instance=capsule_data, schema=schema)

def test_integrity_manifest_tampering(tmp_path):
    dummy_file = tmp_path / "evidence.txt"
    dummy_file.write_text("clean evidence", encoding="utf-8")
    real_hash = compute_sha256_file(dummy_file)

    manifest_file = tmp_path / "manifest.json"
    manifest_data = {
        "files": {str(dummy_file): real_hash}
    }
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    ok, checks = verify_manifest(manifest_file)
    assert ok is True

    dummy_file.write_text("tampered evidence!", encoding="utf-8")
    ok_tampered, checks_tampered = verify_manifest(manifest_file)
    assert ok_tampered is False
    assert checks_tampered[0]["match"] is False


def test_api_coverage_rejection_when_symbol_missing():
    # If candidate lacks a used symbol, validation gate must return False and reject
    proposal = {
        "proposed_replacement": {"name": "math", "type": "stdlib"}
    }
    # 'non_existent_symbol_in_math' is not in math
    is_valid, cov, rejected, reason = run_validation_gate(proposal, ["non_existent_symbol_in_math"], "3.14.6")
    assert is_valid is False
    assert cov == 0.0
    assert len(rejected) > 0
    assert "missing symbols" in rejected[0]

def test_fetch_license_stubbed_and_unknown(monkeypatch):
    from scripts.llm_client import LLMClient
    
    # 1. Successful Ollama response
    class FakeResponse:
        status_code = 200
        def json(self):
            return {"license": "MIT License\n\nPermission is hereby granted..."}
            
    monkeypatch.setattr("requests.post", lambda url, json, timeout: FakeResponse())
    client = LLMClient(provider="ollama", model_id="dummy-model:latest")
    assert "MIT License" in client.license_text
    assert client.license_sha256 != "unknown"
    assert len(client.license_sha256) == 64

    # 2. Unknown fallback
    class ErrorResponse:
        status_code = 404
        def json(self):
            return {}
            
    monkeypatch.setattr("requests.post", lambda url, json, timeout: ErrorResponse())
    client_err = LLMClient(provider="ollama", model_id="unknown-model:latest")
    assert "unknown, see model_card_url" in client_err.license_text
    assert client_err.license_sha256 == "unknown"

def test_propose_replacement_cli_guards():
    import subprocess
    # 1. Missing --model-id when not offline
    res_missing_model = subprocess.run(
        [sys.executable, "scripts/propose_replacement.py", "--dep", "toml", "--usage-file", "assets/usage_toml.json", "--out", "temp.json"],
        capture_output=True,
        text=True
    )
    assert res_missing_model.returncode != 0
    assert "--model-id is required" in res_missing_model.stderr

    # 2. --offline guard succeeds without --model-id
    res_offline = subprocess.run(
        [sys.executable, "scripts/propose_replacement.py", "--dep", "toml", "--usage-file", "assets/usage_toml.json", "--offline", "--out", "assets/proposal_toml.json"],
        capture_output=True,
        text=True
    )
    assert res_offline.returncode == 0

def test_null_commit_sha_for_fixture(tmp_path):
    # build_capsule with commit_sha="" should record "n/a" and not fail
    import subprocess
    out_dir = tmp_path / "capsules"
    out_dir.mkdir()
    res = subprocess.run(
        [
            sys.executable, "scripts/build_capsule.py",
            "--dep", "toml",
            "--scan-file", "assets/scan.json",
            "--usage-file", "assets/usage_toml.json",
            "--proposal-file", "assets/proposal_toml.json",
            "--diff-file", "assets/diff_toml.json",
            "--out", str(out_dir),
            "--commit-sha", ""
        ],
        capture_output=True,
        text=True
    )
    assert res.returncode == 0
    created_capsules = list(out_dir.glob("*.json"))
    assert len(created_capsules) == 1
    cap_json = json.loads(created_capsules[0].read_text(encoding="utf-8"))
    assert cap_json["target_repo"]["commit_sha"] == "n/a"

def test_end_to_end_sample_repo_with_stubbed_model(tmp_path, monkeypatch):
    from scripts.run_diff_tests import apply_candidate_patch
    # Verify that model structured edits reach and patch sample repo correctly
    sample_copy = tmp_path / "sample_copy"
    import shutil
    shutil.copytree(SAMPLE_REPO_DIR, sample_copy)
    
    stubbed_proposal = {
        "proposed_replacement": {"name": "tomllib", "type": "stdlib"},
        "structured_edits": [
            {
                "file": "sample_pkg/core.py",
                "old_text": "import toml",
                "new_text": "import tomllib as toml"
            }
        ]
    }
    
    ok, msg = apply_candidate_patch(sample_copy, stubbed_proposal, "toml", allowed_files={"sample_pkg/core.py"})
    assert ok is True
    patched_content = (sample_copy / "sample_pkg" / "core.py").read_text(encoding="utf-8")
    assert "import tomllib as toml" in patched_content


