# Dependency Exit Capsule: `uvicorn`

- **Capsule ID**: `capsule-gpt-researcher-uvicorn-20261024_194944`
- **Generated At**: `2026-10-24T19:49:44.439326+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'uvicorn' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `29` | [https://pypi.org/pypi/uvicorn/json](https://pypi.org/pypi/uvicorn/json) | 2026-10-24T19:44:38.415814+00:00 |
| yanked | `False` | [https://pypi.org/pypi/uvicorn/json](https://pypi.org/pypi/uvicorn/json) | 2026-10-24T19:44:38.415814+00:00 |

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
- [AI] Candidate rejected by validation gate: API coverage below 100% (0%)
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/uvicorn_raw_model_response.json` | `27cab655df92d182493681501ae3d5aa91116e003a788611e25dbc1b7c0bfa72` | `ollama run gemma2:2b` | 2026-10-24T19:49:44.439239+00:00 |
