# Dependency Exit Capsule: `pydantic`

- **Capsule ID**: `capsule-gpt-researcher-pydantic-20261025_065117`
- **Generated At**: `2026-10-25T06:51:17.128866+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'pydantic' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `13` | [https://pypi.org/pypi/pydantic/json](https://pypi.org/pypi/pydantic/json) | 2026-10-25T06:40:04.070919+00:00 |
| yanked | `False` | [https://pypi.org/pypi/pydantic/json](https://pypi.org/pypi/pydantic/json) | 2026-10-25T06:40:04.070919+00:00 |

### Code Usage (4 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `gpt_researcher/utils/validators.py:5` | import | `pydantic.BaseModel` | NO |
| `gpt_researcher/utils/validators.py:5` | import | `pydantic.Field` | NO |
| `gpt_researcher/utils/validators.py:14` | call | `Field` | NO |
| `json_schema_generator.py:3` | import | `pydantic.BaseModel` | NO |

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `pydantic` (pypi)
- **Provenance**: Provider `ollama` | Model `llama3.1:8b` | License `LLAMA 3.1 COMMUNITY LICENSE AGREEMENT`
- **API Coverage Gate**: 100%

### Migration Steps
1. Run `pip install pydantic` in the project root.
1. Update import statements to use `from pydantic import BaseModel, Field`.

### Suggested Tests
- Verify that the project still compiles and runs as expected.

### Compatibility Gaps & Open Concerns
- [AI] Potential incompatibility with existing project code if not updated to use new import statements.
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/pydantic_raw_model_response.json` | `6a08fec15b706f894a6029669017b63e27bb8ede212a923a9c4a6f9438061aec` | `ollama run llama3.1:8b` | 2026-10-25T06:51:17.128753+00:00 |
