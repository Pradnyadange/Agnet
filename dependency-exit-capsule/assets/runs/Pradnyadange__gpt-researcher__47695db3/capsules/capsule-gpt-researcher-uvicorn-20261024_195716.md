# Dependency Exit Capsule: `uvicorn`

- **Capsule ID**: `capsule-gpt-researcher-uvicorn-20261024_195716`
- **Generated At**: `2026-10-24T19:57:16.082662+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'uvicorn' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `29` | [https://pypi.org/pypi/uvicorn/json](https://pypi.org/pypi/uvicorn/json) | 2026-10-24T19:52:17.879203+00:00 |
| yanked | `False` | [https://pypi.org/pypi/uvicorn/json](https://pypi.org/pypi/uvicorn/json) | 2026-10-24T19:52:17.879203+00:00 |

### Code Usage (6 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `backend/run_server.py:8` | import | `uvicorn` | NO |
| `backend/run_server.py:21` | call | `run` | NO |
| `backend/server/app.py:791` | import | `uvicorn` | NO |
| `backend/server/app.py:792` | call | `run` | NO |
| `main.py:34` | import | `uvicorn` | NO |
| `main.py:37` | call | `run` | NO |

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `no_valid_proposal` (stdlib)
- **Provenance**: Provider `ollama` | Model `gemma2:2b` | License `Gemma Terms of Use `
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
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/uvicorn_raw_model_response.json` | `f2ab33ecfff67aa54573edecc173922573ca3d4582724e629ebdc37447b69d55` | `ollama run gemma2:2b` | 2026-10-24T19:57:16.082634+00:00 |
