"""
investigate_statuses.py – print every capsule status in all runs.
Run as: python scripts/investigate_statuses.py
"""
import json
from collections import Counter
from pathlib import Path

runs_dir = Path(__file__).resolve().parent.parent / "assets" / "runs"

all_caps = []
for run_dir in sorted(runs_dir.iterdir()):
    if not run_dir.is_dir():
        continue
    cap_dir = run_dir / "capsules"
    if not cap_dir.is_dir():
        continue
    for cap_f in sorted(cap_dir.glob("capsule-*.json")):
        try:
            d = json.loads(cap_f.read_text(encoding="utf-8"))
            all_caps.append({
                "run": run_dir.name,
                "dep": d.get("dependency", {}).get("name", "?"),
                "status": d.get("status", "MISSING"),
                "type": d.get("capsule_type", "?"),
                "status_reason": d.get("status_reason", ""),
            })
        except Exception as e:
            all_caps.append({"run": run_dir.name, "dep": cap_f.name, "status": f"ERROR:{e}", "type": "?"})

print(f"Total capsules: {len(all_caps)}")
print("Status distribution:", dict(Counter(c["status"] for c in all_caps)))
print()
print(f"{'RUN':35} {'DEP':20} {'STATUS':20} {'TYPE'}")
print("-" * 90)
for c in all_caps:
    print(f"  {c['run'][:33]:33} {c['dep']:20} {c['status']:20} {c['type']}")
