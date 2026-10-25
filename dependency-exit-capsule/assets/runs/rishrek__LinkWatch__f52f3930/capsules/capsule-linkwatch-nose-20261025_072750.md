# Dependency Exit Capsule: `nose`

- **Capsule ID**: `capsule-linkwatch-nose-20261025_072750`
- **Generated At**: `2026-10-25T07:27:50.259675+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'nose' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `4162` | [https://pypi.org/pypi/nose/json](https://pypi.org/pypi/nose/json) | 2026-10-25T07:26:05.925243+00:00 |
| yanked | `False` | [https://pypi.org/pypi/nose/json](https://pypi.org/pypi/nose/json) | 2026-10-25T07:26:05.925243+00:00 |

### Code Usage (0 locations across 15 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `unittest` (stdlib)
- **Provenance**: Provider `ollama` | Model `llama3.1:8b` | License `LLAMA 3.1 COMMUNITY LICENSE AGREEMENT`
- **API Coverage Gate**: 100%

### Migration Steps
1. Update tests to use unittest framework instead of nose.
1. Remove nose dependencies and install unittest using pip.

### Suggested Tests
- Verify tests run without errors using unittest framework.
- Check for any regressions in test coverage.

### Compatibility Gaps & Open Concerns
- [AI] Since unittest is a standard library module, it should be more secure and maintainable than nose.
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/nose_raw_model_response.json` | `c8b442e93059236bbd8d28eefbc300a85520d1f5fffddfdd16328b3e66869158` | `ollama run llama3.1:8b` | 2026-10-25T07:27:50.259589+00:00 |
