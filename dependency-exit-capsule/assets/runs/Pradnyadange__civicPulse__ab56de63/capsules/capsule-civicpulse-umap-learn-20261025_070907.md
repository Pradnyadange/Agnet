# Dependency Exit Capsule: `umap-learn`

- **Capsule ID**: `capsule-civicpulse-umap-learn-20261025_070907`
- **Generated At**: `2026-10-25T07:09:07.559392+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `civicPulse` (ab56de6)
- **Maintenance Problem**: Dependency 'umap-learn' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `199` | [https://pypi.org/pypi/umap-learn/json](https://pypi.org/pypi/umap-learn/json) | 2026-10-25T07:07:16.258669+00:00 |
| yanked | `False` | [https://pypi.org/pypi/umap-learn/json](https://pypi.org/pypi/umap-learn/json) | 2026-10-25T07:07:16.258669+00:00 |

### Code Usage (2 locations across 15 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `mongodb/clustering_pipeline.py:10` | import | `umap.umap_` | NO |
| `mongodb/clustering_pipeline.py:67` | call | `UMAP` | NO |

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
| `assets/runs/Pradnyadange__civicPulse__ab56de63/evidence/umap-learn_raw_model_response.json` | `33c69c5957db314da8ca9c6838c6d299617531401c77bef37ba0a94c28204b96` | `ollama run llama3.1:8b` | 2026-10-25T07:09:07.559356+00:00 |
