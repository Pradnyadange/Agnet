# Dependency Exit Capsule: `htmldocx`

- **Capsule ID**: `capsule-gpt-researcher-htmldocx-20261024_181713`
- **Generated At**: `2026-10-24T18:17:13.201942+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'htmldocx' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `1886` | [https://pypi.org/pypi/htmldocx/json](https://pypi.org/pypi/htmldocx/json) | 2026-10-24T18:13:13.804650+00:00 |
| yanked | `False` | [https://pypi.org/pypi/htmldocx/json](https://pypi.org/pypi/htmldocx/json) | 2026-10-24T18:13:13.804650+00:00 |

### Code Usage (4 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `backend/utils.py:130` | import | `htmldocx.HtmlToDocx` | NO |
| `backend/utils.py:136` | call | `HtmlToDocx` | NO |
| `multi_agents/agents/utils/file_formats.py:85` | import | `htmldocx.HtmlToDocx` | NO |
| `multi_agents/agents/utils/file_formats.py:92` | call | `HtmlToDocx` | NO |

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `python-docx` (pypi)
- **Provenance**: Provider `ollama` | Model `gemma2:2b` | License `Gemma Terms of Use `
- **API Coverage Gate**: 100%

### Migration Steps
1. Update the 'htmldocx.HtmlToDocx' import to use 'python-docx.Document' instead.
1. Update all 'HtmlToDocx' calls to utilize the `python-docx` library.

### Suggested Tests
- Run unit tests to ensure that the new `python-docx` library is used correctly.

### Compatibility Gaps & Open Concerns
- [AI] Ensure that 'python-docx' covers all functionalities of 'htmldocx'. 
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/htmldocx_raw_model_response.json` | `267f9453bc5e84120d543de9232b29aad5600ff9b71675025b0360dbec462bfe` | `ollama run gemma2:2b` | 2026-10-24T18:17:13.201916+00:00 |
