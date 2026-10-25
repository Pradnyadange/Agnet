# Dependency Exit Capsule: `sgmllib3k`

- **Capsule ID**: `capsule-gpt-researcher-sgmllib3k-20261024_181454`
- **Generated At**: `2026-10-24T18:14:54.075122+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'sgmllib3k' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `5905` | [https://pypi.org/pypi/sgmllib3k/json](https://pypi.org/pypi/sgmllib3k/json) | 2026-10-24T18:13:44.856917+00:00 |
| yanked | `False` | [https://pypi.org/pypi/sgmllib3k/json](https://pypi.org/pypi/sgmllib3k/json) | 2026-10-24T18:13:44.856917+00:00 |

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
- [AI] Candidate rejected by validation gate: unknown replacement type
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/sgmllib3k_raw_model_response.json` | `cfd497a72cc8aee11a2bdd8946e6f0e178da4140b81c48a9d152a64cc7ab6c96` | `ollama run gemma2:2b` | 2026-10-24T18:14:54.075108+00:00 |
