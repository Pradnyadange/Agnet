import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# Strict GitHub-only repo URL regex:
# Must start with https://github.com/
# Owner and repo name must be alphanumeric with hyphens/underscores/dots (cannot be dots only)
# No user credentials (e.g. user:pass@)
GITHUB_URL_REGEX = re.compile(
    r"^https://github\.com/([a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?)/([a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?)(?:\.git)?(?:/)?$"
)

# Limits
MAX_REPO_BYTES = 100 * 1024 * 1024  # 100 MB
MAX_REPO_FILES = 5000


def validate_github_url(url: str) -> tuple[bool, str, str]:
    """
    Validates GitHub URL.
    Returns (is_valid, owner, repo).
    Rejects:
    - Non-GitHub URLs
    - URLs with credentials (e.g., https://user:pass@github.com/...)
    - Dots-only repo or owner names (e.g. .. or .)
    """
    if not url or not isinstance(url, str):
        return False, "", ""
    url = url.strip()
    if "@" in url:
        return False, "", ""  # Rejects credentials in URL

    match = GITHUB_URL_REGEX.match(url)
    if not match:
        return False, "", ""

    owner, repo = match.group(1), match.group(2)
    if repo.endswith(".git"):
        repo = repo[:-4]
    # Check for dots-only or illegal path traversals
    if set(owner) == {"."} or set(repo) == {"."}:
        return False, "", ""

    return True, owner, repo


def check_directory_limits(dir_path: Path, max_bytes: int = MAX_REPO_BYTES, max_files: int = MAX_REPO_FILES) -> tuple[int, int]:
    """Inspect cloned or extracted directory for file count and byte limits."""
    total_files = 0
    total_bytes = 0

    for root, dirs, files in os.walk(dir_path):
        for f in files:
            fp = Path(root) / f
            try:
                # Do not follow symlinks if any
                if fp.is_symlink():
                    continue
                sz = fp.stat().st_size
                total_bytes += sz
                total_files += 1
                if total_files > max_files:
                    raise ValueError(f"Repository file count exceeds limit of {max_files} files (counted {total_files}+)")
                if total_bytes > max_bytes:
                    raise ValueError(f"Repository size exceeds limit of {max_bytes / (1024*1024):.1f} MB (counted {total_bytes / (1024*1024):.1f} MB)")
            except (OSError, FileNotFoundError):
                continue

    return total_files, total_bytes


def clone_github_repo(url: str, target_dir: Path) -> dict:
    """
    Clones a GitHub repository using git clone --depth 1.
    Strictly:
    - shell=False
    - GIT_TERMINAL_PROMPT=0 to prevent interactive hanging
    - Inspects file count and size limits after clone
    - Resolves commit sha
    - Never executes repository code
    """
    is_valid, owner, repo_name = validate_github_url(url)
    if not is_valid:
        raise ValueError(f"Invalid GitHub repository URL: {url}. Must be a valid https://github.com/owner/repo URL without credentials.")

    target_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"

    clone_cmd = [
        "git",
        "clone",
        "--depth", "1",
        f"https://github.com/{owner}/{repo_name}.git",
        str(target_dir.resolve())
    ]

    try:
        res = subprocess.run(
            clone_cmd,
            capture_output=True,
            text=True,
            shell=False,
            env=env,
            timeout=120
        )
        if res.returncode != 0:
            raise RuntimeError(f"git clone failed: {res.stderr.strip() or res.stdout.strip()}")
    except Exception as e:
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to clone repository: {e}")

    # Verify size and file count
    try:
        files_count, bytes_count = check_directory_limits(target_dir)
    except Exception as e:
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
        raise

    # Get HEAD commit SHA
    sha = "unknown"
    sha_res = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(target_dir.resolve()),
        capture_output=True,
        text=True,
        shell=False
    )
    if sha_res.returncode == 0:
        sha = sha_res.stdout.strip()

    return {
        "owner": owner,
        "repo": repo_name,
        "commit_sha": sha,
        "target_dir": str(target_dir.resolve()),
        "files_count": files_count,
        "bytes_count": bytes_count
    }


def extract_zip_repo(zip_path: Path, target_dir: Path) -> dict:
    """
    Extracts an uploaded ZIP archive with strict safety checks:
    - Path traversal / Zip-Slip rejection using os.path.commonpath
    - Rejects symlinks within the ZIP archive
    - Enforces file count and total unpacked byte limits
    - Never executes anything
    """
    if not zip_path.is_file():
        raise FileNotFoundError(f"ZIP file not found at {zip_path}")

    target_dir.mkdir(parents=True, exist_ok=True)
    target_abs = str(target_dir.resolve())

    total_bytes = 0
    total_files = 0

    with zipfile.ZipFile(zip_path, "r") as zf:
        infolist = zf.infolist()
        for member in infolist:
            # Check symlink flag in external attributes:
            # Unix symlink attribute has S_IFLNK (0o120000) in high 16 bits
            mode = member.external_attr >> 16
            if mode & 0o120000 == 0o120000:
                raise ValueError(f"Security error: ZIP file contains forbidden symbolic link '{member.filename}'")

            dest_path = (target_dir / member.filename).resolve()
            # Common path check for Zip Slip prevention
            try:
                common = os.path.commonpath([target_abs, str(dest_path)])
                if common != target_abs:
                    raise ValueError(f"Zip-Slip path traversal detected: '{member.filename}' resolves outside target directory")
            except ValueError:
                raise ValueError(f"Zip-Slip path traversal detected: '{member.filename}' resolves outside target directory")

            # Check size limits before extracting
            total_bytes += member.file_size
            if not member.is_dir():
                total_files += 1

            if total_bytes > MAX_REPO_BYTES:
                raise ValueError(f"Uncompressed ZIP size exceeds limit of {MAX_REPO_BYTES / (1024*1024):.1f} MB")
            if total_files > MAX_REPO_FILES:
                raise ValueError(f"ZIP member count exceeds limit of {MAX_REPO_FILES} files")

        # Safe extraction
        zf.extractall(target_dir)

    # Check if contents are nested inside a single root folder (typical for GitHub zip downloads: repo-main/)
    entries = [p for p in target_dir.iterdir() if p.name not in ("__MACOSX",)]
    if len(entries) == 1 and entries[0].is_dir():
        extracted_root = entries[0]
    else:
        extracted_root = target_dir

    return {
        "owner": "upload",
        "repo": zip_path.stem,
        "commit_sha": "uploaded_zip",
        "target_dir": str(extracted_root.resolve()),
        "files_count": total_files,
        "bytes_count": total_bytes
    }
