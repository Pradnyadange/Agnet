# Dependency Exit Capsule: `sgmllib3k`

- **Capsule ID**: `capsule-gpt-researcher-sgmllib3k-20261025_064253`
- **Generated At**: `2026-10-25T06:42:53.796807+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'sgmllib3k' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `5905` | [https://pypi.org/pypi/sgmllib3k/json](https://pypi.org/pypi/sgmllib3k/json) | 2026-10-25T06:40:41.111729+00:00 |
| yanked | `False` | [https://pypi.org/pypi/sgmllib3k/json](https://pypi.org/pypi/sgmllib3k/json) | 2026-10-25T06:40:41.111729+00:00 |

### Code Usage (0 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `tomllib` (stdlib)
- **Provenance**: Provider `ollama` | Model `llama3.1:8b` | License `LLAMA 3.1 COMMUNITY LICENSE AGREEMENT`
- **API Coverage Gate**: 100%

### Migration Steps
1. Update Python to version 3.11 or later to use the built-in tomllib.
1. If running an older version, consider a temporary solution using the `tomli` package.

### Suggested Tests
- Verify that the replacement module can parse and write TOML files correctly.
- Test that the replacement module can handle edge cases, such as malformed TOML files.

### Compatibility Gaps & Open Concerns
- [AI] The `tomllib` module is not available in Python versions prior to 3.11, which may cause compatibility issues.
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/sgmllib3k_raw_model_response.json` | `d19b07309ffb5c093f9378084c138ceebdf27ebf7511bbafcda85b048b512c10` | `ollama run llama3.1:8b` | 2026-10-25T06:42:53.796768+00:00 |
