# Dependency Exit Capsule: `pytest`

- **Capsule ID**: `capsule-linkwatch-pytest-20261024_202319`
- **Generated At**: `2026-10-24T20:23:19.696562+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'pytest' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `127` | [https://pypi.org/pypi/pytest/json](https://pypi.org/pypi/pytest/json) | 2026-10-24T20:21:51.331826+00:00 |
| yanked | `False` | [https://pypi.org/pypi/pytest/json](https://pypi.org/pypi/pytest/json) | 2026-10-24T20:21:51.331826+00:00 |

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
- **Provenance**: Provider `ollama` | Model `llama3.2:3b` | License `LLAMA 3.2 COMMUNITY LICENSE AGREEMENT`
- **API Coverage Gate**: 0%

### Migration Steps

### Suggested Tests

### Compatibility Gaps & Open Concerns
- [AI] Candidate rejected by validation gate: not in stdlib
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/pytest_raw_model_response.json` | `ad85c4092a2cb172a0e38cdbe2a83e67d0cbe71134725cdd36f66691c0b01969` | `ollama run llama3.2:3b` | 2026-10-24T20:23:19.696520+00:00 |
