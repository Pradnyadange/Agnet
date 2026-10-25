# Dependency Exit Capsule: `toml`

- **Capsule ID**: `capsule-sample_repo-toml-20261022_025633`
- **Generated At**: `2026-10-22T02:56:33.526326+00:00`
- **Status**: **VERIFIED**
- **Target Repository**: `sample_repo` (a1b2c3d)
- **Maintenance Problem**: Dependency toml shows high staleness risk indicators and should be replaced with modern supported alternative.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `2181` | [https://pypi.org/pypi/toml/json](https://pypi.org/pypi/toml/json) | 2026-10-22T02:53:50.391089+00:00 |
| yanked | `False` | [https://pypi.org/pypi/toml/json](https://pypi.org/pypi/toml/json) | 2026-10-22T02:53:50.391089+00:00 |

### Code Usage (2 locations across 2 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `sample_pkg/core.py:1` | import | `toml` | PASS |
| `sample_pkg/core.py:5` | call | `loads` | PASS |

### Test Results Diff
- **Baseline**: 1 passed, 0 failed
- **Candidate**: 1 passed, 0 failed
- **New Failures**: 0
- **pip check**: No broken requirements found.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `tomllib` (stdlib)
- **Provenance**: Provider `rule_based_knowledge_base` | Model `none` | License `N/A`
- **API Coverage Gate**: 100%

### Migration Steps
1. Replace 'import toml' with 'import tomllib' on Python 3.11+
1. Switch to binary file mode (open with 'rb') when calling tomllib.load()
1. Remove 'toml' from requirements.txt

### Suggested Tests
- Test tomllib.loads with basic valid TOML strings
- Test binary stream parsing with tomllib.load

### Compatibility Gaps & Open Concerns
- [AI] tomllib is read-only; writing TOML requires tomli_w if dump/dumps is used
- [AI] Requires Python 3.11 or higher
- [OBSERVED] Results only cover what the repo's tests exercise.
- [OBSERVED] Python only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/evidence/capsule-toml/baseline_pip_check.txt` | `9bc9eff87ccde9a897a86ea3cf9096facadba3cc998bc2b74cc3d856cf1cc971` | `pip check` | 2026-10-22T02:56:33.526326+00:00 |
| `assets/evidence/capsule-toml/candidate_pip_check.txt` | `9bc9eff87ccde9a897a86ea3cf9096facadba3cc998bc2b74cc3d856cf1cc971` | `pip check` | 2026-10-22T02:56:33.526326+00:00 |
| `assets/evidence/capsule-toml/baseline_junit.xml` | `682368db831f41235159401070041e1d7c5624ba8a05ede846aa72ed493c7ce6` | `pytest` | 2026-10-22T02:56:33.526326+00:00 |
| `assets/evidence/capsule-toml/candidate_junit.xml` | `6b37fe36987cebebbda52780c34ae230135758aa31005750a1750bd9668adc82` | `pytest` | 2026-10-22T02:56:33.526326+00:00 |
| `assets/evidence/capsule-toml/baseline_coverage.json` | `19e0e820aff048ed6c8037095d121a884ac1f77ba5f2615f0da9f1845671a5c3` | `llm-response` | 2026-10-22T02:56:33.526326+00:00 |
| `assets/evidence/capsule-toml/candidate_coverage.json` | `53074a7185d8776bd79611b63151ebf1d2a2917e2838d02b880f42cd2ab77ef4` | `llm-response` | 2026-10-22T02:56:33.526326+00:00 |
| `assets/evidence/capsule-toml/baseline_pytest_output.txt` | `ae0190f6d7ec16b7ac1cc1d4fab7bd698922b19bd19dfe441e7d06d9b0a20cbd` | `pytest` | 2026-10-22T02:56:33.526326+00:00 |
| `assets/evidence/capsule-toml/candidate_pytest_output.txt` | `2f484e1a15311a05a272ebd42c50b503debe4e7954079bf55b157d0b4c39387b` | `pytest` | 2026-10-22T02:56:33.526326+00:00 |
