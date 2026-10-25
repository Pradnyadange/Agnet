# Dependency Exit Capsule: `langchain`

- **Capsule ID**: `capsule-gpt-researcher-langchain-20261024_195856`
- **Generated At**: `2026-10-24T19:58:56.530211+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'langchain' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `2` | [https://pypi.org/pypi/langchain/json](https://pypi.org/pypi/langchain/json) | 2026-10-24T19:52:18.775059+00:00 |
| yanked | `False` | [https://pypi.org/pypi/langchain/json](https://pypi.org/pypi/langchain/json) | 2026-10-24T19:52:18.775059+00:00 |

### Code Usage (2 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `tests/vector-store.py:6` | import | `langchain.text_splitter.CharacterTextSplitter` | NO |
| `tests/vector-store.py:104` | call | `CharacterTextSplitter` | NO |

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
- [AI] Candidate rejected by validation gate: package does not exist on PyPI
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/langchain_raw_model_response.json` | `57801ace739fef2cd29f513975f172195b95d23f0431effd52cfa5c2c8bbead2` | `ollama run gemma2:2b` | 2026-10-24T19:58:56.530188+00:00 |
