# Dependency Exit Capsule: `nose`

- **Capsule ID**: `capsule-linkwatch-nose-20261024_201058`
- **Generated At**: `2026-10-24T20:10:58.484590+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'nose' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `4162` | [https://pypi.org/pypi/nose/json](https://pypi.org/pypi/nose/json) | 2026-10-24T20:09:07.417412+00:00 |
| yanked | `False` | [https://pypi.org/pypi/nose/json](https://pypi.org/pypi/nose/json) | 2026-10-24T20:09:07.417412+00:00 |

### Code Usage (0 locations across 15 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `unittest` (stdlib)
- **Provenance**: Provider `ollama` | Model `llama3.1:8b` | License `LLAMA 3.1 COMMUNITY LICENSE AGREEMENT`
- **API Coverage Gate**: 100%

### Migration Steps
1. Remove nose dependency from requirements.txt
1. Update test suite to use unittest instead of nose

### Suggested Tests
- Run tests with Python 3.14.6 to ensure unittest works as expected
- Verify test coverage using tools like coverage.py

### Compatibility Gaps & Open Concerns
- [AI] No significant incompatibilities are expected since unittest is the standard testing framework for Python
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/nose_raw_model_response.json` | `f78fa95aa42bf232ebe2d47154d08be17c59291f845cd84a239df158ae23b848` | `ollama run llama3.1:8b` | 2026-10-24T20:10:58.484556+00:00 |
