# Dependency Exit Capsule: `python-dotenv`

- **Capsule ID**: `capsule-gpt-researcher-python-dotenv-20261024_195131`
- **Generated At**: `2026-10-24T19:51:31.260987+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'python-dotenv' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `23` | [https://pypi.org/pypi/python-dotenv/json](https://pypi.org/pypi/python-dotenv/json) | 2026-10-24T19:44:38.632040+00:00 |
| yanked | `False` | [https://pypi.org/pypi/python-dotenv/json](https://pypi.org/pypi/python-dotenv/json) | 2026-10-24T19:44:38.632040+00:00 |

### Code Usage (43 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `cli.py:19` | import | `dotenv.load_dotenv` | NO |
| `cli.py:360` | call | `load_dotenv` | NO |
| `deep_agents/benchmark.py:17` | import | `dotenv.load_dotenv` | NO |
| `deep_agents/benchmark.py:24` | call | `load_dotenv` | NO |
| `deep_agents/breadth_benchmark.py:25` | import | `dotenv.load_dotenv` | NO |
| `deep_agents/breadth_benchmark.py:36` | call | `load_dotenv` | NO |
| `deep_agents/drb_generate.py:12` | import | `dotenv.load_dotenv` | NO |
| `deep_agents/drb_generate.py:25` | call | `load_dotenv` | NO |
| `deep_agents/hybrid_benchmark.py:38` | import | `dotenv.load_dotenv` | NO |
| `deep_agents/hybrid_benchmark.py:51` | call | `load_dotenv` | NO |
| `deep_agents/main.py:1` | import | `dotenv.load_dotenv` | NO |
| `deep_agents/main.py:10` | call | `load_dotenv` | NO |
| `deep_agents/recency_benchmark.py:27` | import | `dotenv.load_dotenv` | NO |
| `deep_agents/recency_benchmark.py:40` | call | `load_dotenv` | NO |
| `deep_agents/report_benchmark.py:27` | import | `dotenv.load_dotenv` | NO |
| `deep_agents/report_benchmark.py:42` | call | `load_dotenv` | NO |
| `evals/hallucination_eval/evaluate.py:8` | import | `dotenv.load_dotenv` | NO |
| `evals/hallucination_eval/run_eval.py:12` | import | `dotenv.load_dotenv` | NO |
| `evals/hallucination_eval/run_eval.py:28` | call | `load_dotenv` | NO |
| `evals/quality_eval/benchmark.py:35` | import | `dotenv.load_dotenv` | NO |
| `evals/quality_eval/benchmark.py:494` | call | `load_dotenv` | NO |
| `evals/quality_eval/run_eval.py:31` | import | `dotenv.load_dotenv` | NO |
| `evals/quality_eval/run_eval.py:71` | call | `load_dotenv` | NO |
| `evals/simple_evals/run_eval.py:16` | import | `dotenv.load_dotenv` | NO |
| `evals/simple_evals/run_eval.py:47` | call | `load_dotenv` | NO |
| `main.py:1` | import | `dotenv.load_dotenv` | NO |
| `main.py:29` | call | `load_dotenv` | NO |
| `multi_agents/ag2/main.py:2` | import | `dotenv.load_dotenv` | NO |
| `multi_agents/ag2/main.py:12` | call | `load_dotenv` | NO |
| `multi_agents/main.py:1` | import | `dotenv.load_dotenv` | NO |
| `multi_agents/main.py:8` | call | `load_dotenv` | NO |
| `tests/documents-report-source.py:6` | import | `dotenv.load_dotenv` | NO |
| `tests/documents-report-source.py:7` | call | `load_dotenv` | NO |
| `tests/test-openai-llm.py:4` | import | `dotenv.load_dotenv` | NO |
| `tests/test-openai-llm.py:5` | call | `load_dotenv` | NO |
| `tests/test-your-embeddings.py:5` | import | `dotenv.load_dotenv` | NO |
| `tests/test-your-embeddings.py:6` | call | `load_dotenv` | NO |
| `tests/test-your-llm.py:4` | import | `dotenv.load_dotenv` | NO |
| `tests/test-your-llm.py:5` | call | `load_dotenv` | NO |
| `tests/test-your-retriever.py:2` | import | `dotenv.load_dotenv` | NO |
| `tests/test-your-retriever.py:8` | call | `load_dotenv` | NO |
| `tests/test_new_agents.py:4` | import | `dotenv.load_dotenv` | NO |
| `tests/test_new_agents.py:24` | call | `load_dotenv` | NO |

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
- [AI] Candidate rejected by validation gate: not in stdlib
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/python-dotenv_raw_model_response.json` | `3ce80121197c391b8d124dcaf7c39af1c7e68ee286ae3afa2fe75b52530702b4` | `ollama run gemma2:2b` | 2026-10-24T19:51:31.260954+00:00 |
