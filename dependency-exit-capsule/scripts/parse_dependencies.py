import configparser
import os
import re
import tomllib
from pathlib import Path
from packaging.requirements import Requirement, InvalidRequirement

def parse_requirements_txt(file_path: Path, visited: set | None = None) -> dict[str, dict]:
    """
    Parses requirements*.txt with support for recursive -r / --requirement includes.
    Ignores comments, editable flags, and .env files.
    """
    if visited is None:
        visited = set()

    real_path = file_path.resolve()
    if real_path in visited:
        return {}
    visited.add(real_path)

    results = {}
    if not file_path.exists():
        return results

    rel_name = file_path.name
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return results

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        # Handle -r / --requirement includes
        if line.startswith("-r ") or line.startswith("--requirement "):
            included_file_str = line.split(maxsplit=1)[1].strip()
            included_path = (file_path.parent / included_file_str).resolve()
            sub_results = parse_requirements_txt(included_path, visited)
            for k, v in sub_results.items():
                if k not in results:
                    results[k] = v
                else:
                    for src in v["declared_in"]:
                        if src not in results[k]["declared_in"]:
                            results[k]["declared_in"].append(src)
            continue

        # Ignore unsupported options: -i, -f, --extra-index-url, -e, --editable
        if line.startswith("-") or line.startswith("--"):
            continue

        # Strip inline comments
        if " #" in line:
            line = line.split(" #", 1)[0].strip()

        try:
            req = Requirement(line)
            name = req.name.lower().replace("_", "-")
            specifier = str(req.specifier) if req.specifier else ""
            if name not in results:
                results[name] = {
                    "name": name,
                    "declared_specifier": specifier,
                    "declared_in": [rel_name]
                }
            else:
                if rel_name not in results[name]["declared_in"]:
                    results[name]["declared_in"].append(rel_name)
        except InvalidRequirement:
            # Fallback regex if packaging cannot parse complex flags
            match = re.match(r"^([A-Za-z0-9_.\-]+)(.*)$", line)
            if match:
                name = match.group(1).lower().replace("_", "-")
                spec = match.group(2).strip()
                if name not in results:
                    results[name] = {
                        "name": name,
                        "declared_specifier": spec,
                        "declared_in": [rel_name]
                    }
                else:
                    if rel_name not in results[name]["declared_in"]:
                        results[name]["declared_in"].append(rel_name)

    return results


def parse_pyproject_toml(file_path: Path) -> dict[str, dict]:
    """Parses standard pyproject.toml [project.dependencies] and [tool.poetry.dependencies]."""
    results = {}
    if not file_path.exists():
        return results

    rel_name = file_path.name
    try:
        data = tomllib.loads(file_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return results

    # PEP 621 [project.dependencies]
    project_deps = data.get("project", {}).get("dependencies", [])
    if isinstance(project_deps, list):
        for dep_str in project_deps:
            try:
                req = Requirement(dep_str)
                name = req.name.lower().replace("_", "-")
                results[name] = {
                    "name": name,
                    "declared_specifier": str(req.specifier) if req.specifier else "",
                    "declared_in": [rel_name]
                }
            except Exception:
                pass

    # Optional dependencies
    opt_deps = data.get("project", {}).get("optional-dependencies", {})
    if isinstance(opt_deps, dict):
        for group, group_deps in opt_deps.items():
            if isinstance(group_deps, list):
                for dep_str in group_deps:
                    try:
                        req = Requirement(dep_str)
                        name = req.name.lower().replace("_", "-")
                        if name not in results:
                            results[name] = {
                                "name": name,
                                "declared_specifier": str(req.specifier) if req.specifier else "",
                                "declared_in": [f"{rel_name} [{group}]"]
                            }
                        else:
                            results[name]["declared_in"].append(f"{rel_name} [{group}]")
                    except Exception:
                        pass

    # Poetry style [tool.poetry.dependencies]
    poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    if isinstance(poetry_deps, dict):
        for pkg, spec in poetry_deps.items():
            if pkg.lower() == "python":
                continue
            name = pkg.lower().replace("_", "-")
            spec_str = spec if isinstance(spec, str) else str(spec.get("version", "")) if isinstance(spec, dict) else ""
            if name not in results:
                results[name] = {
                    "name": name,
                    "declared_specifier": spec_str,
                    "declared_in": [f"{rel_name} (poetry)"]
                }
            else:
                results[name]["declared_in"].append(f"{rel_name} (poetry)")

    return results


def parse_setup_cfg(file_path: Path) -> dict[str, dict]:
    """Parses setup.cfg [options] install_requires and [options.extras_require]."""
    results = {}
    if not file_path.exists():
        return results

    rel_name = file_path.name
    parser = configparser.ConfigParser()
    try:
        parser.read(str(file_path.resolve()), encoding="utf-8")
    except Exception:
        return results

    # install_requires
    if parser.has_section("options") and parser.has_option("options", "install_requires"):
        raw_val = parser.get("options", "install_requires")
        for line in raw_val.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                req = Requirement(line)
                name = req.name.lower().replace("_", "-")
                results[name] = {
                    "name": name,
                    "declared_specifier": str(req.specifier) if req.specifier else "",
                    "declared_in": [rel_name]
                }
            except Exception:
                pass

    # extras_require
    if parser.has_section("options.extras_require"):
        for extra, raw_lines in parser.items("options.extras_require"):
            for line in raw_lines.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    req = Requirement(line)
                    name = req.name.lower().replace("_", "-")
                    if name not in results:
                        results[name] = {
                            "name": name,
                            "declared_specifier": str(req.specifier) if req.specifier else "",
                            "declared_in": [f"{rel_name} [{extra}]"]
                        }
                    else:
                        results[name]["declared_in"].append(f"{rel_name} [{extra}]")
                except Exception:
                    pass

    return results


def parse_repository_dependencies(repo_path: Path) -> tuple[dict[str, dict], list[str]]:
    """
    Scans repository directory for requirements*.txt, pyproject.toml, and setup.cfg.
    Returns (dependencies_dict, discovered_manifest_files).
    If no supported manifest files are found, returns ({}, []).
    """
    discovered_manifests = []
    all_deps = {}

    # Ignore .env files, virtualenvs, etc.
    # 1. requirements*.txt
    for req_file in sorted(repo_path.glob("requirements*.txt")):
        if req_file.name.lower().startswith(".env"):
            continue
        discovered_manifests.append(req_file.name)
        file_deps = parse_requirements_txt(req_file)
        for name, info in file_deps.items():
            if name not in all_deps:
                all_deps[name] = info
            else:
                for d in info["declared_in"]:
                    if d not in all_deps[name]["declared_in"]:
                        all_deps[name]["declared_in"].append(d)

    # 2. pyproject.toml
    pyproject_file = repo_path / "pyproject.toml"
    if pyproject_file.exists():
        discovered_manifests.append("pyproject.toml")
        py_deps = parse_pyproject_toml(pyproject_file)
        for name, info in py_deps.items():
            if name not in all_deps:
                all_deps[name] = info
            else:
                for d in info["declared_in"]:
                    if d not in all_deps[name]["declared_in"]:
                        all_deps[name]["declared_in"].append(d)

    # 3. setup.cfg
    setup_cfg_file = repo_path / "setup.cfg"
    if setup_cfg_file.exists():
        discovered_manifests.append("setup.cfg")
        cfg_deps = parse_setup_cfg(setup_cfg_file)
        for name, info in cfg_deps.items():
            if name not in all_deps:
                all_deps[name] = info
            else:
                for d in info["declared_in"]:
                    if d not in all_deps[name]["declared_in"]:
                        all_deps[name]["declared_in"].append(d)

    return all_deps, discovered_manifests
