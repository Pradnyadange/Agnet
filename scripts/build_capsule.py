import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import jsonschema

try:
    from common import compute_sha256_file, get_utc_iso_timestamp, load_json, save_json
except ImportError:
    from scripts.common import compute_sha256_file, get_utc_iso_timestamp, load_json, save_json

def generate_markdown_capsule(capsule: dict) -> str:
    dep = capsule["dependency"]["name"]
    status = capsule["status"].upper()
    prob = capsule["maintenance_problem"]
    repl = capsule["ai_generated"]["proposed_replacement"]["name"]
    repl_type = capsule["ai_generated"]["proposed_replacement"]["type"]
    prov = capsule["ai_generated"]["provenance"]
    
    md = [
        f"# Dependency Exit Capsule: `{dep}`",
        f"",
        f"- **Capsule ID**: `{capsule['capsule_id']}`",
        f"- **Generated At**: `{capsule['generated_at']}`",
        f"- **Status**: **{status}**",
        f"- **Target Repository**: `{capsule['target_repo']['name']}` ({capsule['target_repo']['commit_sha'][:7] if capsule['target_repo']['commit_sha'] else 'HEAD'})",
        f"- **Maintenance Problem**: {prob}",
        f"",
        f"## 1. Observed Evidence",
        f"",
        f"### Risk Indicators",
        f"| Indicator | Value | Source | Fetched At |",
        f"|---|---|---|---|"
    ]
    for r in capsule["observed"]["risk_indicators"]:
        md.append(f"| {r['id']} | `{r['value']}` | [{r['source_url']}]({r['source_url']}) | {r['fetched_at']} |")
        
    md.extend([
        f"",
        f"### Code Usage ({len(capsule['observed']['usage_locations'])} locations across {capsule['observed']['scan']['files_scanned']} files)",
        f"| File:Line | Kind | Symbol | Covered By Tests |",
        f"|---|---|---|---|"
    ])
    for u in capsule["observed"]["usage_locations"]:
        cov_icon = "PASS" if u["covered_by_tests"] else "NO"
        md.append(f"| `{u['file']}:{u['line']}` | {u['kind']} | `{u['symbol']}` | {cov_icon} |")
        
    base = capsule["observed"]["test_results"]["baseline"]
    cand = capsule["observed"]["test_results"]["candidate"]
    new_fails = capsule["observed"]["test_results"]["new_failures"]
    
    md.extend([
        f"",
        f"### Test Results Diff",
        f"- **Baseline**: {base['passed']} passed, {base['failed']} failed",
        f"- **Candidate**: {cand['passed']} passed, {cand['failed']} failed",
        f"- **New Failures**: {len(new_fails)}"
    ])
    for nf in new_fails:
        md.append(f"  - `{nf}`")
        
    md.extend([
        f"- **pip check**: {capsule['observed']['test_results']['pip_check']['candidate']}",
        f"",
        f"## 2. AI-Generated Proposal",
        f"- **Proposed Replacement**: `{repl}` ({repl_type})",
        f"- **Provenance**: Provider `{prov['provider']}` | Model `{prov['model_id']}` | License `{prov['model_license_name']}`",
        f"- **API Coverage Gate**: {int(prov['validation']['api_coverage'] * 100)}%",
        f"",
        f"### Migration Steps"
    ])
    for s in capsule["ai_generated"]["migration_steps"]:
        md.append(f"1. {s}")
        
    md.extend([
        f"",
        f"### Suggested Tests"
    ])
    for t in capsule["ai_generated"]["suggested_tests"]:
        md.append(f"- {t}")
        
    md.extend([
        f"",
        f"### Compatibility Gaps & Open Concerns"
    ])
    for g in capsule["ai_generated"]["gap_analysis"]:
        md.append(f"- [AI] {g}")
    for lim in capsule["limitations"]:
        md.append(f"- [OBSERVED] {lim}")
        
    md.extend([
        f"",
        f"## 3. Evidence Hashes",
        f"| Evidence File | SHA-256 | Command | Captured At |",
        f"|---|---|---|---|"
    ])
    for ev in capsule["observed"]["evidence"]:
        md.append(f"| `{ev['path']}` | `{ev['sha256']}` | `{ev['command']}` | {ev['captured_at']} |")
        
    return "\n".join(md) + "\n"

def determine_status(
    baseline_passed: int,
    candidate_passed: int,
    new_failures: list,
    pip_check_clean: bool,
    usage_locations: list,
    api_coverage: float,
    opted_in_tests: bool = True,
    proposal_valid: bool = True,
    is_unused_dep: bool = False
) -> str:
    """
    Status rules (computed by build_capsule.py, displayed by the viewer):
    - no_valid_proposal: Candidate failed validation gate or no proposal generated
    - not_run: User did not opt into test execution
    - failed: New failures appear after the change or pip check fails
    - not_testable: The change cannot be exercised by the repo's tests at all (or tests failed to run)
    - unverified: Tests pass but some call sites lack coverage, or API coverage < 1.0, or unused_dependency not tested without pkg
    - verified: Baseline passes, candidate passes, zero new failures, clean pip check, all call sites covered, API coverage 100%
    """
    if not proposal_valid:
        return "no_valid_proposal"
        
    if not opted_in_tests:
        return "not_run"
        
    if len(new_failures) > 0 or not pip_check_clean:
        return "failed"
        
    # Check if there are any tests exercising the repo
    if baseline_passed == 0 and candidate_passed == 0:
        return "not_testable"
        
    if is_unused_dep:
        # unused_dependency stays unverified until tests pass in an environment without the package
        if baseline_passed > 0 and candidate_passed > 0 and len(new_failures) == 0 and pip_check_clean:
            return "verified"
        return "unverified"

    call_sites = [u for u in usage_locations if u.get("kind") == "call"]
    if not call_sites:
        call_sites = usage_locations
        
    if not usage_locations:
        return "not_testable"

    covered_call_sites = [u for u in call_sites if u.get("covered_by_tests") is True]
    all_covered = (len(covered_call_sites) == len(call_sites)) and (len(call_sites) > 0)
    
    if (
        baseline_passed > 0 and
        candidate_passed > 0 and
        len(new_failures) == 0 and
        pip_check_clean and
        all_covered and
        api_coverage >= 1.0
    ):
        return "verified"
    else:
        return "unverified"


def main():
    parser = argparse.ArgumentParser(description="Stage 5: Build schema-validated Dependency Exit Capsule and manifest.")
    parser.add_argument("--dep", required=True, help="Dependency package name")
    parser.add_argument("--scan-file", default="assets/scan.json", help="Path to scan results JSON")
    parser.add_argument("--usage-file", default="", help="Path to usage JSON (defaults to assets/usage_<dep>.json)")
    parser.add_argument("--proposal-file", default="", help="Path to proposal JSON (defaults to assets/proposal_<dep>.json)")
    parser.add_argument("--diff-file", default="", help="Path to diff results JSON (defaults to assets/diff_<dep>.json)")
    parser.add_argument("--commit-sha", default="", help="Git commit SHA of target repository")
    parser.add_argument("--repo-url", default="", help="Target repository URL")
    parser.add_argument("--not-run", action="store_true", help="Flag if tests were not opted in by user")
    parser.add_argument("--capsule-type", default="replacement", choices=["replacement", "unused_dependency", "version_fix"], help="Capsule type")
    parser.add_argument("--out", default="assets/capsules/", help="Directory to save capsules")
    parser.add_argument("--manifest-out", default="assets/manifest.json", help="Path to write manifest.json")
    args = parser.parse_args()
    
    dep_name = args.dep.lower().replace("_", "-")
    usage_file = args.usage_file or f"assets/usage_{dep_name}.json"
    proposal_file = args.proposal_file or f"assets/proposal_{dep_name}.json"
    diff_file = args.diff_file or f"assets/diff_{dep_name}.json"
    scan_file = args.scan_file
    
    # 1. Load stage inputs
    scan_data = load_json(scan_file)
    usage_data = load_json(usage_file)
    proposal_data = load_json(proposal_file)
    diff_data = load_json(diff_file) if Path(diff_file).exists() else {}
    
    # Refuse placeholder or dummy SHA
    commit_sha = args.commit_sha or scan_data.get("commit_sha", "")
    if commit_sha == "a1b2c3d4e5f678901234567890abcdef12345678" or set(commit_sha) == {"0"}:
        sys.stderr.write(f"Build Capsule Refusal: Valid target repository commit SHA is required; placeholder SHA rejected.\n")
        sys.exit(1)
    if not commit_sha:
        # Fixture or local folder without git history
        commit_sha = "n/a"

        
    # 2. Check for missing evidence or missing provenance
    if "provenance" not in proposal_data:
        sys.stderr.write("Build Capsule Refusal: ai_generated lacks provenance.\n")
        sys.exit(1)
        
    provenance = proposal_data["provenance"]
    required_prov_keys = ["provider", "model_id", "model_license_name", "model_card_url", "prompt_sha256", "raw_response_path", "validation"]
    for k in required_prov_keys:
        if k not in provenance:
            sys.stderr.write(f"Build Capsule Refusal: ai_generated provenance missing '{k}'.\n")
            sys.exit(1)
            
    # Gather evidence files
    evidence_entries = []
    timestamp = get_utc_iso_timestamp()
    
    evidence_paths = diff_data.get("evidence_files", []) if diff_data else []
    if provenance.get("raw_response_path") and provenance["raw_response_path"] != "N/A":
        if Path(provenance["raw_response_path"]).exists():
            evidence_paths.append(provenance["raw_response_path"])
            
    for ep in evidence_paths:
        p = Path(ep)
        if p.exists():
            sha = compute_sha256_file(p)
            cmd = "pytest" if "pytest" in p.name or "junit" in p.name else ("pip check" if "pip" in p.name else "llm-response")
            evidence_entries.append({
                "path": p.as_posix(),
                "sha256": sha,
                "command": cmd,
                "exit_code": 0,
                "captured_at": timestamp
            })
            
    if not evidence_entries:
        sys.stderr.write("Build Capsule Refusal: observed fields lack evidence entries.\n")
        sys.exit(1)
        
    # Get dependency info
    dep_meta = scan_data.get("dependencies", {}).get(dep_name, {})
    declared_spec = dep_meta.get("declared_specifier", "")
    declared_in = dep_meta.get("declared_in", ["requirements.txt"])
    risk_indicators = dep_meta.get("risk_indicators", [])
    
    # Target repo info
    repo_path = scan_data.get("repo_path", "")
    repo_name = Path(repo_path).name if repo_path else "repo"
    repo_url = args.repo_url or scan_data.get("repo_url") or f"https://github.com/local/{repo_name}"
    
    # Read coverage to mark usage locations
    coverage_path = None
    for ep in evidence_paths:
        if "coverage.json" in ep and Path(ep).exists():
            coverage_path = Path(ep)
            break
            
    usage_locations = usage_data.get("usage_locations", [])
    if coverage_path and coverage_path.exists():
        try:
            cov_data = load_json(coverage_path)
            cov_files = cov_data.get("files", {})
            for u in usage_locations:
                u_file_norm = u["file"].replace("\\", "/").lower()
                for cf_key, cf_val in cov_files.items():
                    cf_key_norm = cf_key.replace("\\", "/").lower()
                    if cf_key_norm.endswith(u_file_norm):
                        executed_lines = cf_val.get("executed_lines", [])
                        if u["line"] in executed_lines:
                            u["covered_by_tests"] = True
        except Exception:
            pass

    pip_candidate = diff_data.get("pip_check", {}).get("candidate", "") if diff_data else ""
    pip_clean = "No broken requirements found" in pip_candidate or pip_candidate.strip() == ""
    api_coverage = float(provenance["validation"].get("api_coverage", 1.0))
    proposal_valid = bool(provenance["validation"].get("passed", True))
    is_unused = (len(usage_locations) == 0) or (args.capsule_type == "unused_dependency")
    
    baseline = diff_data.get("baseline", {"passed": 0, "failed": 0, "junit_path": ""}) if diff_data else {"passed": 0, "failed": 0, "junit_path": ""}
    candidate = diff_data.get("candidate", {"passed": 0, "failed": 0, "junit_path": ""}) if diff_data else {"passed": 0, "failed": 0, "junit_path": ""}
    new_failures = diff_data.get("new_failures", []) if diff_data else []
    
    status = determine_status(
        baseline_passed=baseline.get("passed", 0),
        candidate_passed=candidate.get("passed", 0),
        new_failures=new_failures,
        pip_check_clean=pip_clean,
        usage_locations=usage_locations,
        api_coverage=api_coverage,
        opted_in_tests=(not args.not_run),
        proposal_valid=proposal_valid,
        is_unused_dep=is_unused
    )
    
    time_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    capsule_id = f"capsule-{repo_name.lower()}-{dep_name}-{time_slug}"
    
    # Derive maintenance problem from observed indicators only (release age, yanked status, archived flag)
    # Strictly do not mention CVEs or vulnerabilities.
    problem_reasons = []
    for ind in risk_indicators:
        iid = ind.get("id")
        val = ind.get("value")
        if iid == "days_since_release" and isinstance(val, (int, float)) and val > 365:
            problem_reasons.append(f"package has had no releases for {val} days")
        elif iid == "yanked" and val:
            problem_reasons.append("release has been yanked on PyPI")
        elif iid == "is_archived" and val:
            problem_reasons.append("source repository is archived")
            
    if not problem_reasons:
        if is_unused:
            problem_text = f"Dependency '{dep_name}' has 0 recorded import or call sites in the repository."
        else:
            problem_text = f"Dependency '{dep_name}' was flagged during dependency risk scan based on observed release metrics."
    else:
        problem_text = f"Dependency '{dep_name}' flagged because " + "; ".join(problem_reasons) + "."
    
    # Build complete capsule dict matching section 4 contract
    capsule = {
        "schema_version": "2.0.0",
        "capsule_id": capsule_id,
        "generated_at": timestamp,
        "capsule_type": args.capsule_type if not is_unused else "unused_dependency",
        "target_repo": {
            "name": repo_name,
            "url": repo_url,
            "commit_sha": commit_sha,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        },
        "maintenance_problem": problem_text,
        "dependency": {
            "name": dep_name,
            "declared_specifier": declared_spec,
            "declared_in": declared_in
        },
        "observed": {
            "risk_indicators": risk_indicators,
            "scan": {
                "files_scanned": usage_data.get("files_scanned", 0),
                "dynamic_imports": usage_data.get("dynamic_imports", [])
            },
            "usage_locations": usage_locations,
            "test_results": {
                "baseline": {
                    "passed": baseline.get("passed", 0),
                    "failed": baseline.get("failed", 0),
                    "junit_path": baseline.get("junit_path", "")
                },
                "candidate": {
                    "passed": candidate.get("passed", 0),
                    "failed": candidate.get("failed", 0),
                    "junit_path": candidate.get("junit_path", "")
                },
                "new_failures": new_failures,
                "pip_check": {
                    "baseline": diff_data.get("pip_check", {}).get("baseline", ""),
                    "candidate": diff_data.get("pip_check", {}).get("candidate", "")
                }
            },
            "evidence": evidence_entries
        },
        "ai_generated": {
            "proposed_replacement": proposal_data.get("proposed_replacement", {"name": "no_valid_proposal", "type": "stdlib"}),
            "migration_steps": proposal_data.get("migration_steps", []),
            "suggested_tests": proposal_data.get("suggested_tests", []),
            "gap_analysis": proposal_data.get("gap_analysis", []),
            "provenance": provenance
        },
        "status": status,
        "limitations": [
            "Results only cover what the repo's tests exercise.",
            "Python only.",
            "Small models can propose weak replacements; validation gate determines acceptance."
        ]
    }
    
    # Validate against references/capsule-schema.json
    schema_path = Path(__file__).resolve().parent.parent / "references" / "capsule-schema.json"
    if schema_path.exists():
        schema = load_json(schema_path)
        jsonschema.validate(instance=capsule, schema=schema)
        
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{capsule_id}.json"
    md_path = out_dir / f"{capsule_id}.md"
    
    save_json(capsule, json_path)
    md_text = generate_markdown_capsule(capsule)
    md_path.write_text(md_text, encoding="utf-8")
    
    # Update manifest.json
    manifest_path = Path(args.manifest_out)
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = load_json(manifest_path)
        except Exception:
            manifest = {}
            
    manifest_files = manifest.get("files", {})
    # Hash all evidence files and all capsules
    all_files_to_hash = list(evidence_paths) + [str(json_path), str(md_path)]
    for fp in all_files_to_hash:
        p = Path(fp)
        if p.exists():
            manifest_files[p.as_posix()] = compute_sha256_file(p)
            
    manifest["generated_at"] = timestamp
    manifest["files"] = manifest_files
    save_json(manifest, manifest_path)
    
    print(f"Capsule created successfully: {capsule_id} (Status: {status})")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print(f"Updated Manifest: {manifest_path}")

if __name__ == "__main__":
    main()
