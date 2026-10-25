# Dependency Exit Capsule: `python-magic`

- **Capsule ID**: `capsule-gpt-researcher-python-magic-20261024_181738`
- **Generated At**: `2026-10-24T18:17:38.288514+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'python-magic' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `1599` | [https://pypi.org/pypi/python-magic/json](https://pypi.org/pypi/python-magic/json) | 2026-10-24T18:13:41.818159+00:00 |
| yanked | `False` | [https://pypi.org/pypi/python-magic/json](https://pypi.org/pypi/python-magic/json) | 2026-10-24T18:13:41.818159+00:00 |

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
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/python-magic_raw_model_response.json` | `8d1f9db1d1c4174af61dad66f9e4916774d0e83be5697e7a986c2c13c932c0df` | `ollama run gemma2:2b` | 2026-10-24T18:17:38.288462+00:00 |
