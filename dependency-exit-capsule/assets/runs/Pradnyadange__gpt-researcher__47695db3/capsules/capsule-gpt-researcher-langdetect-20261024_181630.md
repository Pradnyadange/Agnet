# Dependency Exit Capsule: `langdetect`

- **Capsule ID**: `capsule-gpt-researcher-langdetect-20261024_181630`
- **Generated At**: `2026-10-24T18:16:30.836985+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'langdetect' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `1996` | [https://pypi.org/pypi/langdetect/json](https://pypi.org/pypi/langdetect/json) | 2026-10-24T18:13:31.397864+00:00 |
| yanked | `False` | [https://pypi.org/pypi/langdetect/json](https://pypi.org/pypi/langdetect/json) | 2026-10-24T18:13:31.397864+00:00 |

### Code Usage (0 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|

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
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/langdetect_raw_model_response.json` | `e91c80d12688e1a4ae970d00a9e01c1ece3bc4cde4bd0c968886da16df18ba29` | `ollama run gemma2:2b` | 2026-10-24T18:16:30.836958+00:00 |
