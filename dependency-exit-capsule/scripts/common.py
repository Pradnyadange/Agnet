import os
import sys
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

def get_utc_iso_timestamp() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()

def compute_sha256_file(filepath: Path | str) -> str:
    """Compute the SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def compute_sha256_text(text: str) -> str:
    """Compute the SHA-256 hash of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def run_command(cmd: list[str], cwd: Path | str | None = None, env: dict | None = None) -> tuple[int, str, str]:
    """
    Run an external command and return (exit_code, stdout, stderr).
    Never raises an exception on non-zero exit codes.
    """
    current_env = os.environ.copy()
    if env:
        current_env.update(env)
    
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=current_env
    )
    return proc.returncode, proc.stdout, proc.stderr

def save_json(data: dict | list, filepath: Path | str, indent: int = 2) -> None:
    """Save data to a JSON file ensuring parent directories exist."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)

def load_json(filepath: Path | str) -> dict | list:
    """Load JSON from a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
