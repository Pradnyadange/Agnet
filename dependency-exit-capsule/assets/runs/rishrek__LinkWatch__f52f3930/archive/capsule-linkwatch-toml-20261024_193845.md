# Dependency Exit Capsule: `toml`

- **Capsule ID**: `capsule-linkwatch-toml-20261024_193845`
- **Generated At**: `2026-10-24T19:38:45.693340+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'toml' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `2183` | [https://pypi.org/pypi/toml/json](https://pypi.org/pypi/toml/json) | 2026-10-24T19:35:37.886272+00:00 |
| yanked | `False` | [https://pypi.org/pypi/toml/json](https://pypi.org/pypi/toml/json) | 2026-10-24T19:35:37.886272+00:00 |

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
- **Proposed Replacement**: `no_valid_proposal` (stdlib)
- **Provenance**: Provider `ollama` | Model `llama3.1:8b` | License `LLAMA 3.1 COMMUNITY LICENSE AGREEMENT`
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
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/toml_raw_model_response.json` | `1476868b122d729b05e6ae516b6434baaa651155974b9fdc67be6699aab34701` | `ollama run llama3.1:8b` | 2026-10-24T19:38:45.693324+00:00 |
