import json
import os
from pathlib import Path


def load_run_json(run_dir: str | Path) -> dict | None:
    """
    Load run.json from a run directory.
    Returns the dict on success, or None if the file is absent or malformed.
    Never derives any information (especially repo_url) from the folder name.
    """
    p = Path(run_dir) / "run.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def list_runs(runs_dir: str | Path | None = None) -> list[dict]:
    """
    Finds all valid run directories in assets/runs/.
    Returns a list of dicts: [{'run_id': str, 'path': Path, 'manifest': dict|None, 'capsules_count': int, 'timestamp': str}]
    Sorted by timestamp descending.
    """
    base_dir = Path(__file__).resolve().parent.parent
    if runs_dir is not None:
        p = Path(runs_dir)
        if not p.is_absolute():
            p = base_dir / p
    else:
        p = base_dir / "assets" / "runs"

    if not p.is_dir():
        return []

    runs = []
    for sub in p.iterdir():
        if not sub.is_dir():
            continue
        # A run directory has either manifest.json or a capsules/ folder
        manifest_p = sub / "manifest.json"
        capsules_dir = sub / "capsules"
        capsules = list(capsules_dir.glob("*.json")) if capsules_dir.is_dir() else list(sub.glob("capsule-*.json"))
        
        manifest_data = None
        timestamp = "N/A"
        if manifest_p.exists():
            try:
                manifest_data = json.loads(manifest_p.read_text(encoding="utf-8"))
                timestamp = manifest_data.get("generated_at", "N/A")
            except Exception:
                pass
        elif capsules:
            try:
                first_cap = json.loads(capsules[0].read_text(encoding="utf-8"))
                timestamp = first_cap.get("generated_at", "N/A")
            except Exception:
                pass

        # Load run.json metadata (authoritative source for display info)
        run_meta = load_run_json(sub)

        # Derive repo_url ONLY from run.json or capsule target_repo — never from folder name
        repo_url: str | None = None
        display_name: str | None = None
        mode: str | None = None
        sealed_at: str | None = None
        if run_meta:
            repo_url = run_meta.get("repo_url") or None
            display_name = run_meta.get("display_name") or None
            mode = run_meta.get("mode") or None
            sealed_at = run_meta.get("sealed_at") or None
        if not repo_url and capsules:
            # Fallback: read from first capsule's target_repo.url — only if it starts with https://
            try:
                first_cap = json.loads(capsules[0].read_text(encoding="utf-8"))
                candidate = first_cap.get("target_repo", {}).get("url", "")
                if candidate.startswith("https://"):
                    repo_url = candidate
            except Exception:
                pass

        if capsules or manifest_p.exists():
            runs.append({
                "run_id": sub.name,
                "path": sub,
                "manifest": manifest_data,
                "capsules_count": len(capsules),
                "timestamp": timestamp,
                # Metadata from run.json (may be None if absent)
                "repo_url": repo_url,
                "display_name": display_name,
                "mode": mode,
                "sealed_at": sealed_at,
            })

    # Sort descending by timestamp or run_id
    runs.sort(key=lambda r: (r["timestamp"], r["run_id"]), reverse=True)
    return runs


def load_capsules_from_run(run_dir: str | Path) -> list[dict]:
    """
    Load all capsule JSONs from a run's capsules/ sub-directory.
    Files inside <run>/capsules/archive/ are excluded so Overview counts are clean.
    """
    p = Path(run_dir)
    if not p.is_dir():
        return []

    caps_p = p / "capsules"
    target_p = caps_p if caps_p.is_dir() else p
    archive_p = target_p / "archive"

    capsules = []
    for f in sorted(target_p.glob("*.json")):
        # Exclude anything inside archive/
        try:
            f.relative_to(archive_p)
            continue   # inside archive – skip
        except ValueError:
            pass
        if f.name in ("manifest.json",) or f.name.startswith("scan"):
            continue
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                if isinstance(data, dict) and "capsule_id" in data:
                    capsules.append(data)
        except Exception:
            pass
    return capsules


def load_manifest_from_run(run_dir: str | Path) -> dict | None:
    """Load manifest.json from a specific run directory."""
    p = Path(run_dir) / "manifest.json"
    if not p.is_file():
        return None
    try:
        with open(p, "r", encoding="utf-8") as fp:
            return json.load(fp)
    except Exception:
        return None


def load_capsules(capsules_dir: str | Path | None = None) -> list[dict]:
    """Backward compatibility: load capsules from runs or capsules folder."""
    base_dir = Path(__file__).resolve().parent.parent
    if capsules_dir is not None:
        p = Path(capsules_dir)
        if not p.is_absolute():
            p = base_dir / p
    else:
        runs_p = base_dir / "assets" / "runs"
        caps_p = base_dir / "assets" / "capsules"
        p = runs_p if runs_p.is_dir() else caps_p

    if not p.is_dir():
        return []

    json_files = list(p.glob("**/capsules/*.json")) or list(p.rglob("capsule-*.json")) or list(p.glob("*.json"))
    capsules = []
    for f in sorted(json_files):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                if isinstance(data, dict) and "capsule_id" in data:
                    capsules.append(data)
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
    """Load raw text of an evidence file safely."""
    p = Path(file_path)
    if not p.is_file():
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def parse_run_log(log_path: str | Path) -> dict:
    """
    Parses a run.log file containing JSON line progress and plain text lines.
    Returns:
    {
        'lines': list[str],
        'events': list[dict],
        'status': 'complete' | 'error' | 'running',
        'final_run_dir': str | None,
        'capsules': list[str],
        'error_message': str | None
    }
    """
    p = Path(log_path)
    if not p.is_file():
        return {
            "lines": [],
            "events": [],
            "status": "running",
            "final_run_dir": None,
            "capsules": [],
            "error_message": None
        }

    try:
        content = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {
            "lines": [],
            "events": [],
            "status": "error",
            "final_run_dir": None,
            "capsules": [],
            "error_message": str(e)
        }

    raw_lines = [line.strip() for line in content.splitlines() if line.strip()]
    events = []
    status = "running"
    final_run_dir = None
    capsules = []
    error_message = None

    for line in raw_lines:
        try:
            item = json.loads(line)
            events.append(item)
            p_step = item.get("step")
            p_status = item.get("status")
            p_msg = item.get("message", "")
            p_data = item.get("data", {})

            if "run_dir" in p_data:
                final_run_dir = p_data["run_dir"]
            if "capsules" in p_data:
                capsules = p_data["capsules"]

            if p_status in ("completed", "complete") and p_step in ("pipeline", "cache"):
                status = "complete"
            elif p_status in ("error", "unsupported", "failed"):
                status = "error"
                error_message = p_msg
        except Exception:
            if "[DONE]" in line:
                status = "complete"
            elif "error:" in line.lower() or "exception" in line.lower():
                status = "error"
                error_message = line

    return {
        "lines": raw_lines,
        "events": events,
        "status": status,
        "final_run_dir": final_run_dir,
        "capsules": capsules,
        "error_message": error_message
    }


def get_last_run_summary(runs_dir: str | Path | None = None) -> dict | None:
    """
    Reads the newest run directory and returns its summary based on run.log and manifest.json.
    Returns:
    {
        'run_id': str,
        'path': Path,
        'status': 'complete' | 'failed' | 'still running',
        'manifest': dict | None,
        'capsules_count': int,
        'timestamp': str,
        'log_info': dict
    }
    """
    base_dir = Path(__file__).resolve().parent.parent
    p = Path(runs_dir) if runs_dir else base_dir / "assets" / "runs"
    if not p.is_dir():
        return None

    run_dirs = [d for d in p.iterdir() if d.is_dir()]
    if not run_dirs:
        return None

    # Sort by mtime descending
    run_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    newest = run_dirs[0]

    log_p = newest / "run.log"
    manifest_p = newest / "manifest.json"
    manifest_data = None
    if manifest_p.is_file():
        try:
            manifest_data = json.loads(manifest_p.read_text(encoding="utf-8"))
        except Exception:
            pass

    log_info = parse_run_log(log_p) if log_p.is_file() else {
        "status": "complete" if manifest_p.is_file() else "still running",
        "lines": [],
        "events": [],
        "error_message": None
    }

    status_str = "still running"
    if manifest_p.is_file() or log_info.get("status") == "complete":
        status_str = "complete"
    elif log_info.get("status") == "error":
        status_str = "failed"

    capsules_dir = newest / "capsules"
    capsules = list(capsules_dir.glob("*.json")) if capsules_dir.is_dir() else list(newest.glob("capsule-*.json"))
    ts = manifest_data.get("generated_at", "N/A") if manifest_data else "N/A"

    return {
        "run_id": newest.name,
        "path": newest,
        "status": status_str,
        "manifest": manifest_data,
        "capsules_count": len(capsules),
        "timestamp": ts,
        "log_info": log_info
    }


def count_capsule_statuses(capsules: list[dict]) -> dict[str, int]:
    """
    Compute counts for every known capsule status.

    Standard statuses (tested runs):  verified, unverified, not_run, not_testable,
                                       no_valid_proposal, failed
    Static-run additional statuses:   no_action
    Fallback bucket:                   other  (status value not in the above set)

    The sum of all values is guaranteed to equal len(capsules).
    The viewer's Overview uses this to populate its status table.
    """
    known_statuses = [
        "verified",
        "unverified",
        "not_run",
        "not_testable",
        "no_valid_proposal",
        "failed",
        "no_action",   # static runs: healthy/remove deps – no model call, no tests
    ]
    counts: dict[str, int] = {s: 0 for s in known_statuses}
    counts["other"] = 0

    for c in capsules:
        st = c.get("status", "")
        if st in counts:
            counts[st] += 1
        else:
            counts["other"] += 1

    return counts



