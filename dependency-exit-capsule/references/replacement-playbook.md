# Replacement Playbook: Dependency Exit Strategy

This document provides system prompt instructions and guidelines for proposing drop-in replacements for obsolete or risky Python dependencies.

## Key Principles

1. **Stdlib First**:
   - If Python standard library offers modern native alternatives (e.g., `tomllib` in 3.11+, `ipaddress`, `zoneinfo`, `secrets`, `pathlib`, `http.client`), prefer stdlib over adding another third-party package.
2. **Maintained Successors**:
   - When stdlib is insufficient, propose well-maintained successor packages (e.g., `platformdirs` for `appdirs`, `httpx` or `requests` for `urllib3` pinning issues, `tomli` for `toml` on <3.11).
3. **Symbol Grounding**:
   - The proposal MUST be strictly grounded in the real usage call sites discovered by the AST scan.
   - Every used function, method, attribute, and import must map directly to the replacement.
4. **Validation**:
   - All proposed packages must be validated against `sys.stdlib_module_names` or verified on PyPI.
   - API coverage of required symbols must be measured.
5. **No Hallucinations**:
   - If no safe drop-in replacement exists without complete architectural rewrites, the model must output `no_valid_proposal`.
