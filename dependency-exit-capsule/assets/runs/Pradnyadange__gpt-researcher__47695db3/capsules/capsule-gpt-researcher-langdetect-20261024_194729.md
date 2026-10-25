# Dependency Exit Capsule: `langdetect`

- **Capsule ID**: `capsule-gpt-researcher-langdetect-20261024_194729`
- **Generated At**: `2026-10-24T19:47:29.967124+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'langdetect' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `1996` | [https://pypi.org/pypi/langdetect/json](https://pypi.org/pypi/langdetect/json) | 2026-10-24T19:45:05.182073+00:00 |
| yanked | `False` | [https://pypi.org/pypi/langdetect/json](https://pypi.org/pypi/langdetect/json) | 2026-10-24T19:45:05.182073+00:00 |

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
1. 1. Update dependencies to `langdetect` (with the new version):  `pip install langdetect`
1. 2. Verify functionality: Test the new version by using it in your application.
1. 3.  Document the change:  Update the README with details of the migration and the new version.

### Suggested Tests
- Verify that the code in the application works correctly with the updated `langdetect` version.
- Test different languages and environments (e.g., API, web, or CLI).

### Compatibility Gaps & Open Concerns
- [AI] Potential incompatibility issues might arise if the new version does not fully replace the original functionality or have a different API.
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/langdetect_raw_model_response.json` | `78ea3a1c971100fd904b9658c14c20c10003faa2f0c77b8c12d355071692eee7` | `ollama run gemma2:2b` | 2026-10-24T19:47:29.967087+00:00 |
