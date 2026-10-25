import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def load_static_import_map() -> dict[str, list[str]]:
    """Loads fallback static mapping from references/package_import_map.json."""
    map_path = Path(__file__).resolve().parent.parent / "references" / "package_import_map.json"
    if map_path.exists():
        try:
            return json.loads(map_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "pyyaml": ["yaml"],
        "beautifulsoup4": ["bs4"],
        "python-dateutil": ["dateutil"]
    }


def get_import_names_from_wheel(package_name: str) -> list[str]:
    """
    Attempts to download a pure-python or any binary wheel using:
    pip download --no-deps --only-binary=:all: <package_name>
    and inspects top_level.txt or RECORD inside the wheel (.dist-info/).
    Never installs or runs the code.
    Returns list of import names.
    """
    norm_pkg = package_name.lower().replace("_", "-")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        cmd = [
            sys.executable,
            "-m", "pip", "download",
            "--no-deps",
            "--only-binary=:all:",
            "--dest", str(tmp_path),
            package_name
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode == 0:
                wheels = list(tmp_path.glob("*.whl"))
                if wheels:
                    whl_path = wheels[0]
                    with zipfile.ZipFile(whl_path, "r") as zf:
                        # 1. Look for top_level.txt
                        for name in zf.namelist():
                            if name.endswith(".dist-info/top_level.txt"):
                                content = zf.read(name).decode("utf-8", errors="replace")
                                imports = [line.strip() for line in content.splitlines() if line.strip()]
                                if imports:
                                    return imports
                        # 2. Look for RECORD or top-level py files/dirs
                        top_names = set()
                        for name in zf.namelist():
                            if ".dist-info/" in name or ".data/" in name:
                                continue
                            parts = name.split("/")
                            if parts[0].endswith(".py"):
                                top_names.add(parts[0][:-3])
                            elif len(parts) > 1 and parts[0]:
                                top_names.add(parts[0])
                        if top_names:
                            return sorted(list(top_names))
        except Exception:
            pass

    return []


def resolve_import_names(package_name: str) -> list[str]:
    """
    Resolves top-level Python import names for a package.
    Order of precedence:
    1. Wheel inspection via pip download --no-deps --only-binary=:all:
    2. Labelled static data file fallback (references/package_import_map.json)
    3. Normalised package name (replacing '-' with '_')
    """
    norm_pkg = package_name.lower().replace("_", "-")

    # 1. Try wheel inspection
    wheel_imports = get_import_names_from_wheel(norm_pkg)
    if wheel_imports:
        return wheel_imports

    # 2. Try static fallback
    static_map = load_static_import_map()
    if norm_pkg in static_map:
        return static_map[norm_pkg]

    # 3. Default normalized name
    return [norm_pkg.replace("-", "_")]
