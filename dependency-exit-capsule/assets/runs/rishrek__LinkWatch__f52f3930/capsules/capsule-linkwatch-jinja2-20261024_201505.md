# Dependency Exit Capsule: `jinja2`

- **Capsule ID**: `capsule-linkwatch-jinja2-20261024_201505`
- **Generated At**: `2026-10-24T20:15:05.954889+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `LinkWatch` (f52f393)
- **Maintenance Problem**: Dependency 'jinja2' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `598` | [https://pypi.org/pypi/jinja2/json](https://pypi.org/pypi/jinja2/json) | 2026-10-24T20:09:08.265862+00:00 |
| yanked | `False` | [https://pypi.org/pypi/jinja2/json](https://pypi.org/pypi/jinja2/json) | 2026-10-24T20:09:08.265862+00:00 |

### Code Usage (6 locations across 15 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `linkwatch/report.py:3` | import | `jinja2.Environment` | NO |
| `linkwatch/report.py:3` | import | `jinja2.FileSystemLoader` | NO |
| `linkwatch/report.py:3` | import | `jinja2.select_autoescape` | NO |
| `linkwatch/report.py:9` | call | `Environment` | NO |
| `linkwatch/report.py:10` | call | `FileSystemLoader` | NO |
| `linkwatch/report.py:11` | call | `select_autoescape` | NO |

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
| `assets/runs/rishrek__LinkWatch__f52f3930/evidence/jinja2_raw_model_response.json` | `e0edcbc2f313c897a45a75892ec6095b1205408291ae0119f021222b48529d00` | `ollama run llama3.1:8b` | 2026-10-24T20:15:05.954826+00:00 |
