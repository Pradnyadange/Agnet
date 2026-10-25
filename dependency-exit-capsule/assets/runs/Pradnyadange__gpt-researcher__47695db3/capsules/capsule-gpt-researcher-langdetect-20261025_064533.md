# Dependency Exit Capsule: `langdetect`

- **Capsule ID**: `capsule-gpt-researcher-langdetect-20261025_064533`
- **Generated At**: `2026-10-25T06:45:33.234090+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'langdetect' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `1996` | [https://pypi.org/pypi/langdetect/json](https://pypi.org/pypi/langdetect/json) | 2026-10-25T06:40:28.712396+00:00 |
| yanked | `False` | [https://pypi.org/pypi/langdetect/json](https://pypi.org/pypi/langdetect/json) | 2026-10-25T06:40:28.712396+00:00 |

### Code Usage (0 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `babel` (pypi)
- **Provenance**: Provider `ollama` | Model `llama3.1:8b` | License `LLAMA 3.1 COMMUNITY LICENSE AGREEMENT`
- **API Coverage Gate**: 100%

### Migration Steps
1. Install Babel using pip: `pip install babel`
1. Update code to use `babel` instead of `langdetect`
1. Update import statements: `import langdetect` becomes `from babel.detection import detect`

### Suggested Tests
- Test language detection with `babel` using the `detect` function
- Verify that language detection works correctly with different languages

### Compatibility Gaps & Open Concerns
- [AI] Potential incompatibility: `langdetect` may not support all languages as well as `babel`
- [AI] Potential incompatibility: `babel` may have slightly different API usage compared to `langdetect`
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/langdetect_raw_model_response.json` | `de073e9586c4b2028ea968494c80301b72d088faed09b20875c4324ec4c3066c` | `ollama run llama3.1:8b` | 2026-10-25T06:45:33.233997+00:00 |
