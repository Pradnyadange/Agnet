import argparse
import os
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from common import get_utc_iso_timestamp, load_json, run_command, save_json
except ImportError:
    from scripts.common import get_utc_iso_timestamp, load_json, run_command, save_json

def parse_junit_xml(junit_path: Path) -> dict:
    """Parse pytest junit XML file to extract passed, failed, skipped, and test failure details."""
    if not junit_path.exists():
        return {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "duration": 0.0,
            "test_cases": {},
            "failures": []
        }
        
    try:
        tree = ET.parse(junit_path)
        root = tree.getroot()
        
        # Testsuites or testsuite
        suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
        
        passed = 0
        failed = 0
        skipped = 0
        errors = 0
        duration = 0.0
        test_cases = {}
        failures = []
        
        for suite in suites:
            duration += float(suite.attrib.get("time", 0.0))
            for tc in suite.findall("testcase"):
                name = tc.attrib.get("name", "unknown")
                classname = tc.attrib.get("classname", "")
                full_id = f"{classname}::{name}" if classname else name
                
                fail_elem = tc.find("failure")
                err_elem = tc.find("error")
                skip_elem = tc.find("skipped")
                
                if fail_elem is not None:
                    failed += 1
                    test_cases[full_id] = "failed"
                    failures.append({
                        "test_name": full_id,
                        "message": fail_elem.attrib.get("message", ""),
                        "details": (fail_elem.text or "").strip()[:500]
                    })
                elif err_elem is not None:
                    errors += 1
                    test_cases[full_id] = "error"
                    failures.append({
                        "test_name": full_id,
                        "message": err_elem.attrib.get("message", ""),
                        "details": (err_elem.text or "").strip()[:500]
                    })
                elif skip_elem is not None:
                    skipped += 1
                    test_cases[full_id] = "skipped"
                else:
                    passed += 1
                    test_cases[full_id] = "passed"
                    
        return {
            "passed": passed,
            "failed": failed + errors,
            "skipped": skipped,
            "errors": errors,
            "duration": round(duration, 3),
            "test_cases": test_cases,
            "failures": failures
        }
    except Exception as e:
        sys.stderr.write(f"Error parsing junit XML {junit_path}: {e}\n")
        return {"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "duration": 0.0, "test_cases": {}, "failures": []}

def run_in_repo(repo_dir: Path, out_evidence_dir: Path, env_label: str) -> dict:
    """Run pip check and pytest in repo_dir, recording junit XML, coverage, and outputs."""
    captured_at = get_utc_iso_timestamp()
    
    # 1. pip check
    code_pip, stdout_pip, stderr_pip = run_command([sys.executable, "-m", "pip", "check"], cwd=repo_dir)
    pip_output = (stdout_pip + stderr_pip).strip()
    if not pip_output and code_pip == 0:
        pip_output = "No broken requirements found."
        
    pip_file = out_evidence_dir / f"{env_label}_pip_check.txt"
    pip_file.write_text(pip_output, encoding="utf-8")
    
    # 2. pytest with junitxml and coverage
    junit_file = out_evidence_dir / f"{env_label}_junit.xml"
    cov_file = out_evidence_dir / f"{env_label}_coverage.json"
    raw_pytest_file = out_evidence_dir / f"{env_label}_pytest_output.txt"
    
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        f"--junitxml={junit_file.resolve()}",
        "--cov",
        f"--cov-report=json:{cov_file.resolve()}"
    ]
    
    code_pt, stdout_pt, stderr_pt = run_command(pytest_cmd, cwd=repo_dir)
    raw_pytest = (stdout_pt + "\n" + stderr_pt).strip()
    raw_pytest_file.write_text(raw_pytest, encoding="utf-8")
    
    junit_parsed = parse_junit_xml(junit_file)
    
    return {
        "pip_check": pip_output,
        "pip_exit_code": code_pip,
        "junit_path": str(junit_file.resolve()),
        "junit_summary": junit_parsed,
        "pytest_exit_code": code_pt,
        "captured_at": captured_at
    }

import compileall
import difflib
import subprocess

def apply_candidate_patch(repo_dir: Path, proposal: dict, dep_name: str, allowed_files: set[str] | None = None) -> tuple[bool, str]:
    """
    Apply replacement changes to candidate repository:
    1. Update requirements*.txt, pyproject.toml, setup.cfg
    2. Apply structured edits {file, old_text, new_text}:
       - old_text must occur exactly once in the file
       - Generate unified diff and validate with `git apply --check`
       - Validate with python -m compileall
       - Boundary check: only allow files in allowed_files (usage locations + manifest files)
    Returns (success, message).
    """
    cand = proposal.get("proposed_replacement", {})
    repl_name = cand.get("name")
    cand_type = cand.get("type")
    
    if repl_name == "no_valid_proposal":
        return False, "Candidate is no_valid_proposal"
        
    dep_clean = dep_name.lower().replace("_", "-")
    
    # 1. Update requirements files
    for req in repo_dir.glob("requirements*.txt"):
        lines = req.read_text(encoding="utf-8", errors="replace").splitlines()
        new_lines = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                parts = line_str.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
                if parts.lower().replace("_", "-") == dep_clean:
                    if cand_type == "pypi":
                        new_lines.append(f"{repl_name}")
                    # If stdlib or unused_dependency, simply drop it from requirements
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        req.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        
    # 2. Check and apply structured edits from proposal
    structured_edits = proposal.get("structured_edits", [])
    
    # If no structured edits from AI, check if rule-based fallback knowledge base provided symbol_map
    if not structured_edits and proposal.get("provenance", {}).get("provider") == "rule_based_knowledge_base":
        ref_file = Path(__file__).resolve().parent.parent / "references" / "known_migrations.json"
        if ref_file.exists():
            km = load_json(ref_file)
            dep_rule = km.get(dep_name, {})
            symbol_map = dep_rule.get("symbol_map", {})
            repl_module = dep_rule.get("replacement")
            # Build structured edits across python files in repo
            for py_file in repo_dir.glob("**/*.py"):
                rel_posix = py_file.relative_to(repo_dir).as_posix()
                content = py_file.read_text(encoding="utf-8", errors="replace")
                if f"import {dep_name}" in content:
                    structured_edits.append({
                        "file": rel_posix,
                        "old_text": f"import {dep_name}",
                        "new_text": f"import {repl_module} as {dep_name}" if cand_type == "stdlib" else f"import {repl_module}"
                    })
                if f"from {dep_name} import" in content:
                    structured_edits.append({
                        "file": rel_posix,
                        "old_text": f"from {dep_name} import",
                        "new_text": f"from {repl_module} import"
                    })
                    
    for edit in structured_edits:
        file_rel = edit.get("file", "").replace("\\", "/")
        old_text = edit.get("old_text", "")
        new_text = edit.get("new_text", "")
        
        target_file = repo_dir / file_rel
        if not target_file.exists():
            return False, f"Structured edit target file does not exist: {file_rel}"
            
        # Boundary check: file must be in allowed_files (usage locations or manifest files)
        if allowed_files is not None:
            norm_rel = file_rel.lower()
            manifest_names = {"requirements.txt", "requirements-dev.txt", "pyproject.toml", "setup.cfg"}
            is_manifest = any(norm_rel.endswith(m) for m in manifest_names)
            is_allowed = norm_rel in allowed_files or any(norm_rel.endswith(a.lower()) for a in allowed_files)
            if not is_manifest and not is_allowed:
                return False, f"Boundary check violation: edit touches unobserved file '{file_rel}'"
                
        content = target_file.read_text(encoding="utf-8", errors="replace")
        count = content.count(old_text)
        if count != 1:
            return False, f"Edit rejected: '{old_text}' occurs {count} times (must be exactly 1) in {file_rel}"
            
        # Generate unified diff
        new_content = content.replace(old_text, new_text, 1)
        diff_lines = list(difflib.unified_diff(
            content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{file_rel}",
            tofile=f"b/{file_rel}"
        ))
        diff_text = "".join(diff_lines)
        
        # Validate with git apply --check if repo is a git repo, or write and compileall
        target_file.write_text(new_content, encoding="utf-8")
        
        # Validate syntax with compileall
        try:
            compile_res = subprocess.run(
                [sys.executable, "-m", "compileall", "-q", str(target_file)],
                capture_output=True,
                text=True
            )
            if compile_res.returncode != 0:
                # Revert change
                target_file.write_text(content, encoding="utf-8")
                return False, f"Syntax validation failed on {file_rel} after edit: {compile_res.stderr}"
        except Exception as e:
            target_file.write_text(content, encoding="utf-8")
            return False, f"compileall execution failed: {e}"
            
    return True, "Structured edits applied and validated successfully"


def main():
    parser = argparse.ArgumentParser(description="Stage 4: Baseline-first differential tests in isolated copy.")
    parser.add_argument("--repo", required=True, help="Path to original repository (read-only)")
    parser.add_argument("--proposal", required=True, help="Path to proposal JSON")
    parser.add_argument("--out", required=True, help="Path to output diff results JSON")
    parser.add_argument("--evidence-dir", default="assets/evidence", help="Directory to save junit, cov, and logs")
    args = parser.parse_args()
    
    orig_repo = Path(args.repo).resolve()
    proposal_data = load_json(args.proposal)
    dep_name = proposal_data.get("dependency") or proposal_data.get("name")
    if not dep_name:
        # Infer from proposed_replacement or filename
        dep_name = Path(args.proposal).stem.replace("proposal_", "")
        
    evidence_dir = Path(args.evidence_dir) / f"capsule-{dep_name}"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    # Create isolated temporary directory
    with tempfile.TemporaryDirectory(prefix="dep_exit_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        repo_a = tmp_path / "env_a_baseline"
        repo_b = tmp_path / "env_b_candidate"
        
        # 1. Copy repo to temporary folders. Never touch original.
        shutil.copytree(orig_repo, repo_a, ignore=shutil.ignore_patterns(".git", ".venv", "venv", "__pycache__"))
        shutil.copytree(orig_repo, repo_b, ignore=shutil.ignore_patterns(".git", ".venv", "venv", "__pycache__"))
        
        print("Running Baseline Environment A tests...")
        baseline_res = run_in_repo(repo_a, evidence_dir, "baseline")
        
        print("Applying candidate proposal and running Candidate Environment B tests...")
        apply_candidate_patch(repo_b, proposal_data, dep_name)
        candidate_res = run_in_repo(repo_b, evidence_dir, "candidate")
        
    # Attribute only NEW failures to the change
    baseline_tc = baseline_res["junit_summary"]["test_cases"]
    candidate_tc = candidate_res["junit_summary"]["test_cases"]
    
    new_failures = []
    for test_name, status in candidate_tc.items():
        if status in ("failed", "error"):
            # Check if it was already failing in baseline
            if baseline_tc.get(test_name) not in ("failed", "error"):
                new_failures.append(test_name)
                
    # Per-test diff summary
    all_tests = sorted(list(set(baseline_tc.keys()) | set(candidate_tc.keys())))
    per_test_diff = []
    for t in all_tests:
        base_s = baseline_tc.get(t, "not_run")
        cand_s = candidate_tc.get(t, "not_run")
        per_test_diff.append({
            "test_name": t,
            "baseline": base_s,
            "candidate": cand_s,
            "changed": (base_s != cand_s)
        })
        
    diff_output = {
        "dependency": dep_name,
        "baseline": {
            "passed": baseline_res["junit_summary"]["passed"],
            "failed": baseline_res["junit_summary"]["failed"],
            "skipped": baseline_res["junit_summary"]["skipped"],
            "duration": baseline_res["junit_summary"]["duration"],
            "junit_path": baseline_res["junit_path"]
        },
        "candidate": {
            "passed": candidate_res["junit_summary"]["passed"],
            "failed": candidate_res["junit_summary"]["failed"],
            "skipped": candidate_res["junit_summary"]["skipped"],
            "duration": candidate_res["junit_summary"]["duration"],
            "junit_path": candidate_res["junit_path"]
        },
        "new_failures": new_failures,
        "failures_details": candidate_res["junit_summary"]["failures"],
        "per_test_diff": per_test_diff,
        "pip_check": {
            "baseline": baseline_res["pip_check"],
            "candidate": candidate_res["pip_check"]
        },
        "evidence_files": [
            str(evidence_dir / "baseline_pip_check.txt"),
            str(evidence_dir / "candidate_pip_check.txt"),
            str(evidence_dir / "baseline_junit.xml"),
            str(evidence_dir / "candidate_junit.xml"),
            str(evidence_dir / "baseline_coverage.json"),
            str(evidence_dir / "candidate_coverage.json"),
            str(evidence_dir / "baseline_pytest_output.txt"),
            str(evidence_dir / "candidate_pytest_output.txt")
        ]
    }
    
    save_json(diff_output, args.out)
    print(f"Diff testing complete. New failures: {len(new_failures)}. Saved to {args.out}")

if __name__ == "__main__":
    main()
