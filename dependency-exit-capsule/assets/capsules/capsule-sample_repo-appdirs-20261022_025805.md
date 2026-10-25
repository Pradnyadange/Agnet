# Dependency Exit Capsule: `appdirs`

- **Capsule ID**: `capsule-sample_repo-appdirs-20261022_025805`
- **Generated At**: `2026-10-22T02:58:05.743131+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `sample_repo` (a1b2c3d)
- **Maintenance Problem**: Dependency appdirs shows high staleness risk indicators and should be replaced with modern supported alternative.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `2354` | [https://pypi.org/pypi/appdirs/json](https://pypi.org/pypi/appdirs/json) | 2026-10-22T02:53:50.715232+00:00 |
| yanked | `False` | [https://pypi.org/pypi/appdirs/json](https://pypi.org/pypi/appdirs/json) | 2026-10-22T02:53:50.715232+00:00 |

### Code Usage (0 locations across 2 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|

### Test Results Diff
- **Baseline**: 1 passed, 0 failed
- **Candidate**: 1 passed, 0 failed
- **New Failures**: 0
- **pip check**: No broken requirements found.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `platformdirs` (pypi)
- **Provenance**: Provider `rule_based_knowledge_base` | Model `none` | License `N/A`
- **API Coverage Gate**: 100%

### Migration Steps
1. Replace 'appdirs' with 'platformdirs' in requirements.txt
1. Update import statements from 'import appdirs' to 'import platformdirs as appdirs' or rename usages to 'platformdirs'
1. Verify directory paths match platform standard directories

### Suggested Tests
- Validate user_cache_dir returns identical or standard OS path
- Check compatibility of custom appname arguments

### Compatibility Gaps & Open Concerns
- [AI] platformdirs is actively maintained; minor differences in macOS path resolution for specific system flags
- [OBSERVED] Results only cover what the repo's tests exercise.
- [OBSERVED] Python only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/evidence/capsule-appdirs/baseline_pip_check.txt` | `9bc9eff87ccde9a897a86ea3cf9096facadba3cc998bc2b74cc3d856cf1cc971` | `pip check` | 2026-10-22T02:58:05.743131+00:00 |
| `assets/evidence/capsule-appdirs/candidate_pip_check.txt` | `9bc9eff87ccde9a897a86ea3cf9096facadba3cc998bc2b74cc3d856cf1cc971` | `pip check` | 2026-10-22T02:58:05.743131+00:00 |
| `assets/evidence/capsule-appdirs/baseline_junit.xml` | `72955b7026730e7be312bbbc8a450865cb6747ee11f26dfc4d8174f6c3fe3cb0` | `pytest` | 2026-10-22T02:58:05.743131+00:00 |
| `assets/evidence/capsule-appdirs/candidate_junit.xml` | `7ad1d7592b7cda79aa8d3996e7be38e6cff5c968758b0e6f23bec1de5140e3c5` | `pytest` | 2026-10-22T02:58:05.743131+00:00 |
| `assets/evidence/capsule-appdirs/baseline_coverage.json` | `a6870988b0253a93b1aa3117c83eba2d6511ee6944022ef47b7031c1a19db9d5` | `llm-response` | 2026-10-22T02:58:05.743131+00:00 |
| `assets/evidence/capsule-appdirs/candidate_coverage.json` | `57185a5ee00333a3beeb97fd5ae6ab5c4ddbe9284a1c5130152dc288f28696cb` | `llm-response` | 2026-10-22T02:58:05.743131+00:00 |
| `assets/evidence/capsule-appdirs/baseline_pytest_output.txt` | `16ab1d4a41814ce08a723abe76a488712a3ba3785bc9508a42f3a13743414d2d` | `pytest` | 2026-10-22T02:58:05.743131+00:00 |
| `assets/evidence/capsule-appdirs/candidate_pytest_output.txt` | `ab2873d127a804b64bcfd25395b387f23c7a0c57cfea43d5bf9f489a29499a83` | `pytest` | 2026-10-22T02:58:05.743131+00:00 |
