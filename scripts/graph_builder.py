import argparse
import ast
import os
import sys
from pathlib import Path

from common import save_json, load_json

class ImportGraphExtractor:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.py_files = {}       # rel_path -> list of imported module names
        self.all_imports = set()
        self.ignore_dirs = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "build", "dist", ".tox"}

    def scan_files(self):
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs and not d.startswith(".")]
            for file in files:
                if file.endswith(".py"):
                    full_p = Path(root) / file
                    rel_p = full_p.relative_to(self.repo_path).as_posix()
                    self._parse_file(full_p, rel_p)

    def _parse_file(self, full_p: Path, rel_p: str):
        try:
            tree = ast.parse(full_p.read_text(encoding="utf-8", errors="replace"), filename=str(full_p))
        except Exception:
            self.py_files[rel_p] = []
            return

        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    imported_modules.add(root_mod)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split(".")[0]
                    imported_modules.add(root_mod)
                elif node.level and node.level > 0:
                    # Relative import
                    # Map relative import to corresponding file if possible
                    file_dir = Path(rel_p).parent
                    imported_modules.add(file_dir.as_posix())

        self.py_files[rel_p] = list(imported_modules)
        for m in imported_modules:
            self.all_imports.add(m)

def build_blast_cone(target_dep: str, edges: list[dict]) -> set[str]:
    """
    Blast cone for a dependency: start at files that import it,
    then walk edges in reverse (who imports those files) until no new files appear.
    """
    dep_clean = target_dep.lower().replace("-", "_")
    direct_importers = set()
    
    # Direct importers
    for edge in edges:
        target = edge["to"].lower().replace("-", "_")
        if target == dep_clean:
            direct_importers.add(edge["from"])
            
    # Reverse walk: find files that import direct_importers
    blast_cone = set(direct_importers)
    changed = True
    while changed:
        changed = False
        for edge in edges:
            if edge["to"] in blast_cone and edge["from"] not in blast_cone:
                blast_cone.add(edge["from"])
                changed = True
    return blast_cone

def build_graph_data(repo_path: Path, target_dep: str | None = None, coverage_json_path: Path | None = None, junit_xml_path: Path | None = None) -> dict:
    extractor = ImportGraphExtractor(repo_path)
    extractor.scan_files()
    
    # Build nodes and edges
    # Project files are nodes, imported packages are nodes
    nodes = {}
    edges = []
    
    # 1. Project file nodes
    for file_path in extractor.py_files.keys():
        nodes[file_path] = {
            "id": file_path,
            "label": file_path,
            "type": "file",
            "in_degree": 0,
            "test_status": "not_covered"
        }
        
    # 2. Package nodes & Edges
    for file_path, imports in extractor.py_files.items():
        for imp in imports:
            # Check if imp matches another project file (e.g., internal module)
            # Or if it is a third-party package
            is_internal = False
            for p in extractor.py_files.keys():
                stem = Path(p).stem
                if stem == imp or p.replace(".py", "").replace("/", ".") == imp:
                    target_id = p
                    is_internal = True
                    break
            if not is_internal:
                target_id = imp
                if target_id not in nodes:
                    nodes[target_id] = {
                        "id": target_id,
                        "label": target_id,
                        "type": "package",
                        "in_degree": 0,
                        "test_status": "not_covered"
                    }
                    
            edges.append({
                "from": file_path,
                "to": target_id
            })

    # Compute in-degree: count of importers per node
    for edge in edges:
        to_id = edge["to"]
        if to_id in nodes:
            nodes[to_id]["in_degree"] += 1

    # Apply coverage and test results if available
    if coverage_json_path and coverage_json_path.exists():
        try:
            cov_data = load_json(coverage_json_path)
            cov_files = cov_data.get("files", {})
            for f_key, f_val in cov_files.items():
                norm_key = Path(f_key).as_posix()
                for n_id, n_info in nodes.items():
                    if norm_key.endswith(n_id):
                        pct = f_val.get("summary", {}).get("percent_covered", 0)
                        if pct > 0:
                            n_info["test_status"] = "covered_and_passing"
        except Exception:
            pass

    # Blast cone for target dependency
    blast_cone = []
    direct_usage = []
    if target_dep:
        dep_clean = target_dep.lower().replace("-", "_")
        for edge in edges:
            if edge["to"].lower().replace("-", "_") == dep_clean:
                direct_usage.append(edge["from"])
        blast_cone = list(build_blast_cone(target_dep, edges))

    # Top hot files by in-degree
    sorted_files = sorted(
        [n for n in nodes.values() if n["type"] == "file"],
        key=lambda x: x["in_degree"],
        reverse=True
    )
    
    return {
        "file_count": len([n for n in nodes.values() if n["type"] == "file"]),
        "import_edge_count": len(edges),
        "target_dependency": target_dep,
        "direct_usage_files": direct_usage,
        "blast_cone_files": blast_cone,
        "top_files_by_importers": sorted_files[:10],
        "nodes": list(nodes.values()),
        "edges": edges
    }

def main():
    parser = argparse.ArgumentParser(description="Graph Builder: AST import graph, blast cone, and test status.")
    parser.add_argument("--repo", required=True, help="Path to repository")
    parser.add_argument("--dep", default=None, help="Target dependency")
    parser.add_argument("--coverage-json", default=None, help="Optional coverage JSON path")
    parser.add_argument("--out", required=True, help="Output path for graph JSON")
    args = parser.parse_args()
    
    cov_p = Path(args.coverage_json) if args.coverage_json else None
    graph_data = build_graph_data(Path(args.repo), args.dep, cov_p)
    save_json(graph_data, args.out)
    print(f"Generated import graph: {graph_data['file_count']} files, {graph_data['import_edge_count']} edges.")

if __name__ == "__main__":
    main()
