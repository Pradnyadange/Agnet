# Dependency Exit Capsule: `pydantic`

- **Capsule ID**: `capsule-gpt-researcher-pydantic-20261024_195753`
- **Generated At**: `2026-10-24T19:57:53.468973+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'pydantic' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `13` | [https://pypi.org/pypi/pydantic/json](https://pypi.org/pypi/pydantic/json) | 2026-10-24T19:52:18.205346+00:00 |
| yanked | `False` | [https://pypi.org/pypi/pydantic/json](https://pypi.org/pypi/pydantic/json) | 2026-10-24T19:52:18.205346+00:00 |

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
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/pydantic_raw_model_response.json` | `203ecdcabb3a32e594e661354fb3197acfb41199755b62f158cc4d2c8aa56cc3` | `ollama run gemma2:2b` | 2026-10-24T19:57:53.468944+00:00 |
