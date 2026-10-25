---
name: dependency-exit-capsule
description: Safely exit risky Python dependencies with evidence, AST blast radius mapping, model migration proposals, and isolated differential tests.
---

# Dependency Exit Capsule: Maintenance Agent Skill

Point this skill at a Python repository. It finds dependencies with risk indicators, shows exactly where they are used via AST analysis, proposes replacements via open-weight model or rule-based fallback, runs the repo's own tests in an isolated sandbox with the old vs new version, and records everything in an unalterable, hashed Dependency Exit Capsule.

## When to Use This Skill
- When auditing a Python project for abandoned, yanked, or stale packages.
- When planning a safe deprecation or replacement of a third-party dependency.
- When generating tamper-evident evidence packages (junit XML, pip check, AST blast radius) before merging a migration PR.

## Exact Commands & Steps

### Step 1: Scan Risk Indicators
Scan `requirements*.txt` and `pyproject.toml` against PyPI JSON endpoints:
```bash
python scripts/scan_risk.py --repo <path_to_repo> --out assets/scan.json
```

### Step 2: Map AST Usage Locations
Trace every direct import, alias call, and attribute usage down to `file:line`:
```bash
python scripts/map_usage.py --repo <path_to_repo> --dep <dependency_name> --out assets/usage_<dependency_name>.json
```

### Step 3: Propose Replacement & Validate Gate
Query an open-weight model (e.g. Qwen 2.5 Coder 7B via Ollama) or offline rule-based knowledge base:
```bash
# Model-assisted
python scripts/propose_replacement.py --dep <dependency_name> --usage-file assets/usage_<dependency_name>.json --provider ollama --ollama-model qwen2.5-coder:7b --out assets/proposal_<dependency_name>.json

# Or offline fallback
python scripts/propose_replacement.py --dep <dependency_name> --usage-file assets/usage_<dependency_name>.json --offline --out assets/proposal_<dependency_name>.json
```

### Step 4: Run Baseline-First Differential Tests
Execute test suites across isolated baseline and candidate environments:
```bash
python scripts/run_diff_tests.py --repo <path_to_repo> --proposal assets/proposal_<dependency_name>.json --out assets/diff_<dependency_name>.json
```

### Step 5: Build Sealed Capsule and Manifest
Assemble the capsule, determine status (`verified`, `unverified`, `not_testable`, `failed`), and generate SHA-256 manifest:
```bash
python scripts/build_capsule.py --dep <dependency_name> --out assets/capsules/
```

### Step 6: Verify Cryptographic Integrity
Check all capsule files and test evidence logs against SHA-256 hashes:
```bash
python scripts/verify_capsule.py assets/manifest.json
```

### Step 7: Launch Interactive Viewer
Inspect the generated capsules, diffs, and blast radius:
```bash
streamlit run app.py
```

## Security & Integrity Design
- **Prompt Injection Defense**: Repository texts, code snippets, and README comments are isolated in delimited passive blocks labeled `UNTRUSTED DATA`. The model is restricted to JSON-only output and passes through validation gates before any candidate is entertained.
- **Secret Redaction**: Common secret tokens (API keys, bearer tokens, passwords) are scrubbed before prompt submission. Redaction counts are permanently recorded in capsule metadata. Sensitive files such as `.env` are automatically excluded.
- **Replacement Trust Verification**: Third-party replacement packages are checked against PyPI metadata (release history, source repository links, and typo-squatting edit distances).
- **Vulnerability Data Policy**: Security vulnerabilities and advisory data (CVEs/GHSA) are NOT used to rank packages or determine capsule status (`verified`/`unverified`/`failed`). If vulnerability or advisory information is observed, it is recorded strictly as informational metadata and is never used in exit decision logic.

