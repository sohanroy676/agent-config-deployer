"""Clone public GitHub repos into a target parent folder using the system git CLI."""

import subprocess
from pathlib import Path
from urllib.parse import urlparse


class GitCloneError(Exception):
    """Raised when a git clone operation fails."""


def clone_repo(repo_url: str, parent_dir: Path) -> Path:
    """Clone a public repo into parent_dir and return the resulting project folder.

    The repo name is derived from the URL's last path segment (minus .git).
    """
    parent_dir = Path(parent_dir)
    if not parent_dir.exists():
        raise GitCloneError(f"Parent folder does not exist: {parent_dir}")

    repo_name = _repo_name_from_url(repo_url)
    if not repo_name:
        raise GitCloneError(f"Could not determine repo name from URL: {repo_url}")

    target = parent_dir / repo_name
    if target.exists():
        raise GitCloneError(f"Target folder already exists: {target}")

    try:
        result = subprocess.run(
            ["git", "clone", repo_url, str(target)],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise GitCloneError(f"git clone failed: {exc}") from exc

    if result.returncode != 0:
        raise GitCloneError(f"git clone failed: {result.stderr.strip()}")

    return target


def _repo_name_from_url(repo_url: str) -> str:
    """Extract the repo folder name from a git URL (https or ssh)."""
    url = repo_url.rstrip("/").removesuffix(".git")

    # SSH form: git@github.com:user/repo
    if ":" in url and "@" in url:
        name = url.rsplit(":", 1)[-1].rsplit("/", 1)[-1]
        return name.strip()

    # HTTPS form: https://github.com/user/repo
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return ""
    return path.rsplit("/", 1)[-1].strip()
