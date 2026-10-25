# Dependency Exit Capsule: `appdirs`

- **Capsule ID**: `capsule-linkwatch-appdirs-20261024_202242`
- **Generated At**: `2026-10-24T20:22:42.113874+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'appdirs' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `2357` | [https://pypi.org/pypi/appdirs/json](https://pypi.org/pypi/appdirs/json) | 2026-10-24T20:21:51.658592+00:00 |
| yanked | `False` | [https://pypi.org/pypi/appdirs/json](https://pypi.org/pypi/appdirs/json) | 2026-10-24T20:21:51.658592+00:00 |

### Code Usage (2 locations across 15 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `linkwatch/cache.py:4` | import | `appdirs.user_cache_dir` | NO |
| `linkwatch/cache.py:10` | call | `user_cache_dir` | NO |

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
- [AI] Candidate rejected by validation gate: API coverage below 100% (0%)
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/appdirs_raw_model_response.json` | `681809c0689146752ac44ab42173b70c3be7fd25b057ef0420c637d919a352a9` | `ollama run llama3.2:3b` | 2026-10-24T20:22:42.113836+00:00 |
