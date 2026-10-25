# Dependency Exit Capsule: `nose`

- **Capsule ID**: `capsule-linkwatch-nose-20261024_202209`
- **Generated At**: `2026-10-24T20:22:09.708324+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'nose' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `4162` | [https://pypi.org/pypi/nose/json](https://pypi.org/pypi/nose/json) | 2026-10-24T20:21:51.543484+00:00 |
| yanked | `False` | [https://pypi.org/pypi/nose/json](https://pypi.org/pypi/nose/json) | 2026-10-24T20:21:51.543484+00:00 |

### Code Usage (0 locations across 15 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|

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
- [AI] Candidate rejected by validation gate: not in stdlib
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/nose_raw_model_response.json` | `ea083864b44f09cb1119e03b914e637d5fa67da7b9f1c7c6cd8aae30626ff114` | `ollama run llama3.2:3b` | 2026-10-24T20:22:09.708284+00:00 |
