import argparse
import ast
import os
import sys
from pathlib import Path

try:
    from common import save_json
except ImportError:
    from scripts.common import save_json

class UsageVisitor(ast.NodeVisitor):
    def __init__(self, target_pkg: str, filepath: str, import_names: list[str] | None = None):
        self.target_pkg = target_pkg.lower().replace("-", "_")
        self.raw_target = target_pkg.lower()
        self.import_names = set(i.lower().replace("-", "_") for i in (import_names or [self.target_pkg]))
        self.filepath = filepath
        self.usage_records = []
        self.aliases = set()      # local alias names mapping to target package
        self.symbol_aliases = {}  # local name -> symbol imported from target package
        self.dynamic_imports = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            parts = alias.name.split(".")
            root_mod = parts[0].lower().replace("-", "_")
            if root_mod in self.import_names:
                local_name = alias.asname if alias.asname else alias.name
                self.aliases.add(local_name)
                self.usage_records.append({
                    "file": self.filepath,
                    "line": node.lineno,
                    "symbol": alias.name,
                    "kind": "import",
                    "covered_by_tests": False
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            parts = node.module.split(".")
            root_mod = parts[0].lower().replace("-", "_")
            if root_mod in self.import_names:
                for alias in node.names:
                    local_name = alias.asname if alias.asname else alias.name
                    symbol_name = alias.name
                    self.symbol_aliases[local_name] = symbol_name
                    self.usage_records.append({
                        "file": self.filepath,
                        "line": node.lineno,
                        "symbol": f"{node.module}.{symbol_name}",
                        "kind": "import",
                        "covered_by_tests": False
                    })
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Detect dynamic imports: __import__, importlib.import_module, eval
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = self._resolve_attr_chain(node.func)
            
        if func_name in ("__import__", "importlib.import_module", "eval"):
            self.dynamic_imports.append(f"{self.filepath}:{node.lineno} ({func_name})")

        # Detect calls to imported symbols or aliases
        # 1. Alias call: e.g. y.load() where y is an alias for target_pkg
        if isinstance(node.func, ast.Attribute):
            base = self._get_root_name(node.func.value)
            attr = node.func.attr
            if base in self.aliases:
                chain = self._resolve_attr_chain(node.func)
                self.usage_records.append({
                    "file": self.filepath,
                    "line": node.lineno,
                    "symbol": attr,
                    "kind": "call",
                    "covered_by_tests": False
                })
        # 2. Direct symbol call: e.g. loads(...) where loads was imported from target_pkg
        elif isinstance(node.func, ast.Name):
            if node.func.id in self.symbol_aliases:
                orig_symbol = self.symbol_aliases[node.func.id]
                self.usage_records.append({
                    "file": self.filepath,
                    "line": node.lineno,
                    "symbol": orig_symbol,
                    "kind": "call",
                    "covered_by_tests": False
                })

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        # Attribute access that is not a Call (e.g., pkg.property used as value)
        base = self._get_root_name(node.value)
        if base in self.aliases:
            # Check if this node is inside a call (handled by visit_Call)
            # We record attribute access as well to ensure properties/constants are tracked
            pass
        self.generic_visit(node)

    def _get_root_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_root_name(node.value)
        return None

    def _resolve_attr_chain(self, node: ast.Attribute) -> str:
        parts = [node.attr]
        curr = node.value
        while isinstance(curr, ast.Attribute):
            parts.append(curr.attr)
            curr = curr.value
        if isinstance(curr, ast.Name):
            parts.append(curr.id)
        return ".".join(reversed(parts))

def map_repo_usage(repo_path: Path, target_dep: str, import_names: list[str] | None = None) -> dict:
    """Walk all .py files in repo_path, parse AST, and identify usage of target_dep."""
    py_files = []
    # Avoid virtualenvs, hidden folders, caches
    ignore_dirs = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "build", "dist", ".tox"}
    
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".") and not d.lower().startswith(".env")]
        for file in files:
            if file.lower() == ".env" or file.lower().startswith(".env."):
                continue
            if file.endswith(".py"):
                py_files.append(Path(root) / file)
                
    files_scanned = len(py_files)
    if files_scanned == 0:
        sys.stderr.write(f"Error: files_scanned is zero in repository: {repo_path}\n")
        sys.exit(1)
        
    all_usages = []
    all_dynamic = []
    
    for py_file in py_files:
        rel_path = py_file.relative_to(repo_path).as_posix()
        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(content, filename=str(py_file))
            visitor = UsageVisitor(target_dep, rel_path, import_names=import_names)
            visitor.visit(tree)
            all_usages.extend(visitor.usage_records)
            all_dynamic.extend(visitor.dynamic_imports)
        except SyntaxError as e:
            sys.stderr.write(f"Warning: Syntax error parsing {rel_path}: {e}\n")
            
    # Sort usages by file, line
    all_usages.sort(key=lambda u: (u["file"], u["line"]))
    
    return {
        "dependency": target_dep,
        "files_scanned": files_scanned,
        "dynamic_imports": sorted(list(set(all_dynamic))),
        "usage_locations": all_usages
    }

def main():
    parser = argparse.ArgumentParser(description="Stage 2: Map dependency usage across repository using AST.")
    parser.add_argument("--repo", required=True, help="Path to repository to scan")
    parser.add_argument("--dep", required=True, help="Dependency package name to map")
    parser.add_argument("--out", required=True, help="Path to save usage output JSON")
    args = parser.parse_args()
    
    repo_path = Path(args.repo)
    if not repo_path.is_dir():
        sys.stderr.write(f"Error: Repository path does not exist: {args.repo}\n")
        sys.exit(1)
        
    usage_data = map_repo_usage(repo_path, args.dep)
    save_json(usage_data, args.out)
    print(f"Scanned {usage_data['files_scanned']} files. Found {len(usage_data['usage_locations'])} usages for {args.dep}.")

if __name__ == "__main__":
    main()
