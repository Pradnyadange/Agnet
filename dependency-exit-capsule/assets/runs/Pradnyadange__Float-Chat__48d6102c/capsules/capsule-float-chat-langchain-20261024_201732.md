# Dependency Exit Capsule: `langchain`

- **Capsule ID**: `capsule-float-chat-langchain-20261024_201732`
- **Generated At**: `2026-10-24T20:17:32.608790+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `Float-Chat` (48d6102)
- **Maintenance Problem**: Dependency 'langchain' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `2` | [https://pypi.org/pypi/langchain/json](https://pypi.org/pypi/langchain/json) | 2026-10-24T20:13:23.484817+00:00 |
| yanked | `False` | [https://pypi.org/pypi/langchain/json](https://pypi.org/pypi/langchain/json) | 2026-10-24T20:13:23.484817+00:00 |

### Code Usage (4 locations across 6 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `src/helpers.py:2` | import | `langchain.text_splitter.RecursiveCharacterTextSplitter` | NO |
| `src/helpers.py:6` | import | `langchain.schema.Document` | NO |
| `src/helpers.py:24` | call | `Document` | NO |
| `src/helpers.py:33` | call | `RecursiveCharacterTextSplitter` | NO |

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
- [AI] Candidate rejected by validation gate: API coverage below 100% (0%)
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__Float-Chat__48d6102c/evidence/langchain_raw_model_response.json` | `6c92b83cdd461b1f4fe4a97a2407cdae38cff72d2ace044648e6954bc0005060` | `ollama run llama3.2:3b` | 2026-10-24T20:17:32.608749+00:00 |
