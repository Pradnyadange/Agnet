# Dependency Exit Capsule: `docopt`

- **Capsule ID**: `capsule-gpt-researcher-docopt-20261024_195318`
- **Generated At**: `2026-10-24T19:53:18.478086+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'docopt' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `4513` | [https://pypi.org/pypi/docopt/json](https://pypi.org/pypi/docopt/json) | 2026-10-24T19:52:27.388727+00:00 |
| yanked | `False` | [https://pypi.org/pypi/docopt/json](https://pypi.org/pypi/docopt/json) | 2026-10-24T19:52:27.388727+00:00 |

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
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/docopt_raw_model_response.json` | `27a213a5f0b7686d7cfa3901a1b50d06cd7038fecf840b19a7b873a0218766dc` | `ollama run gemma2:2b` | 2026-10-24T19:53:18.478060+00:00 |
