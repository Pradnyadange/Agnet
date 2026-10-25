# Dependency Exit Capsule: `toml`

- **Capsule ID**: `capsule-linkwatch-toml-20261024_201229`
- **Generated At**: `2026-10-24T20:12:29.635328+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'toml' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `2183` | [https://pypi.org/pypi/toml/json](https://pypi.org/pypi/toml/json) | 2026-10-24T20:09:07.748601+00:00 |
| yanked | `False` | [https://pypi.org/pypi/toml/json](https://pypi.org/pypi/toml/json) | 2026-10-24T20:09:07.748601+00:00 |

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
1. Update import statements in linkwatch/config.py to import from tomllib instead of toml
1. Replace toml.load() calls in linkwatch/config.py with tomllib.load()

### Suggested Tests
- Test config loading with various toml files and validate output
- Verify config updates are reflected correctly after modification

### Compatibility Gaps & Open Concerns
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/toml_raw_model_response.json` | `f4b8e00480155683dc73f73321812f6f89d30933da2c73e60ab83175be7a3de2` | `ollama run llama3.1:8b` | 2026-10-24T20:12:29.634948+00:00 |
