# Dependency Exit Capsule: `html5lib`

- **Capsule ID**: `capsule-gpt-researcher-html5lib-20261024_194702`
- **Generated At**: `2026-10-24T19:47:03.007043+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'html5lib' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `2314` | [https://pypi.org/pypi/html5lib/json](https://pypi.org/pypi/html5lib/json) | 2026-10-24T19:45:01.444624+00:00 |
| yanked | `False` | [https://pypi.org/pypi/html5lib/json](https://pypi.org/pypi/html5lib/json) | 2026-10-24T19:45:01.444624+00:00 |

### Code Usage (0 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `pyparsing` (pypi)
- **Provenance**: Provider `ollama` | Model `gemma2:2b` | License `Gemma Terms of Use `
- **API Coverage Gate**: 100%

### Migration Steps
1. Update the 'html5lib' dependency to use `pyparsing` instead of `html5lib`. This will require restructuring of the code to use the `pyparsing` module.
1. Validate that the migrated code works as expected and does not introduce any new vulnerabilities or performance regressions.

### Suggested Tests
- Test the functionality of the application to ensure that the migration has not negatively affected its performance or security.
- Run unit tests and integration tests to ensure the migrated code is working as expected.

### Compatibility Gaps & Open Concerns
- [AI] Potential incompatibility: The migration requires updating the `html5lib` dependency to use `pyparsing`. This may lead to potential incompatibilities with existing code.
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/html5lib_raw_model_response.json` | `d56cd1808340c7f97cf267be0e37306e0b0cd539d43d21d28b30b47e380e95ac` | `ollama run gemma2:2b` | 2026-10-24T19:47:03.007016+00:00 |
