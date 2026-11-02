# Dependency Exit Capsule

**Hackathon Track 2 (Maintenance Agent Skill) | Repository: H26_Softerror_TrustLedger | Primary test target: [LinkWatch](https://github.com/rishrek/LinkWatch)**

A reusable Agent Skill (plus a local viewer) that helps a maintainer prepare to stop using a risky dependency. It finds dependencies that look risky, shows exactly where they are used, asks an open-weight model for a suggestion, checks that suggestion with automated gates, and (for repositories you trust) runs the repo's own tests with the old and the new version. Everything is written to a **Dependency Exit Capsule** that keeps what was **observed** apart from what the **AI suggested**.

> The model suggests. Scripts and test runs decide. Anything the AI wrote is labelled AI-GENERATED and is never counted as proof.

**Reading this README:** items tagged **(Phase 2)** describe the second round of work. They are listed as *pending verification* in [Implementation status](#implementation-status) until a recorded run and tests exist for them.

## Contents

- [How it works](#how-it-works)
- [Observed vs AI-generated](#observed-vs-ai-generated)
- [Dependency actions (Phase 2)](#dependency-actions-phase-2)
- [Capsule statuses](#capsule-statuses)
- [Implementation status](#implementation-status)
- [Results on LinkWatch](#results-on-linkwatch)
- [Quick start](#quick-start)
- [Viewer](#viewer)
- [Analyzing other repositories](#analyzing-other-repositories)
- [Run folders, labels and large repositories (Phase 2)](#run-folders-labels-and-large-repositories-phase-2)
- [Models, access, license and privacy](#models-access-license-and-privacy)
- [Limitations](#limitations)
- [Repository layout](#repository-layout)
- [License and third-party notices](#license-and-third-party-notices)

## How it works

```
Target repo (never modified)
   |
   v
fetch_repo.py ----------> shallow clone or ZIP, strict validation, size limits
parse_dependencies.py --> requirements*.txt, pyproject.toml, setup.cfg
scan_risk.py -----------> risk indicators from PyPI (GitHub optional)      [observed]
import_mapper.py -------> import names for each package (from its wheel)   [observed]
map_usage.py -----------> imports and call sites with file:line (ast)      [observed]
(Phase 2) action step --> replace / upgrade / remove / no_action           [observed data + policy file]
propose_replacement.py -> model proposal + validation gates                [AI-generated, then checked]
run_diff_tests.py ------> baseline vs candidate tests (tested mode)        [observed]
build_capsule.py -------> schema-validated capsule JSON + Markdown         [both, kept separate]
verify_capsule.py ------> SHA-256 manifest check                           [observed]
   |
   v
assets/runs/<owner>__<repo>__<sha>/  -->  Viewer (reads files only)
```

`run_pipeline.py` orchestrates these steps and streams progress as JSON lines.

### Validation gates applied to every model proposal

- Standard-library candidates are checked against `sys.stdlib_module_names`.
- PyPI candidates must exist on PyPI.
- **API coverage:** the candidate must provide the symbols the repo actually uses (for example `user_cache_dir`). A candidate that lacks one is rejected.
- **Replacement trust check:** first release date, release count, project links and name similarity to popular packages are recorded, and weak candidates are flagged for human review.
- **(Phase 2) Python-version gate:** a candidate's minimum Python version is compared with the target's `requires-python` and classifiers. For example, `tomllib` needs Python 3.11 or newer, so it is marked incompatible for a project that supports older versions. Minimum versions for standard-library modules come from a labelled data file; PyPI candidates use `requires_python` from PyPI.
- Repository text (README, comments, code) is treated as untrusted data in prompts. Model output is only parsed as JSON and checked by the gates; nothing the model returns is executed.
- Common secret patterns are redacted before any text is put into a prompt.

If no candidate passes, the capsule says `no_valid_proposal`. The tool never invents one.

## Observed vs AI-generated

| Kind | Examples | Source | Label |
|---|---|---|---|
| Observed | Release dates, usage locations, test counts, `pip check`, coverage, file hashes | PyPI/GitHub APIs, `ast`, pytest junit XML, command output | OBSERVED |
| AI-generated | Replacement choice, migration steps, suggested tests, gap explanations | Open-weight model, saved with prompt hash and raw response | AI-GENERATED |
| Rule-based | Offline fallback suggestions from a data file | `references/known_migrations.json`, only with `--offline` | RULE-BASED |

Each capsule records its provenance: provider, model ID, license name and text hash (read from the model server, never guessed from the model name), prompt hash, and the path of the raw response.

## Dependency actions (Phase 2)

Not every old dependency should be replaced. Before any model call, each dependency gets one action decided from observed data. Thresholds live in `references/risk_policy.json` (policy data, shown in the viewer's About tab), not in code.

| Action | When |
|---|---|
| `replace` | Archived flag, deprecation text in the PyPI description or README, or a very long time since the latest release |
| `upgrade` | Healthy, but the pinned version is many releases behind the latest |
| `remove` | No usage in Python files, no reference in non-Python files (Makefile, `tox.ini`, `setup.cfg`, CI workflows, docs), and not required by another declared dependency |
| `no_action` | Healthy and current |

- The model is called only for `replace` and `upgrade`.
- Test frameworks and developer tools are not proposed for replacement unless archived or deprecated.
- Each capsule records the dependency's scope (runtime or dev), `required_by` (from the other dependencies' `requires_dist` on PyPI) and any non-Python references found.
- "Days since latest release" and "versions behind latest" are indicators, not proof that a project is abandoned.

## Capsule statuses

| Status | Meaning |
|---|---|
| `verified` | Tests ran: baseline and candidate pass, no new failures, `pip check` clean, API coverage complete, every changed call site covered by a passing test |
| `unverified` | Tests ran and pass, but some changed call sites are not covered or API coverage is incomplete |
| `not_run` | Tests were not executed (for example static analysis of an external repository) |
| `not_testable` | Tests cannot be installed or run, or cannot exercise the change |
| `no_valid_proposal` | Every candidate was rejected by the gates |
| `failed` | The change introduced new test failures or broke `pip check` |

`verified` always means "verified for the repository's existing tests, in a copy, on the recorded OS and Python version". The original repository is never modified.

**(Phase 2) Status reasons.** Every capsule carries a machine-readable `status_reason`, shown next to the badge: `tests_not_executed`, `gate_rejected`, `no_usage_found`, `required_by_other_dependency`, `healthy_no_action`, `not_on_pypi`, `tests_cannot_exercise_change`, `coverage_incomplete`.

**(Phase 2) Static runs** pass "tests not executed" to the status rules, so they produce `not_run` or `no_valid_proposal`, never `unverified`, `not_testable`, `verified` or `failed`.

### Showing failures (Phase 2)

A tool that never says no is not trustworthy, so rejections are shown as first-class evidence:

- **Rejected by tests:** every tested candidate is stored in the capsule's `candidate_results` (change, install result, `pip check`, junit counts, evidence paths, whether it was chosen). The model's own `MarkupSafe` proposal from the LinkWatch run appears here with its failing test.
- **Rejected by the gate:** proposals the gate refused (for example `pathlib` for `appdirs`), with the missing symbol and the run number.
- **Negative-control fixture:** `tests/fixtures/sample_repo_breaking/` contains a plausible replacement that really breaks a test, so the pipeline can produce a `failed` capsule from a real junit result. It is labelled **"fixture demo"** and is kept out of LinkWatch counts.

The Overview shows three separate cards (capsules failed, candidates rejected by tests, proposals rejected by the gate) plus a count for every status that sums to the number of capsules.

## Implementation status

| Capability | Status |
|---|---|
| Risk scan from live PyPI data (GitHub optional) | Working |
| `ast` usage mapping with `file:line`; wheel-based import-name resolution | Working |
| Model proposals with explicit `--model-id`; license read from the model server | Working |
| Validation gates: stdlib, PyPI existence, API coverage, replacement trust check | Working |
| Structured edits `{file, old_text, new_text}` with boundary check | Working |
| Baseline-first differential tests, junit parsing, `pip check`, coverage | Working |
| Capsule schema validation; provenance and evidence enforcement | Working |
| SHA-256 integrity manifest and `verify_capsule.py` | Working |
| Viewer tabs: Analyze, Overview, Capsule, Blast radius, Test proof, Integrity, About | Working |
| GitHub URL and ZIP intake in static mode | Working |
| (Phase 2) Static runs produce `not_run` / `no_valid_proposal`; status reasons | Pending verification |
| (Phase 2) One capsule per dependency per run; older copies archived | Pending verification |
| (Phase 2) Action step (replace, upgrade, remove, no action) and `risk_policy.json` | Pending verification |
| (Phase 2) Non-Python reference scan and `required_by` check before `remove` | Pending verification |
| (Phase 2) Python-version compatibility gate | Pending verification |
| (Phase 2) Rejected-by-tests and rejected-by-gate tables; `failed` fixture demo | Pending verification |
| (Phase 2) `run.json` metadata, run labels in UTC, corrected run summary | Pending verification |
| (Phase 2) "Analyze all dependencies", time estimate, resume and stop | Pending verification |
| Running an external repository's tests in a Docker sandbox | Not built |
| Equivalence checks of old vs new library outputs | Not built |
| Non-Python ecosystems | Not built |
| Auto-merge or pull-request creation | Not built |
| Signed capsules (hashes only) | Not built |

The tool's own test suite last ran at 25 passed (`python -m pytest -q`) before Phase 2 work began.

## Results on LinkWatch

LinkWatch is the trusted test target. A tested run (Python 3.12.10, Windows, fresh virtual environments) is stored in `assets/runs/20261023_232609/`. Commit `f52f3930` of `rishrek/LinkWatch` was used and the source repository was not modified.

**Baseline.** 9 passed, 1 failed (`tests/test_report.py::test_report_renders_all_sites`). Cause: `Jinja2==2.11.3` imports `soft_unicode` from MarkupSafe, which MarkupSafe 3.0.4 no longer provides. `pip check` was clean even though the test failed, because Jinja2 2.11.3 declares no upper bound on MarkupSafe.

| Candidate | pip check | Passed | Failed |
|---|---|---|---|
| Cap MarkupSafe at 2.0.1 | clean | 10 | 0 |
| Cap MarkupSafe below 2.1.0 | clean | 10 | 0 |
| Upgrade Jinja2 to 3.1.4 | clean | 10 | 0 |
| Upgrade Jinja2 to 3.1.6 | clean | 10 | 0 |
| **The model's own proposal: MarkupSafe 2.1.1** | clean | **9** | **1** |

The model's proposal was tested and **rejected by the test run**: 2.1.1 still lacks the removed function. The capsule records the model's claims next to the evidence for and against each one. Capping MarkupSafe and upgrading Jinja2 are both presented as options with their trade-offs, and the maintainer chooses. An earlier HTML comparison found identical rendered output between the capped and the upgraded environments for the data used by the test.

**Model evaluation** (`llama3.1:8b` via Ollama, 3 runs per dependency, 9 calls, about 30 to 80 seconds each): 9 of 9 responses were valid JSON and 8 of 9 passed the gate. One `appdirs` run proposed `pathlib`, which was rejected because it has no `user_cache_dir`. The model agreed with itself on 3 of 3 runs for `nose` and 2 of 3 for `appdirs` and `toml`.

**Static analysis cannot see this kind of failure.** The Jinja2/MarkupSafe break only appeared when the tests ran, which is why tested runs are kept for repositories you trust.

Raw responses, prompt hashes, junit files and hashes are in the run folder. These numbers come from the recorded runs, so re-run and compare before citing them elsewhere.

## Quick start

### 1. Install

Requires Python 3.12 and (for local models) [Ollama](https://ollama.com).

```bash
git clone https://github.com/Pradnyadange/H26_Softerror_TrustLedger.git
cd H26_Softerror_TrustLedger/dependency-exit-capsule
python -m venv .venv          # use Python 3.12
# Windows: .\.venv\Scripts\Activate.ps1      macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Run the pipeline on a repository

All commands are run from `dependency-exit-capsule/`. A model ID is required; the tool does not choose one for you.

```bash
ollama list                                   # see installed models
python scripts/run_pipeline.py --repo-url https://github.com/rishrek/LinkWatch --top 3 --model-id llama3.1:8b
```

Run `python scripts/run_pipeline.py --help` for all options, including how to select every dependency instead of the top N. A run is written to `assets/runs/<owner>__<repo>__<sha>/`. If the same repository, commit, model and settings were already analysed, the saved run is reused and shown as a saved run.

Individual steps can also be run by hand:

```bash
python scripts/scan_risk.py --repo <path> --out assets/scan.json
python scripts/map_usage.py --repo <path> --dep <name> --out assets/usage_<name>.json
python scripts/propose_replacement.py --dep <name> --usage-file assets/usage_<name>.json \
       --provider ollama --model-id <model> --out assets/proposal_<name>.json
python scripts/run_diff_tests.py --repo <path> --proposal assets/proposal_<name>.json --out assets/diff_<name>.json
python scripts/build_capsule.py --dep <name> --out assets/capsules/
python scripts/verify_capsule.py assets/runs/<run>/manifest.json
```

Offline, rule-based suggestions are available only on request and are labelled RULE-BASED in the capsule:

```bash
python scripts/propose_replacement.py --dep <name> --usage-file assets/usage_<name>.json --offline --out assets/proposal_<name>.json
```

### 3. Start the viewer

```bash
python -m streamlit run app.py
```

Open `http://localhost:8501`. The server binds to localhost.

### 4. Run the tool's own tests

```bash
python -m pytest -q
```

### Optional environment variables

| Variable | Purpose |
|---|---|
| `GITHUB_TOKEN` | Raises GitHub API rate limits for the risk scan. If missing or limited, indicators are recorded as "unavailable" |
| `DEC_ACCESS_CODE` | If set, the viewer asks for this code before showing anything. If unset, the viewer runs normally. There are no user accounts |

API keys for hosted providers are read from environment variables and are never written to files, logs or capsules.

## Viewer

| Tab | What it shows |
|---|---|
| Analyze | GitHub URL or ZIP input, dependency scan and selection, model choice (from `ollama list`), live progress |
| Overview | Run summary, counts for every status, and one row per dependency with its action, status and reason |
| Capsule | OBSERVED column (indicators, usage, tests) next to AI-GENERATED column (proposal, steps, provenance); "rejected by the gate" table |
| Blast radius | Import graph with the selected dependency, its direct importers and downstream files |
| Test proof | Baseline vs candidate counts, `pip check`, new failures, per-test diff; "rejected by tests" table |
| Integrity | Expected vs current SHA-256 for capsules and evidence |
| About | Model information, privacy note, risk policy thresholds and the status table |

The header badge says **LIVE RUN** only for a run started in the current session and **SAVED RUN** (with a UTC time) otherwise. The viewer reads capsule files and contains no analysis logic of its own.

## Analyzing other repositories

The Analyze tab accepts a public GitHub URL or a ZIP file.

**External repositories are analysed statically.** The tool reads dependency files and code, queries PyPI, and asks the model for suggestions. **Nothing from the analysed repository is executed**, and its tests are not run, because running a stranger's tests means running untrusted code. Capsules from such runs cannot be `verified`. The viewer shows a banner saying so.

Safeguards in the intake code:

- Only `https://github.com/<owner>/<repo>` is accepted; credentials in URLs and dots-only names are rejected.
- `git clone --depth 1` with `GIT_TERMINAL_PROMPT=0`, no shell, a timeout, and size and file-count limits.
- ZIP files are checked for path traversal and symlinks and limited in size and file count while extracting.
- Package import names are read from a downloaded wheel (`--only-binary=:all:`, no install, no build scripts). A labelled static map is used only as a fallback.
- Repository text is untrusted data in prompts, and secret patterns are redacted before prompts are built.
- Dependencies that are not on PyPI (editable installs, `git+` URLs, local paths) are listed as unresolved with the reason instead of being dropped.

Public repositories and Python projects only. A repository with no supported dependency file gets an "unsupported" result.

## Run folders, labels and large repositories (Phase 2)

**Run metadata.** Each run folder gets a `run.json` with a display name, repository URL, commit SHA, mode (`tested` or `static`), and start and sealed times in UTC. The viewer uses it for the run selector label (`<repo> | tested or static | N capsules | <UTC time> UTC`) and for repository links. Links are never derived from folder names.

**One capsule per dependency.** Re-running a repository archives older capsules into `<run>/archive/` instead of leaving duplicates. Archived files are kept (never deleted), stay in the manifest history, and are ignored by the viewer and by all counts.

**Analyzing all dependencies.** Instead of a fixed top-N limit, the Analyze tab has an "Analyze all dependencies" option, with "Select all" and "Clear" buttons.

- Before running, the viewer shows how many dependencies will reach the model and an estimated time based on earlier run logs, or "no estimate yet".
- PyPI and metadata lookups run concurrently (up to 8 workers). Model calls run one at a time.
- Model runs per dependency default to 1; 3 runs is optional for comparing variation.
- A configurable hard maximum (default 100) asks the user to choose a subset for very large repositories.
- Each capsule is written as its dependency finishes, so a stopped run can be resumed. A Stop button ends the run cleanly and records it as "stopped". One failing dependency is recorded and does not abort the run.

## Models, access, license and privacy

| Item | Value |
|---|---|
| Model used for the LinkWatch results | `llama3.1:8b` (Meta Llama 3.1, 8B instruct) |
| Access method | Local [Ollama](https://ollama.com) daemon on `localhost:11434` |
| Also installed for comparison | `llama3.2:3b`, `gemma2:2b` |
| Gemma 4 | Not used |
| Model license | Llama 3.1 Community License. The license text and its SHA-256 are read from the model server and stored in each capsule's provenance |
| Other model licenses | `llama3.2:3b`: Llama 3.2 Community License. `gemma2:2b`: Gemma Terms of Use |

Llama 3.1 is licensed under the Llama 3.1 Community License, Copyright (c) Meta Platforms, Inc. All Rights Reserved. Read the full license text for attribution and acceptable-use terms before redistributing anything built on it.

Hosted providers (any OpenAI-compatible API) are supported through the same client. Whichever model actually ran is recorded in the capsule.

**Privacy**

- **Local mode:** the model call stays on your machine. The risk scan and import-name lookup still contact PyPI (package names only), cloning contacts GitHub, and GitHub API calls are optional.
- **Hosted mode:** prompts, including the usage lines taken from the analysed repository, are sent to the provider you configure.

## Limitations

- Results only cover what the repository's existing tests exercise. A single test may be the only coverage of a changed call site, and this is stated in the capsule.
- Tested runs so far were on Windows with Python 3.12 only.
- `pip check` cannot detect every incompatibility (it was clean at baseline although a test failed).
- Static runs of external repositories cannot prove that a replacement works, and cannot see failures that only appear at run time. They show usage, risk indicators and a checked suggestion.
- "Days since latest release" is an indicator, not proof that a project is abandoned. Healthy packages can be old.
- A passing test and a matching API name do not prove identical behaviour. Equivalence checks of old and new outputs are not built.
- Small local models can suggest weak replacements. The gates and tests decide what is accepted, not the model.
- Python only. Public repositories only.
- SHA-256 hashes detect changes made after a capsule was generated. They are not signatures, so someone who can edit both a file and the manifest can defeat them.
- Security vulnerabilities are out of scope by design, and the tool does not rank or decide by them.

## Repository layout

```
.
├── README.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── .gitignore
└── dependency-exit-capsule/        the Agent Skill (self-contained)
    ├── SKILL.md                    skill description and exact commands
    ├── app.py                      viewer entry point
    ├── viewer/                     viewer modules (data loading, components, graph)
    ├── static/                     bundled front-end assets
    ├── scripts/                    fetch_repo, parse_dependencies, import_mapper,
    │                               scan_risk, map_usage, propose_replacement, llm_client,
    │                               run_diff_tests, build_capsule, verify_capsule,
    │                               run_pipeline, common
    ├── references/                 capsule-schema.json, risk_policy.json and other labelled data files
    ├── assets/runs/                one folder per run: capsules, evidence, run.json, manifest.json, archive/
    ├── tests/                      tool tests and fixtures (including the labelled failing fixture)
    ├── pytest.ini
    └── requirements.txt
```

## License and third-party notices

This project is released under the license in [`LICENSE`](LICENSE). Third-party libraries, fonts, the graph library and model licenses are listed in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). No datasets are used. LinkWatch (MIT, by rishrek) is used only as a test target and is not included in this repository.
