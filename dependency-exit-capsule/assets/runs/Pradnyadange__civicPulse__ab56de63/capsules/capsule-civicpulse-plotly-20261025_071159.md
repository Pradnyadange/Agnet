# Dependency Exit Capsule: `plotly`

- **Capsule ID**: `capsule-civicpulse-plotly-20261025_071159`
- **Generated At**: `2026-10-25T07:11:59.749383+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `civicPulse` (ab56de6)
- **Maintenance Problem**: Dependency 'plotly' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `39` | [https://pypi.org/pypi/plotly/json](https://pypi.org/pypi/plotly/json) | 2026-10-25T07:07:16.569741+00:00 |
| yanked | `False` | [https://pypi.org/pypi/plotly/json](https://pypi.org/pypi/plotly/json) | 2026-10-25T07:07:16.569741+00:00 |

### Code Usage (4 locations across 15 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `admin_analytics.py:3` | import | `plotly.express` | NO |
| `admin_analytics.py:94` | call | `pie` | NO |
| `admin_analytics.py:101` | call | `pie` | NO |
| `admin_analytics.py:111` | call | `bar` | NO |

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `plotnine` (pypi)
- **Provenance**: Provider `ollama` | Model `llama3.1:8b` | License `LLAMA 3.1 COMMUNITY LICENSE AGREEMENT`
- **API Coverage Gate**: 100%

### Migration Steps
1. Replace all `plotly.express` imports with `plotnine`
1. Update code to use `plotnine`'s `pie` and `bar` functions

### Suggested Tests
- Test `plotnine`'s pie and bar functions with existing data
- Verify the replacement does not introduce new regressions

### Compatibility Gaps & Open Concerns
- [AI] Potential incompatibility: `plotnine` does not have a direct equivalent to `plotly.express`'s functionality, may require code restructuring
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__civicPulse__ab56de63/evidence/plotly_raw_model_response.json` | `ff22c9d6c4c39fc71732cad95c379252e3d55b40f6881a6a8c505013b790622f` | `ollama run llama3.1:8b` | 2026-10-25T07:11:59.749356+00:00 |
