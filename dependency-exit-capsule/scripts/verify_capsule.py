import argparse
import sys
from pathlib import Path

try:
    from common import compute_sha256_file, load_json
except ImportError:
    from scripts.common import compute_sha256_file, load_json

def verify_manifest(manifest_path: Path) -> tuple[bool, list[dict]]:
    """
    Recompute SHA-256 hashes of all files in manifest.json.
    Returns (all_match, list_of_checks).
    Each check has {path, expected, actual, match}.
    """
    if not manifest_path.exists():
        sys.stderr.write(f"Error: Manifest file not found at {manifest_path}\n")
        return False, []
        
    data = load_json(manifest_path)
    files = data.get("files", {})
    all_match = True
    checks = []
    
    for rel_path, expected_hash in files.items():
        file_p = Path(rel_path)
        if not file_p.exists():
            checks.append({
                "path": rel_path,
                "expected": expected_hash,
                "actual": "FILE_NOT_FOUND",
                "match": False
            })
            all_match = False
            continue
            
        actual_hash = compute_sha256_file(file_p)
        is_match = (actual_hash == expected_hash)
        if not is_match:
            all_match = False
        checks.append({
            "path": rel_path,
            "expected": expected_hash,
            "actual": actual_hash,
            "match": is_match
        })
        
    return all_match, checks

def main():
    parser = argparse.ArgumentParser(description="Stage 6: Verify capsule and evidence SHA-256 hashes.")
    parser.add_argument("manifest", help="Path to assets/manifest.json")
    args = parser.parse_args()
    
    manifest_p = Path(args.manifest)
    all_match, checks = verify_manifest(manifest_p)
    
    print(f"\n--- Integrity Manifest Verification: {manifest_p} ---")
    print(f"{'Status':<8} | {'File Path':<45} | Expected / Actual SHA-256")
    print("-" * 80)
    for c in checks:
        status_str = "MATCH" if c["match"] else "MISMATCH"
        print(f"{status_str:<8} | {c['path']:<45} | {c['expected'][:12]}... / {c['actual'][:12]}...")
        
    if all_match and checks:
        print("\nResult: VERIFIED (All hashes match).")
        sys.exit(0)
    else:
        print("\nResult: MISMATCH DETECTED (Integrity violation or missing files).")
        sys.exit(1)

if __name__ == "__main__":
    main()
