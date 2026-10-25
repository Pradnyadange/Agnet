"""
action_decision.py – decide the action for each dependency from observed data only.
Called BEFORE any model call. Results determine whether the model is called at all.

Actions
-------
  replace          – archived, deprecated, or very stale (>= stale_days_replace days)
  upgrade          – healthy but the pinned version is many releases behind latest
  remove           – no Python-file usage, no non-Python references, not required_by
                     another declared dep, not a protected dev-scope tool
  no_action        – healthy and current; or dev-scope tool not marked deprecated

Only ``replace`` and ``upgrade`` trigger a model call.

Thresholds are read from ``references/risk_policy.json`` (never hard-coded here).
"""
from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path
from typing import Optional

_POLICY_PATH = Path(__file__).resolve().parent.parent / "references" / "risk_policy.json"
_POLICY: dict | None = None


def _policy() -> dict:
    global _POLICY
    if _POLICY is None:
        try:
            import json
            _POLICY = json.loads(_POLICY_PATH.read_text(encoding="utf-8"))
        except Exception:
            _POLICY = {}
    return _POLICY


def _p(key, default):
    return _policy().get(key, default)


# ---------------------------------------------------------------------------
# Scope detection
# ---------------------------------------------------------------------------

def detect_scope(dep_name: str, declared_in: list[str]) -> str:
    """Return 'dev' or 'runtime'."""
    dev_patterns: list[str] = _p("dev_scope_patterns", [])
    dev_file_patterns: list[str] = _p("dev_file_patterns", [])

    dn = dep_name.lower().replace("-", "").replace("_", "")
    for pat in dev_patterns:
        if dn == pat.lower().replace("-", "").replace("_", ""):
            return "dev"

    for filename in declared_in:
        for fp in dev_file_patterns:
            if fnmatch.fnmatch(filename.lower(), fp.lower()):
                return "dev"

    return "runtime"


# ---------------------------------------------------------------------------
# Non-Python reference check
# ---------------------------------------------------------------------------

def dep_referenced_in_non_python(dep_name: str, repo_path: Path) -> bool:
    """Return True if dep_name appears in a non-Python project configuration file."""
    safe_pat = dep_name.lower().replace("-", r"[-_]").replace("_", r"[-_]")
    pattern = re.compile(safe_pat, re.IGNORECASE)
    globs: list[str] = _p("non_python_ref_globs", [])

    checked = set()
    for glob_pat in globs:
        for fpath in repo_path.rglob(glob_pat):
            if fpath in checked or fpath.suffix == ".py":
                continue
            checked.add(fpath)
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
                if pattern.search(text):
                    return True
            except Exception:
                pass
    return False


# ---------------------------------------------------------------------------
# Deprecation / archive signal from PyPI full JSON
# ---------------------------------------------------------------------------

def has_deprecation_signal(pypi_full: dict) -> bool:
    """Return True if PyPI metadata signals deprecation or archival."""
    info = pypi_full.get("info", {})
    if info.get("yanked"):
        return True
    for c in info.get("classifiers", []):
        if any(kw in c for kw in ("Inactive", "Abandoned", "Unsupported", "Obsolete")):
            return True
    desc = (info.get("description") or "") + " " + (info.get("summary") or "")
    desc_lower = desc.lower()
    keywords: list[str] = _p("deprecation_keywords", [])
    return any(kw.lower() in desc_lower for kw in keywords)


# ---------------------------------------------------------------------------
# Version-lag check
# ---------------------------------------------------------------------------

def version_lag(pypi_full: dict, declared_specifier: str) -> int:
    """Return how many final releases exist after the declared pinned version."""
    m = re.search(r"==\s*([^\s,;]+)", declared_specifier or "")
    if not m:
        return 0
    declared_ver_str = m.group(1)
    latest = pypi_full.get("info", {}).get("version", "")
    if not latest:
        return 0
    try:
        from packaging.version import Version
        declared_v = Version(declared_ver_str)
        latest_v = Version(latest)
        if latest_v <= declared_v:
            return 0
        count = 0
        for ver_str in pypi_full.get("releases", {}):
            try:
                v = Version(ver_str)
                if not v.is_prerelease and not v.is_devrelease and v > declared_v:
                    count += 1
            except Exception:
                pass
        return count
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Main action-decision function
# ---------------------------------------------------------------------------

def decide_action(
    dep_name: str,
    dep_info: dict,
    pypi_full: dict | None,
    usage_locations: list[dict],
    repo_path: Path,
    required_by: list[str],
    github_archived: bool = False,
) -> dict:
    """
    Parameters
    ----------
    dep_name        canonical package name (lower, hyphenated)
    dep_info        entry from scan_dependencies: {declared_specifier, declared_in, risk_indicators}
    pypi_full       full PyPI JSON response (or None if unavailable)
    usage_locations list of usage dicts from map_repo_usage
    repo_path       root of the cloned repo (for non-Python ref search)
    required_by     list of other declared dep names that list this dep as a requirement
    github_archived True if the GitHub API says the repo is archived

    Returns
    -------
    {
      "action":        "replace" | "upgrade" | "remove" | "no_action",
      "scope":         "runtime" | "dev",
      "reason":        str,
      "status_reason": str,
      "call_model":    bool,
    }
    """
    declared_specifier = dep_info.get("declared_specifier", "")
    declared_in = dep_info.get("declared_in", [])
    risk_indicators = dep_info.get("risk_indicators", [])

    scope = detect_scope(dep_name, declared_in)

    # Extract pre-fetched indicator values
    days_since: int | None = None
    yanked_flag = False
    for ind in risk_indicators:
        if ind["id"] == "days_since_release" and isinstance(ind.get("value"), (int, float)):
            days_since = int(ind["value"])
        if ind["id"] == "yanked" and ind.get("value") is True:
            yanked_flag = True

    # --- Policy thresholds (from risk_policy.json) ---
    stale_replace: int = _p("stale_days_replace", 730)
    stale_upgrade: int = _p("stale_days_upgrade", 180)
    lag_threshold: int = _p("version_lag_upgrade", 5)

    # --- Deprecation / archive signal ---
    deprecated = (
        github_archived
        or yanked_flag
        or (pypi_full is not None and has_deprecation_signal(pypi_full))
    )

    is_dev = (scope == "dev")

    # ===== Decision tree =====

    # 1. Explicitly deprecated / archived → always replace (even dev tools)
    if deprecated:
        reason_txt = (
            "GitHub repository is archived"
            if github_archived
            else "yanked on PyPI"
            if yanked_flag
            else "deprecation signal in PyPI description or classifiers"
        )
        return _result("replace", scope, reason_txt, "archived_or_deprecated", call_model=True)

    # 2. Very stale → replace
    if days_since is not None and days_since >= stale_replace:
        return _result(
            "replace", scope,
            f"no release in {days_since} days (threshold {stale_replace})",
            "stale_replace",
            call_model=True,
        )

    # 3. Dev-scope tool (not deprecated) → no_action
    #    (dev tools are used via CLI; model proposals not warranted unless deprecated)
    if is_dev and not deprecated:
        return _result(
            "no_action", scope,
            "dev-scope tool; replacement not proposed unless archived or deprecated",
            "dev_tool_not_deprecated",
            call_model=False,
        )

    # 4. No Python-file usage
    if not usage_locations:
        if required_by:
            return _result(
                "no_action", scope,
                f"no direct Python usage but required transitively by: {', '.join(required_by)}",
                "required_by_other_dependency",
                call_model=False,
            )
        if dep_referenced_in_non_python(dep_name, repo_path):
            return _result(
                "no_action", scope,
                "no Python-file usage but referenced in non-Python project files (Makefile/CI/cfg)",
                "referenced_in_non_python_files",
                call_model=False,
            )
        return _result(
            "remove", scope,
            "no usage in Python files, no non-Python references, not required transitively",
            "no_usage_found",
            call_model=False,
        )

    # 5. Moderately stale → maybe upgrade
    if days_since is not None and days_since >= stale_upgrade:
        lag = version_lag(pypi_full, declared_specifier) if pypi_full else 0
        if lag >= lag_threshold:
            return _result(
                "upgrade", scope,
                f"pinned version is {lag} releases behind latest; {days_since} days since last release",
                "version_lag",
                call_model=True,
            )

    # 6. Healthy and current
    return _result(
        "no_action", scope,
        "healthy and current",
        "healthy_no_action",
        call_model=False,
    )


def _result(action: str, scope: str, reason: str, status_reason: str, call_model: bool) -> dict:
    return {
        "action": action,
        "scope": scope,
        "reason": reason,
        "status_reason": status_reason,
        "call_model": call_model,
    }
