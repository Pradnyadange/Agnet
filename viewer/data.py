import json
import os
from pathlib import Path

def load_capsules(capsules_dir: str = "assets/capsules") -> list[dict]:
    """Load all *.json capsules from assets/capsules."""
    p = Path(capsules_dir)
    capsules = []
    if not p.is_dir():
        return []
    for f in sorted(p.glob("*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                capsules.append(json.load(fp))
        except Exception:
            pass
    return capsules

def load_manifest(manifest_path: str = "assets/manifest.json") -> dict | None:
    """Load manifest.json if it exists."""
    p = Path(manifest_path)
    if not p.is_file():
        return None
    try:
        with open(p, "r", encoding="utf-8") as fp:
            return json.load(fp)
    except Exception:
        return None

def load_evidence_file(file_path: str) -> str | None:
    """Load the raw text of an evidence file."""
    p = Path(file_path)
    if not p.is_file():
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
