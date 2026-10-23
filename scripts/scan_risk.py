import argparse
import glob
import os
import re
import sys
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
            # Remove inline comments
            line = line.split("#")[0].strip()
            # Match package name and specifier
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
        
        # Standard PEP 621 dependencies
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
        
        # Poetry dependencies
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

def fetch_pypi_indicators(package_name: str) -> list[dict]:
    """Query PyPI JSON API and compute days since latest release at run time."""
    pypi_url = f"https://pypi.org/pypi/{package_name}/json"
    fetched_at = get_utc_iso_timestamp()
    
    try:
        resp = requests.get(pypi_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            releases = data.get("releases", {})
            info = data.get("info", {})
            yanked = info.get("yanked", False)
            
            # Find the most recent release upload time
            latest_upload_time = None
            for rel_version, files in releases.items():
                for file_info in files:
                    upload_time_str = file_info.get("upload_time_iso_8601") or file_info.get("upload_time")
                    if upload_time_str:
                        try:
                            # Handle timezone offset or lack thereof
                            if "Z" in upload_time_str or "+" in upload_time_str:
                                dt = datetime.fromisoformat(upload_time_str.replace("Z", "+00:00"))
                            else:
                                dt = datetime.fromisoformat(upload_time_str).replace(tzinfo=timezone.utc)
                            
                            if latest_upload_time is None or dt > latest_upload_time:
                                latest_upload_time = dt
                        except Exception:
                            pass
            
            days_since = None
            if latest_upload_time:
                now = datetime.now(timezone.utc)
                days_since = max(0, (now - latest_upload_time).days)
            
            indicators = [
                {
                    "id": "days_since_release",
                    "value": days_since if days_since is not None else "unavailable",
                    "source_url": pypi_url,
                    "fetched_at": fetched_at
                },
                {
                    "id": "yanked",
                    "value": bool(yanked),
                    "source_url": pypi_url,
                    "fetched_at": fetched_at
                }
            ]
            return indicators
        else:
            return [
                {
                    "id": "days_since_release",
                    "value": "unavailable",
                    "source_url": pypi_url,
                    "fetched_at": fetched_at
                },
                {
                    "id": "yanked",
                    "value": "unavailable",
                    "source_url": pypi_url,
                    "fetched_at": fetched_at
                }
            ]
    except Exception as e:
        return [
            {
                "id": "days_since_release",
                "value": "unavailable",
                "source_url": pypi_url,
                "fetched_at": fetched_at
            },
            {
                "id": "yanked",
                "value": "unavailable",
                "source_url": pypi_url,
                "fetched_at": fetched_at
            }
        ]

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
                {
                    "id": "github_archived",
                    "value": data.get("archived", False),
                    "source_url": api_url,
                    "fetched_at": fetched_at
                },
                {
                    "id": "github_last_push",
                    "value": data.get("pushed_at", "unavailable"),
                    "source_url": api_url,
                    "fetched_at": fetched_at
                }
            ]
    except Exception:
        pass
        
    return [
        {
            "id": "github_archived",
            "value": "unavailable",
            "source_url": api_url,
            "fetched_at": fetched_at
        },
        {
            "id": "github_last_push",
            "value": "unavailable",
            "source_url": api_url,
            "fetched_at": fetched_at
        }
    ]

def scan_repository(repo_path: Path) -> dict:
    """Find all dependencies and calculate risk indicators."""
    all_deps = {}
    
    # 1. Parse requirements*.txt
    for req_file in repo_path.glob("requirements*.txt"):
        deps = parse_requirements_file(req_file)
        for name, info in deps.items():
            if name not in all_deps:
                all_deps[name] = {"declared_specifier": info["specifier"], "declared_in": [info["declared_in"]]}
            else:
                if info["declared_in"] not in all_deps[name]["declared_in"]:
                    all_deps[name]["declared_in"].append(info["declared_in"])

    # 2. Parse pyproject.toml
    pyproject_path = repo_path / "pyproject.toml"
    if pyproject_path.exists():
        pyproject_deps = parse_pyproject(pyproject_path)
        for name, info in pyproject_deps.items():
            if name not in all_deps:
                all_deps[name] = {"declared_specifier": info["specifier"], "declared_in": [info["declared_in"]]}
            else:
                if info["declared_in"] not in all_deps[name]["declared_in"]:
                    all_deps[name]["declared_in"].append(info["declared_in"])
                    
    github_token = os.environ.get("GITHUB_TOKEN")
    
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
