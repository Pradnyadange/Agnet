# Dependency Exit Capsule: `langchain-community`

- **Capsule ID**: `capsule-float-chat-langchain-community-20261024_201706`
- **Generated At**: `2026-10-24T20:17:06.714840+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `Float-Chat` (48d6102)
- **Maintenance Problem**: Dependency 'langchain-community' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `155` | [https://pypi.org/pypi/langchain-community/json](https://pypi.org/pypi/langchain-community/json) | 2026-10-24T20:13:25.235525+00:00 |
| yanked | `False` | [https://pypi.org/pypi/langchain-community/json](https://pypi.org/pypi/langchain-community/json) | 2026-10-24T20:13:25.235525+00:00 |

### Code Usage (5 locations across 6 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `src/helpers.py:1` | import | `langchain_community.document_loaders.DirectoryLoader` | NO |
| `src/helpers.py:1` | import | `langchain_community.document_loaders.PyPDFLoader` | NO |
| `src/helpers.py:3` | import | `langchain_community.embeddings.HuggingFaceEmbeddings` | NO |
| `src/helpers.py:10` | call | `DirectoryLoader` | NO |
| `src/helpers.py:43` | call | `HuggingFaceEmbeddings` | NO |

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
| `assets/runs/Pradnyadange__Float-Chat__48d6102c/evidence/langchain-community_raw_model_response.json` | `a059fa7563cc26f1c98e62867a84e1b6c3cd9e67e32e62d9dcccbf12e953f522` | `ollama run llama3.2:3b` | 2026-10-24T20:17:06.714814+00:00 |
