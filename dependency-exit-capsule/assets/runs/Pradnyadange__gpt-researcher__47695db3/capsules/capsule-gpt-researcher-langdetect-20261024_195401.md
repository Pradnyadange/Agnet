# Dependency Exit Capsule: `langdetect`

- **Capsule ID**: `capsule-gpt-researcher-langdetect-20261024_195401`
- **Generated At**: `2026-10-24T19:54:01.175915+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'langdetect' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `1996` | [https://pypi.org/pypi/langdetect/json](https://pypi.org/pypi/langdetect/json) | 2026-10-24T19:52:31.592973+00:00 |
| yanked | `False` | [https://pypi.org/pypi/langdetect/json](https://pypi.org/pypi/langdetect/json) | 2026-10-24T19:52:31.592973+00:00 |

### Code Usage (0 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `langdetect` (pypi)
- **Provenance**: Provider `ollama` | Model `gemma2:2b` | License `Gemma Terms of Use `
- **API Coverage Gate**: 100%

### Migration Steps
1. 1. Replace all occurrences of `langdetect` with the `langdetect` package.
1. 2. Ensure the `langdetect` package's API remains consistent with the `langdetect` package's API.

### Suggested Tests
- Verify the accuracy of the detected language using the `langdetect` package and comparing with the output of `langdetect` package.
- Run unit tests for the `langdetect` package to ensure code stability.

### Compatibility Gaps & Open Concerns
- [AI] While the `langdetect` package is a well-maintained alternative, there might be dependencies that require specific versions of this package for functionality. A gap analysis needs to be conducted to identify any such dependencies.
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/langdetect_raw_model_response.json` | `a051f13eec6a7b6fc4a8327cd909feedcb266fc1b310698e8db4e6d0c744c8aa` | `ollama run gemma2:2b` | 2026-10-24T19:54:01.175878+00:00 |
