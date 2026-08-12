"""Copy base template files and write project-specific content into the target project.

This is the ONLY module that writes files into the target project folder.
"""

import shutil
from pathlib import Path

from core.conflict_resolver import ConflictReport


class DeployError(Exception):
    """Raised when a deployment operation fails."""


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _copy_file(src: Path, dst: Path) -> None:
    _ensure_parent(dst)
    shutil.copy2(src, dst)


def _merge_file(src: Path, dst: Path) -> None:
    """Append src content to dst if it's not already present (line-based dedupe)."""
    _ensure_parent(dst)
    if not dst.exists():
        shutil.copy2(src, dst)
        return
    existing = dst.read_text(encoding="utf-8")
    new_content = src.read_text(encoding="utf-8")
    if new_content in existing:
        return
    with open(dst, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write(new_content)


def deploy_base_files(
    agent_config: dict,
    base_template_path: Path,
    project_dir: Path,
    report: ConflictReport,
) -> list[Path]:
    """Copy base template files into project_dir per the agent's structure.

    Returns the list of files actually written. Respects the conflict report's
    decisions (overwrite/skip/merge). Merge is only applied to .gitignore.
    """
    base_template_path = Path(base_template_path)
    if not base_template_path.exists():
        raise DeployError(f"Base template path does not exist: {base_template_path}")

    written: list[Path] = []
    base_files = agent_config.get("structure", {}).get("base_files", {})
    for src_rel, dst_rel in base_files.items():
        src = base_template_path / src_rel
        dst = project_dir / dst_rel
        if not src.exists():
            raise DeployError(f"Template file missing: {src}")

        if dst.exists():
            choice = report.decisions.get(str(dst), "overwrite")
            if choice == "skip":
                continue
            if choice == "merge" and dst_rel == ".gitignore":
                _merge_file(src, dst)
                written.append(dst)
                continue
            # overwrite (or merge on a non-mergeable file) -> copy over
        _copy_file(src, dst)
        written.append(dst)
    return written


def deploy_project_specific_files(
    agent_config: dict,
    project_dir: Path,
    content_map: dict[str, str],
    report: ConflictReport,
) -> list[Path]:
    """Write user-provided project-specific content into the correct locations.

    content_map keys are the project-specific file keys from the agent config
    (e.g. "tech-stack.md"), values are the file contents as strings.
    Returns the list of files actually written.
    """
    written: list[Path] = []
    project_files = agent_config.get("structure", {}).get("project_specific_files", {})
    for key, dst_rel in project_files.items():
        content = content_map.get(key)
        if not content or not content.strip():
            # No content (or only whitespace) — skip so any pre-deployed
            # base template (e.g. ROADMAP.md) is left in place.
            continue
        dst = project_dir / dst_rel
        if dst.exists():
            choice = report.decisions.get(str(dst), "overwrite")
            if choice == "skip":
                continue
        _ensure_parent(dst)
        dst.write_text(content, encoding="utf-8")
        written.append(dst)
    return written
