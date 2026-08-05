"""Detect existing files/folders that would be overwritten and ask the user how to proceed.

This module is pure decision logic — it never writes files and never auto-decides.
The UI layer is responsible for actually prompting the user and passing the choice back.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Conflict:
    """A single file/folder that already exists in the target project."""

    path: Path
    is_dir: bool = False


@dataclass
class ConflictReport:
    """All conflicts found for a planned deployment, plus the user's decisions."""

    conflicts: list[Conflict] = field(default_factory=list)
    decisions: dict[str, str] = field(
        default_factory=dict
    )  # path -> "overwrite"|"skip"|"merge"

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)


def detect_conflicts(project_dir: Path, planned_files: list[Path]) -> ConflictReport:
    """Return a report of which planned files already exist in project_dir.

    planned_files are absolute target paths. Only existing files/folders are reported.
    """
    report = ConflictReport()
    for target in planned_files:
        if target.exists():
            report.conflicts.append(Conflict(path=target, is_dir=target.is_dir()))
    return report


def record_decision(report: ConflictReport, path: Path, choice: str) -> None:
    """Record the user's choice for a given conflict path.

    choice must be one of: "overwrite", "skip", "merge".
    """
    if choice not in ("overwrite", "skip", "merge"):
        raise ValueError(f"Invalid choice: {choice}")
    report.decisions[str(path)] = choice


def resolve_plan(report: ConflictReport) -> list[Path]:
    """Return the list of target paths that should actually be written.

    - "overwrite" -> included
    - "skip" -> excluded
    - "merge" -> included (merge semantics are handled by the deployer)
    Paths with no recorded decision are included (no conflict = write it).
    """
    if not report.has_conflicts:
        return []
    result = []
    for conflict in report.conflicts:
        choice = report.decisions.get(str(conflict.path), "overwrite")
        if choice in ("overwrite", "merge"):
            result.append(conflict.path)
    return result
