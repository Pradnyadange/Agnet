"""
deduplicate_capsules.py  –  keep exactly one capsule per dependency per run folder.
Older duplicates are moved to <run>/archive/ (not deleted).
Manifest is regenerated.  verify_capsule.py is re-run if available.

Usage:
    python scripts/deduplicate_capsules.py [--runs-dir assets/runs] [--dry-run]

Counts before/after are printed for every run that has duplicates.
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from common import compute_sha256_file, get_utc_iso_timestamp, load_json, save_json


def deduplicate_run(run_dir: Path, dry_run: bool = False) -> dict:
    """
    Deduplicate capsules inside a single run directory.
    Returns summary dict with before/after counts.
    """
    capsules_dir = run_dir / "capsules"
    if not capsules_dir.is_dir():
        return {}

    # Load all capsule files and group by dep name
    from collections import defaultdict
    dep_to_files: dict[str, list[tuple[str, Path]]] = defaultdict(list)

    for cap_f in sorted(capsules_dir.glob("capsule-*.json")):
        try:
            d = json.loads(cap_f.read_text(encoding="utf-8"))
            dep_name = d.get("dependency", {}).get("name", "")
            generated_at = d.get("generated_at", "")
            if dep_name:
                dep_to_files[dep_name].append((generated_at, cap_f))
        except Exception as exc:
            print(f"  WARN: cannot read {cap_f.name}: {exc}", file=sys.stderr)

    statuses_before: dict[str, int] = {}
    statuses_after: dict[str, int] = {}

    # Count statuses before
    for cap_f in sorted(capsules_dir.glob("capsule-*.json")):
        try:
            d = json.loads(cap_f.read_text(encoding="utf-8"))
            st = d.get("status", "MISSING")
            statuses_before[st] = statuses_before.get(st, 0) + 1
        except Exception:
            pass

    total_before = sum(len(v) for v in dep_to_files.values())
    archived_count = 0
    archive_dir = run_dir / "archive"

    for dep_name, file_list in dep_to_files.items():
        if len(file_list) <= 1:
            continue
        # Sort by generated_at descending; keep the newest (last in sorted)
        file_list.sort(key=lambda x: x[0])
        to_keep = file_list[-1][1]
        to_archive = [t[1] for t in file_list[:-1]]

        if not dry_run:
            archive_dir.mkdir(parents=True, exist_ok=True)

        for old_f in to_archive:
            if dry_run:
                print(f"  [dry-run] would archive {old_f.name}")
            else:
                dest = archive_dir / old_f.name
                shutil.move(str(old_f), str(dest))
                # Also move companion .md if it exists
                old_md = old_f.with_suffix(".md")
                if old_md.exists():
                    shutil.move(str(old_md), str(archive_dir / old_md.name))
                print(f"  archived  {old_f.name}")
                archived_count += 1

    if not dry_run and archived_count > 0:
        # Regenerate manifest.json (only non-archive files)
        manifest_file = run_dir / "manifest.json"
        files_to_hash = []
        for p in (run_dir / "capsules").glob("*.json"):
            files_to_hash.append(p)
        for p in (run_dir / "capsules").glob("*.md"):
            files_to_hash.append(p)
        if (run_dir / "scan.json").exists():
            files_to_hash.append(run_dir / "scan.json")
        for p in run_dir.glob("usage_*.json"):
            files_to_hash.append(p)
        evidence_dir = run_dir / "evidence"
        if evidence_dir.is_dir():
            for p in evidence_dir.rglob("*"):
                if p.is_file():
                    files_to_hash.append(p)

        run_folder_name = run_dir.name
        files_map = {}
        for p in sorted(files_to_hash):
            rel_p = f"assets/runs/{run_folder_name}/" + str(p.relative_to(run_dir)).replace("\\", "/")
            files_map[rel_p] = compute_sha256_file(p)

        manifest = {
            "manifest_version": "1.0",
            "run_id": run_folder_name,
            "generated_at": get_utc_iso_timestamp(),
            "files": files_map,
        }
        save_json(manifest, manifest_file)
        print(f"  manifest regenerated: {len(files_map)} files")

    # Count statuses after
    for cap_f in sorted(capsules_dir.glob("capsule-*.json")):
        try:
            d = json.loads(cap_f.read_text(encoding="utf-8"))
            st = d.get("status", "MISSING")
            statuses_after[st] = statuses_after.get(st, 0) + 1
        except Exception:
            pass

    total_after = sum(statuses_after.values())
    return {
        "run": run_dir.name,
        "before": statuses_before,
        "after": statuses_after,
        "total_before": total_before,
        "total_after": total_after,
        "archived": archived_count,
    }


def main():
    parser = argparse.ArgumentParser(description="Deduplicate capsules: keep newest per dep, archive older ones.")
    parser.add_argument("--runs-dir", default="assets/runs", help="Base runs directory")
    parser.add_argument("--run", default="", help="Restrict to a single run folder name")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be archived without moving files")
    args = parser.parse_args()

    runs_dir = Path(args.runs_dir)
    if not runs_dir.is_absolute():
        runs_dir = Path(__file__).resolve().parent.parent / runs_dir

    run_dirs = sorted(
        [d for d in runs_dir.iterdir() if d.is_dir() and (not args.run or d.name == args.run)]
    )
    print(f"Scanning {len(run_dirs)} run folder(s) in {runs_dir}\n")

    total_archived = 0
    for run_dir in run_dirs:
        summary = deduplicate_run(run_dir, dry_run=args.dry_run)
        if not summary:
            continue
        if summary["archived"] > 0 or args.dry_run:
            print(f"\n{'='*60}")
            print(f"Run: {summary['run']}")
            print(f"  Capsules BEFORE: {summary['total_before']}  {summary['before']}")
            print(f"  Capsules AFTER:  {summary['total_after']}   {summary['after']}")
            print(f"  Archived:        {summary['archived']}")
            total_archived += summary["archived"]

    print(f"\n{'='*60}")
    print(f"Done. Total archived: {total_archived}" + (" (dry-run, nothing moved)" if args.dry_run else "."))

    if total_archived > 0 and not args.dry_run:
        # Re-run verify_capsule.py if available
        verify_script = SCRIPTS_DIR / "verify_capsule.py"
        if verify_script.exists():
            print("\nRe-running verify_capsule.py...")
            result = subprocess.run(
                [sys.executable, str(verify_script), "--runs-dir", str(runs_dir)],
                capture_output=True, text=True
            )
            print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
            if result.returncode != 0:
                print(result.stderr[-1000:], file=sys.stderr)


if __name__ == "__main__":
    main()
