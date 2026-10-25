# Dependency Exit Capsule: `uvicorn`

- **Capsule ID**: `capsule-gpt-researcher-uvicorn-20261025_064931`
- **Generated At**: `2026-10-25T06:49:31.970545+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'uvicorn' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `29` | [https://pypi.org/pypi/uvicorn/json](https://pypi.org/pypi/uvicorn/json) | 2026-10-25T06:40:03.712770+00:00 |
| yanked | `False` | [https://pypi.org/pypi/uvicorn/json](https://pypi.org/pypi/uvicorn/json) | 2026-10-25T06:40:03.712770+00:00 |

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
- **Proposed Replacement**: `hypercorn` (pypi)
- **Provenance**: Provider `ollama` | Model `llama3.1:8b` | License `LLAMA 3.1 COMMUNITY LICENSE AGREEMENT`
- **API Coverage Gate**: 100%

### Migration Steps
1. Update the import statements in all files to import from hypercorn
1. Replace calls to uvicorn.run() with hypercorn.run()

### Suggested Tests
- Test that hypercorn.run() works as expected
- Verify that hypercorn handles edge cases as uvicorn did

### Compatibility Gaps & Open Concerns
- [AI] hypercorn may not support all uvicorn features, may require additional configuration
- [AI] hypercorn may introduce new features that require application-specific handling
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/uvicorn_raw_model_response.json` | `b43dffc89a4ef5d3ea36ecad176ae549ad65100e6d506fc44d60c432d855026b` | `ollama run llama3.1:8b` | 2026-10-25T06:49:31.970491+00:00 |
