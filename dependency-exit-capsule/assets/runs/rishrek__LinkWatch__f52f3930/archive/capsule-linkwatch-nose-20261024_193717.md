# Dependency Exit Capsule: `nose`

- **Capsule ID**: `capsule-linkwatch-nose-20261024_193717`
- **Generated At**: `2026-10-24T19:37:17.578357+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'nose' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `4162` | [https://pypi.org/pypi/nose/json](https://pypi.org/pypi/nose/json) | 2026-10-24T19:35:37.626655+00:00 |
| yanked | `False` | [https://pypi.org/pypi/nose/json](https://pypi.org/pypi/nose/json) | 2026-10-24T19:35:37.626655+00:00 |

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
1. Remove nose from the project dependencies.
1. Update the project's test runner to use the unittest module.

### Suggested Tests
- Test the project's tests with the unittest test runner.
- Verify that the project's functionality is not affected by the removal of nose.

### Compatibility Gaps & Open Concerns
- [AI] nose is an older testing framework that may have incompatibilities with the current Python version.
- [AI] The unittest module is the built-in testing framework for Python and is actively maintained.
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/nose_raw_model_response.json` | `f2e91cacf71d85351a64eb6a8781de7a4a616d403acc35b323eb7a7a2e58536f` | `ollama run llama3.1:8b` | 2026-10-24T19:37:17.578334+00:00 |
