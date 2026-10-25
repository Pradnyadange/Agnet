# Dependency Exit Capsule: `rich`

- **Capsule ID**: `capsule-linkwatch-rich-20261024_201644`
- **Generated At**: `2026-10-24T20:16:44.740381+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'rich' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `195` | [https://pypi.org/pypi/rich/json](https://pypi.org/pypi/rich/json) | 2026-10-24T20:09:09.771730+00:00 |
| yanked | `False` | [https://pypi.org/pypi/rich/json](https://pypi.org/pypi/rich/json) | 2026-10-24T20:09:09.771730+00:00 |

### Code Usage (6 locations across 15 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `linkwatch/cli.py:2` | import | `rich.console.Console` | NO |
| `linkwatch/cli.py:3` | import | `rich.live.Live` | NO |
| `linkwatch/cli.py:4` | import | `rich.table.Table` | NO |
| `linkwatch/cli.py:9` | call | `Console` | NO |
| `linkwatch/cli.py:13` | call | `Table` | NO |
| `linkwatch/cli.py:40` | call | `Live` | NO |

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
- [AI] Candidate rejected by validation gate: API coverage below 100% (0%)
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/rich_raw_model_response.json` | `2e699c3f26c51c92b5209c5d67fc1305380f18eda96b8d237dbcbc23f01693e5` | `ollama run llama3.1:8b` | 2026-10-24T20:16:44.740355+00:00 |
