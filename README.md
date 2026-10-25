# Dependency Exit Capsule: H26_Softerror_TrustLedger

Hackathon Track 2 (Maintenance Agent Skill) | Target repository: LinkWatch | Living spec version 1

A tool that helps a maintainer safely stop using a risky dependency, and a website that lets anyone inspect the evidence.

## The One-Sentence Pitch
Point the skill at a Python repository. It finds dependencies that look risky, shows exactly where they are used, asks an open-weight model for a replacement, runs the repo's own tests with the old and the new version, and records everything in a Dependency Exit Capsule that keeps what we observed apart from what the AI suggested.

## Architecture

- **Engine (`scripts/`)**: Scans repo risk indicators, maps AST usage, proposes validated replacements, runs isolated diff tests, builds signed/hashed capsules.
- **Capsule Data (`assets/capsules/`, `assets/evidence/`, `assets/manifest.json`)**: Schema-validated JSON and human-readable Markdown capsules with tamper-evident SHA-256 hashes.
- **Viewer (`app.py`, `viewer/`)**: Streamlit application displaying verified vs unverified capsules, evidence logs, junit diffs, AST blast-radius graph, and integrity checks. Displays observed data and model results with absolute honesty.

## Quick Start

### 1. Requirements
- Python 3.12+
- Dependencies: `pip install -r dependency-exit-capsule/requirements.txt`

### 2. Run Pipeline (Per Dependency)
All commands are run from the self-contained `dependency-exit-capsule/` directory:
```bash
cd dependency-exit-capsule

python scripts/scan_risk.py --repo <path> --out assets/scan.json
python scripts/map_usage.py --repo <path> --dep <name> --out assets/usage_<name>.json
python scripts/propose_replacement.py --dep <name> --usage-file assets/usage_<name>.json --provider ollama --ollama-model qwen2.5-coder:7b --out assets/proposal_<name>.json
python scripts/run_diff_tests.py --repo <path> --proposal assets/proposal_<name>.json --out assets/diff_<name>.json
python scripts/build_capsule.py --dep <name> --out assets/capsules/
python scripts/verify_capsule.py assets/manifest.json
```

Or run offline rule-based replacement:
```bash
python scripts/propose_replacement.py --dep <name> --usage-file assets/usage_<name>.json --offline --out assets/proposal_<name>.json
```

### 3. Launch Viewer
```bash
streamlit run app.py
```
View the dashboard at `http://localhost:8501`.

## Model Information
- **Default Local Model**: Qwen 2.5 Coder 7B / Llama 3.1 8B via Ollama
- **Model Card**: https://ollama.com/library/qwen2.5-coder
- **License**: Apache 2.0
- **Privacy Note**: Local mode (`--provider ollama`) sends zero network traffic externally. Hosted mode sends code snippets and usage sites to the chosen provider API.

## Honest Limitations
1. **Test Suite Coverage**: Results only cover what the repo's existing test suite exercises. Uncovered call sites are reported as `not_testable`.
2. **Python Only**: The AST mapper and test harness are specialized for Python projects.
3. **Model Quality & Validation Gate**: Small local models can propose weak or incomplete replacements; the validation gate (`sys.stdlib_module_names`, API symbol coverage check, and pytest diffs) determines acceptance, not model confidence.
4. **Display Only**: The viewer displays saved runs and integrity manifests. It does not perform live repo modifications or auto-merges.
