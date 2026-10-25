# Dependency Exit Capsule: `pytest`

- **Capsule ID**: `capsule-linkwatch-pytest-20261025_073042`
- **Generated At**: `2026-10-25T07:30:42.916045+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'pytest' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `127` | [https://pypi.org/pypi/pytest/json](https://pypi.org/pypi/pytest/json) | 2026-10-25T07:26:05.511958+00:00 |
| yanked | `False` | [https://pypi.org/pypi/pytest/json](https://pypi.org/pypi/pytest/json) | 2026-10-25T07:26:05.511958+00:00 |

### Code Usage (2 locations across 15 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `tests/conftest.py:6` | import | `pytest` | NO |
| `tests/conftest.py:60` | call | `fixture` | NO |

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `no_valid_proposal` (stdlib)
- **Provenance**: Provider `ollama` | Model `llama3.1:8b` | License `LLAMA 3.1 COMMUNITY LICENSE AGREEMENT`
- **API Coverage Gate**: 0%

### Migration Steps

### Suggested Tests

### Compatibility Gaps & Open Concerns
- [AI] Candidate rejected by validation gate: unknown replacement type
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/pytest_raw_model_response.json` | `fdc2d005027da6c5ed60352e5f6fc2f4e4f69be3b293f091dc8abcaba1f534c3` | `ollama run llama3.1:8b` | 2026-10-25T07:30:42.916009+00:00 |
