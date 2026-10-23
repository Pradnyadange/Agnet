# Dependency Exit Capsule: `toml`

- **Capsule ID**: `capsule-sample_repo-toml-20261022_025545`
- **Generated At**: `2026-10-22T02:55:45.980541+00:00`
- **Status**: **NOT_TESTABLE**
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
| `sample_pkg/core.py:1` | import | `toml` | NO |
| `sample_pkg/core.py:5` | call | `loads` | NO |

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
| `assets/evidence/capsule-toml/baseline_pip_check.txt` | `9bc9eff87ccde9a897a86ea3cf9096facadba3cc998bc2b74cc3d856cf1cc971` | `pip check` | 2026-10-22T02:55:45.980541+00:00 |
| `assets/evidence/capsule-toml/candidate_pip_check.txt` | `9bc9eff87ccde9a897a86ea3cf9096facadba3cc998bc2b74cc3d856cf1cc971` | `pip check` | 2026-10-22T02:55:45.980541+00:00 |
| `assets/evidence/capsule-toml/baseline_junit.xml` | `4a26ca011b3ea3318911560fc8a53340f8b9aae63d698bc598bf62fbd359a4b0` | `pytest` | 2026-10-22T02:55:45.980541+00:00 |
| `assets/evidence/capsule-toml/candidate_junit.xml` | `499cf81d262c0396b4c5088745e9299cb0fb5c3dfa0a3c42a6f38453086fe1cd` | `pytest` | 2026-10-22T02:55:45.980541+00:00 |
| `assets/evidence/capsule-toml/baseline_pytest_output.txt` | `a78bfb74cf5a3b85a2941b5a03e3deb758ae601e228121fd703ead9d685f4259` | `pytest` | 2026-10-22T02:55:45.980541+00:00 |
| `assets/evidence/capsule-toml/candidate_pytest_output.txt` | `6bf36ab2cbe51df456f1a787a6afbfc81262c56b508edcb28f95412667d4fc0c` | `pytest` | 2026-10-22T02:55:45.980541+00:00 |
