# Dependency Exit Capsule: `toml`

- **Capsule ID**: `capsule-linkwatch-toml-20261025_072948`
- **Generated At**: `2026-10-25T07:29:48.289118+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'toml' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `2184` | [https://pypi.org/pypi/toml/json](https://pypi.org/pypi/toml/json) | 2026-10-25T07:26:06.205079+00:00 |
| yanked | `False` | [https://pypi.org/pypi/toml/json](https://pypi.org/pypi/toml/json) | 2026-10-25T07:26:06.205079+00:00 |

### Code Usage (2 locations across 15 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `linkwatch/config.py:3` | import | `toml` | NO |
| `linkwatch/config.py:37` | call | `load` | NO |

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
1. Remove the `toml` import statement from `linkwatch/config.py`.
1. Replace the `toml.load()` call with `tomllib.loads()` or `tomllib.load()` depending on the exact usage context.
1. Update `setup.py` or `requirements.txt` to reflect the new dependency.

### Suggested Tests
- Run `python -m unittest linkwatch.tests` to ensure the replacement doesn't introduce new test failures.
- Verify that the application still works as expected with the new dependency.

### Compatibility Gaps & Open Concerns
- [AI] Potential incompatibility: If the application uses custom TOML parsing logic, it might not be directly compatible with `tomllib`. In this case, the migration steps may need to be adjusted or additional custom parsing logic implemented.
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/toml_raw_model_response.json` | `166dd1901e8eee6f9678f613890b2b87d6440aab4e931b99c0957836babeeb3d` | `ollama run llama3.1:8b` | 2026-10-25T07:29:48.289090+00:00 |
