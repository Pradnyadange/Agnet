# Dependency Exit Capsule: `langchain-classic`

- **Capsule ID**: `capsule-gpt-researcher-langchain-classic-20261024_195932`
- **Generated At**: `2026-10-24T19:59:32.778183+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'langchain-classic' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `135` | [https://pypi.org/pypi/langchain-classic/json](https://pypi.org/pypi/langchain-classic/json) | 2026-10-24T19:52:18.875749+00:00 |
| yanked | `False` | [https://pypi.org/pypi/langchain-classic/json](https://pypi.org/pypi/langchain-classic/json) | 2026-10-24T19:52:18.875749+00:00 |

### Code Usage (9 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `gpt_researcher/context/compression.py:21` | import | `langchain_classic.retrievers.ContextualCompressionRetriever` | NO |
| `gpt_researcher/context/compression.py:22` | import | `langchain_classic.retrievers.document_compressors.DocumentCompressorPipeline` | NO |
| `gpt_researcher/context/compression.py:22` | import | `langchain_classic.retrievers.document_compressors.EmbeddingsFilter` | NO |
| `gpt_researcher/context/compression.py:135` | call | `EmbeddingsFilter` | NO |
| `gpt_researcher/context/compression.py:137` | call | `DocumentCompressorPipeline` | NO |
| `gpt_researcher/context/compression.py:143` | call | `ContextualCompressionRetriever` | NO |
| `gpt_researcher/context/compression.py:225` | call | `EmbeddingsFilter` | NO |
| `gpt_researcher/context/compression.py:227` | call | `DocumentCompressorPipeline` | NO |
| `gpt_researcher/context/compression.py:233` | call | `ContextualCompressionRetriever` | NO |

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `no_valid_proposal` (stdlib)
- **Provenance**: Provider `ollama` | Model `gemma2:2b` | License `Gemma Terms of Use `
- **API Coverage Gate**: 0%

### Migration Steps

### Suggested Tests

### Compatibility Gaps & Open Concerns
- [AI] Candidate rejected by validation gate: unknown replacement type
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/langchain-classic_raw_model_response.json` | `eca89dacae6eaef771b1fd73c4a1c7bc147dbfa858fe9cf27530eca85ba97b07` | `ollama run gemma2:2b` | 2026-10-24T19:59:32.778143+00:00 |
