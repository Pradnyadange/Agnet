# Dependency Exit Capsule: `sentence-transformers`

- **Capsule ID**: `capsule-float-chat-sentence-transformers-20261024_201750`
- **Generated At**: `2026-10-24T20:17:50.240786+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `Float-Chat` (48d6102)
- **Maintenance Problem**: Dependency 'sentence-transformers' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `3` | [https://pypi.org/pypi/sentence-transformers/json](https://pypi.org/pypi/sentence-transformers/json) | 2026-10-24T20:13:23.938833+00:00 |
| yanked | `False` | [https://pypi.org/pypi/sentence-transformers/json](https://pypi.org/pypi/sentence-transformers/json) | 2026-10-24T20:13:23.938833+00:00 |

### Code Usage (0 locations across 6 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `sentence-transformers` (pypi)
- **Provenance**: Provider `ollama` | Model `llama3.2:3b` | License `LLAMA 3.2 COMMUNITY LICENSE AGREEMENT`
- **API Coverage Gate**: 100%

### Migration Steps
1. Update existing dependencies to use sentence-transformers

### Suggested Tests
- Test model functionality with sentence-transformers

### Compatibility Gaps & Open Concerns
- [AI] Verify compatibility with Python 3.14.6
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__Float-Chat__48d6102c/evidence/sentence-transformers_raw_model_response.json` | `1eb68c9ab4ff255547da13d503644f047095d788fa47eaa5d8420f946345d7d4` | `ollama run llama3.2:3b` | 2026-10-24T20:17:50.240746+00:00 |
