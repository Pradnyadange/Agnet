# Dependency Exit Capsule: `html5lib`

- **Capsule ID**: `capsule-gpt-researcher-html5lib-20261025_064436`
- **Generated At**: `2026-10-25T06:44:36.330069+00:00`
- **Status**: **NOT_TESTABLE**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'html5lib' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `2315` | [https://pypi.org/pypi/html5lib/json](https://pypi.org/pypi/html5lib/json) | 2026-10-25T06:40:25.357897+00:00 |
| yanked | `False` | [https://pypi.org/pypi/html5lib/json](https://pypi.org/pypi/html5lib/json) | 2026-10-25T06:40:25.357897+00:00 |

### Code Usage (0 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `xmlschema` (pypi)
- **Provenance**: Provider `ollama` | Model `llama3.1:8b` | License `LLAMA 3.1 COMMUNITY LICENSE AGREEMENT`
- **API Coverage Gate**: 100%

### Migration Steps
1. Install xmlschema using pip: `pip install xmlschema`
1. Update your import statements to import from xmlschema instead of html5lib
1. If using html5lib for HTML parsing, consider migrating to a modern parser like lxml or html.parser

### Suggested Tests
- Test that xmlschema correctly parses and validates HTML documents
- Verify that xmlschema does not introduce any regressions or performance issues

### Compatibility Gaps & Open Concerns
- [AI] Potential incompatibility: xmlschema may not support all features and edge cases of html5lib
- [AI] Potential incompatibility: xmlschema may have different performance characteristics compared to html5lib
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/html5lib_raw_model_response.json` | `ceaace709d3e56fd1b591bcf25adc637f574ef9bab7afb57165ea8c2ad9231dd` | `ollama run llama3.1:8b` | 2026-10-25T06:44:36.329985+00:00 |
