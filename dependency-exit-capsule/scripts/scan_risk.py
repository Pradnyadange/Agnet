import argparse
import fnmatch
import glob
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import requests

import tomllib

try:
    from common import get_utc_iso_timestamp, save_json
except ImportError:
    from scripts.common import get_utc_iso_timestamp, save_json

def parse_requirements_file(filepath: Path) -> dict[str, dict]:
    """Parse a requirements*.txt file and return found dependencies with specifiers."""
    deps = {}
    if not filepath.is_file():
        return deps
    
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            line = line.split("#")[0].strip()
            match = re.match(r"^([A-Za-z0-9_.\-]+)(.*)$", line)
            if match:
                pkg_name = match.group(1).lower().replace("_", "-")
                specifier = match.group(2).strip()
                deps[pkg_name] = {
                    "raw_name": match.group(1),
                    "specifier": specifier,
                    "declared_in": filepath.name
                }
    return deps

def parse_pyproject(filepath: Path) -> dict[str, dict]:
    """Parse pyproject.toml dependencies."""
    deps = {}
    if not filepath.is_file():
        return deps
    
    try:
        with open(filepath, "rb") as f:
            data = tomllib.load(f)
        
        project_deps = data.get("project", {}).get("dependencies", [])
        for dep_str in project_deps:
            match = re.match(r"^([A-Za-z0-9_.\-]+)(.*)$", dep_str.strip())
            if match:
                pkg_name = match.group(1).lower().replace("_", "-")
                deps[pkg_name] = {
                    "raw_name": match.group(1),
                    "specifier": match.group(2).strip(),
                    "declared_in": "pyproject.toml"
                }
        
        poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        for name, spec in poetry_deps.items():
            if name.lower() == "python":
                continue
            pkg_name = name.lower().replace("_", "-")
            spec_str = spec if isinstance(spec, str) else str(spec.get("version", ""))
            deps[pkg_name] = {
                "raw_name": name,
                "specifier": spec_str,
                "declared_in": "pyproject.toml"
            }
    except Exception as e:
        sys.stderr.write(f"Warning: Failed parsing {filepath}: {e}\n")
    return deps


# ---------------------------------------------------------------------------
# Full PyPI JSON fetching with retry and rate-limit handling
# ---------------------------------------------------------------------------

def fetch_pypi_full(package_name: str, retries: int = 3, backoff: float = 2.0) -> dict | None:
    """
    Fetch the full PyPI JSON for a package.  Returns None on persistent failure.
    Respects 429 rate-limit responses with exponential back-off.
    """
    pypi_url = f"https://pypi.org/pypi/{package_name}/json"
    for attempt in range(retries):
        try:
            resp = requests.get(pypi_url, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                wait = backoff * (attempt + 1) * 2
                sys.stderr.write(f"[scan_risk] 429 for {package_name}; sleeping {wait:.1f}s\n")
                time.sleep(wait)
            elif resp.status_code == 404:
                return None
            else:
                time.sleep(backoff)
        except requests.exceptions.RequestException as exc:
            sys.stderr.write(f"[scan_risk] request error for {package_name}: {exc}\n")
            time.sleep(backoff * (attempt + 1))
    return None


def fetch_all_deps_parallel(
    dep_names: list[str],
    max_workers: int = 8,
    retries: int = 3,
    backoff: float = 2.0,
) -> dict[str, dict | None]:
    """
    Fetch full PyPI JSON for all deps concurrently (ThreadPoolExecutor, max_workers).
    Returns {dep_name: pypi_full_json | None}.
    """
    results: dict[str, dict | None] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_pypi_full, dep, retries, backoff): dep
            for dep in dep_names
        }
        for future in as_completed(futures):
            dep = futures[future]
            try:
                results[dep] = future.result()
            except Exception as exc:
                sys.stderr.write(f"[scan_risk] parallel fetch failed for {dep}: {exc}\n")
                results[dep] = None
    return results


def extract_indicators_from_full(package_name: str, pypi_full: dict | None) -> list[dict]:
    """
    Derive the risk_indicators list from a full PyPI JSON response.
    Produces the same shape as fetch_pypi_indicators so callers need no change.
    """
    fetched_at = get_utc_iso_timestamp()
    pypi_url = f"https://pypi.org/pypi/{package_name}/json"

    if not pypi_full:
        return [
            {"id": "days_since_release", "value": "unavailable", "source_url": pypi_url, "fetched_at": fetched_at},
            {"id": "yanked",             "value": "unavailable", "source_url": pypi_url, "fetched_at": fetched_at},
        ]

    info = pypi_full.get("info", {})
    yanked = info.get("yanked", False)

    latest_upload_time = None
    for _ver, files in pypi_full.get("releases", {}).items():
        for file_info in files:
            upload_str = file_info.get("upload_time_iso_8601") or file_info.get("upload_time")
            if upload_str:
                try:
                    dt = datetime.fromisoformat(upload_str.replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if latest_upload_time is None or dt > latest_upload_time:
                        latest_upload_time = dt
                except Exception:
                    pass

    days_since = None
    if latest_upload_time:
        days_since = max(0, (datetime.now(timezone.utc) - latest_upload_time).days)

    return [
        {
            "id": "days_since_release",
            "value": days_since if days_since is not None else "unavailable",
            "source_url": pypi_url,
            "fetched_at": fetched_at,
        },
        {
            "id": "yanked",
            "value": bool(yanked),
            "source_url": pypi_url,
            "fetched_at": fetched_at,
        },
    ]


def build_required_by_map(
    dep_names: list[str],
    pypi_data: dict[str, dict | None],
) -> dict[str, list[str]]:
    """
    For each dep in dep_names, check if any OTHER dep lists it in requires_dist.
    Returns {dep_name: [dep_names_that_require_it]}.
    """
    required_by: dict[str, list[str]] = {dep: [] for dep in dep_names}
    norm_map = {
        dep.lower().replace("-", "").replace("_", ""): dep
        for dep in dep_names
    }

    for dep_name, data in pypi_data.items():
        if not data:
            continue
        requires_dist = data.get("info", {}).get("requires_dist") or []
        for req_str in requires_dist:
            m = re.match(r"^([A-Za-z0-9_.\-]+)", req_str.strip())
            if not m:
                continue
            req_norm = m.group(1).lower().replace("-", "").replace("_", "")
            target = norm_map.get(req_norm)
            if target and target != dep_name:
                if dep_name not in required_by[target]:
                    required_by[target].append(dep_name)

    return required_by


# ---------------------------------------------------------------------------
# Legacy single-package indicator fetcher (delegates to full fetch for consistency)
# ---------------------------------------------------------------------------

def fetch_pypi_indicators(package_name: str) -> list[dict]:
    """Query PyPI JSON API and compute days since latest release at run time."""
    pypi_full = fetch_pypi_full(package_name)
    return extract_indicators_from_full(package_name, pypi_full)


def fetch_github_indicators(repo_owner_repo: str, token: str | None = None) -> list[dict]:
    """Optionally query GitHub API for archived flag and last push."""
    fetched_at = get_utc_iso_timestamp()
    api_url = f"https://api.github.com/repos/{repo_owner_repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
        
    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return [
                {"id": "github_archived", "value": data.get("archived", False), "source_url": api_url, "fetched_at": fetched_at},
                {"id": "github_last_push", "value": data.get("pushed_at", "unavailable"), "source_url": api_url, "fetched_at": fetched_at}
            ]
    except Exception:
        pass
        
    return [
        {"id": "github_archived", "value": "unavailable", "source_url": api_url, "fetched_at": fetched_at},
        {"id": "github_last_push", "value": "unavailable", "source_url": api_url, "fetched_at": fetched_at}
    ]

def scan_repository(repo_path: Path) -> dict:
    """Find all dependencies and calculate risk indicators."""
    all_deps = {}
    
    for req_file in repo_path.glob("requirements*.txt"):
        if req_file.name.lower().startswith(".env") or req_file.name.lower() == ".env":
            continue
        deps = parse_requirements_file(req_file)
        for name, info in deps.items():
            if name not in all_deps:
                all_deps[name] = {"declared_specifier": info["specifier"], "declared_in": [info["declared_in"]]}
            else:
                if info["declared_in"] not in all_deps[name]["declared_in"]:
                    all_deps[name]["declared_in"].append(info["declared_in"])

    pyproject_path = repo_path / "pyproject.toml"
    if pyproject_path.exists():
        pyproject_deps = parse_pyproject(pyproject_path)
        for name, info in pyproject_deps.items():
            if name not in all_deps:
                all_deps[name] = {"declared_specifier": info["specifier"], "declared_in": [info["declared_in"]]}
            else:
                if info["declared_in"] not in all_deps[name]["declared_in"]:
                    all_deps[name]["declared_in"].append(info["declared_in"])
                    
    results = {
        "repo_path": str(repo_path.resolve()),
        "scanned_at": get_utc_iso_timestamp(),
        "dependencies": {}
    }
    
    for dep_name, dep_info in all_deps.items():
        indicators = fetch_pypi_indicators(dep_name)
        results["dependencies"][dep_name] = {
            "name": dep_name,
            "declared_specifier": dep_info["declared_specifier"],
            "declared_in": dep_info["declared_in"],
            "risk_indicators": indicators
        }
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Stage 1: Scan repository dependencies and risk indicators.")
    parser.add_argument("--repo", required=True, help="Path to repository to scan")
    parser.add_argument("--out", required=True, help="Path to save scan.json output")
    args = parser.parse_args()
    
    repo_path = Path(args.repo)
    if not repo_path.is_dir():
        sys.stderr.write(f"Error: Repository path does not exist or is not a directory: {args.repo}\n")
        sys.exit(1)
        
    scan_results = scan_repository(repo_path)
    save_json(scan_results, args.out)
    print(f"Scanned {len(scan_results['dependencies'])} dependencies. Saved scan results to {args.out}")

if __name__ == "__main__":
    main()
