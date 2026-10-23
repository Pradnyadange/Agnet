# Phase 0 Audit: Hardcoding, Claims, and Model Names

Date: 2026-10-22
Repository: dependency-exit-capsule

## Summary of Findings

| Location | Finding / Text | Category | Severity | Remediation Plan |
|---|---|---|---|---|
| `scripts/run_diff_tests.py:168-178` | `dep_clean == "toml" and repl_clean == "tomllib"`, `dep_clean == "appdirs" and repl_clean == "platformdirs"` | Hardcoded migration strings | High | Replace with generic structured edits `{file, old_text, new_text}` applied only if `old_text` occurs exactly once; boundary checked against observed files + manifests. |
| `scripts/build_capsule.py:223` | `repo_name = Path(repo_path).name or "LinkWatch"` | Hardcoded fallback | Medium | Derive name dynamically from URL/path basename. |
| `scripts/build_capsule.py:277` | `"commit_sha": "a1b2c3d4e5f678901234567890abcdef12345678"` | Dummy placeholder SHA | High | Refuse dummy/placeholder SHAs; require real commit SHA from git. |
| `scripts/build_capsule.py:280` | `"Dependency {dep_name} shows high staleness risk indicators and should be replaced with modern supported alternative."` | Generic template sentence | Medium | Derive maintenance problem statement dynamically from observed risk indicators only (release age, yanked status, archived flag). |
| `scripts/scan_risk.py:11-13` | `import toml as tomllib` fallback when `tomllib` is absent | Third-party parser fallback | Medium | Use stdlib `import tomllib` only. Fail with clear error on Python < 3.11. |
| `scripts/llm_client.py:18,22` | Default `model_id="qwen2.5-coder:7b"`, inferred license by name | Model Assumption | High | Require explicit `--model-id`. Read license from Ollama model info (`ollama show` / API); store license text and sha256. Never infer license from model name. |
| `scripts/propose_replacement.py:131,237` | Default `qwen2.5-coder:7b`, `"gpt-4o"` | Model Assumption | High | Require explicit `--model-id`. Remove defaults. |
| `scripts/map_usage.py:96` | Comment referencing `appdirs.user_cache_dir` | Comment residual | Low | Remove specific package name from comment. |
| `app.py:499` | Static text: `Model Name: Qwen 2.5 Coder 7B Instruct / Llama 3.1 8B` | Hardcoded Model Claim | High | Read provenance dynamically from selected capsule. |
| `app.py:506` | `Zero outbound network calls; AST and code snippets never leave your machine.` | Unqualified claim | Medium | State accurately that local model runs locally while PyPI risk checks make outbound HTTP calls for metadata. |
| `app.py:517` | `<th>Working (Production Tested)</th>` | Unqualified claim | High | Change to `Implemented & Automated`. |
| `app.py:50` | Tab `Integrity` | Wording | Medium | Rename to `Integrity manifest (SHA-256 file hashes)` and clarify hashes detect changes since generation, not tamper-proof without cryptographic signing. |
