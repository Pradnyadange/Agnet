# Dependency Exit Capsule: `sgmllib3k`

- **Capsule ID**: `capsule-gpt-researcher-sgmllib3k-20261024_194610`
- **Generated At**: `2026-10-24T19:46:10.178655+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'sgmllib3k' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `5905` | [https://pypi.org/pypi/sgmllib3k/json](https://pypi.org/pypi/sgmllib3k/json) | 2026-10-24T19:45:16.849655+00:00 |
| yanked | `False` | [https://pypi.org/pypi/sgmllib3k/json](https://pypi.org/pypi/sgmllib3k/json) | 2026-10-24T19:45:16.849655+00:00 |

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
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/sgmllib3k_raw_model_response.json` | `02d851d43be1e257b59ba7343f11428943d36f77c34eddae664ce59646005436` | `ollama run gemma2:2b` | 2026-10-24T19:46:10.178628+00:00 |
