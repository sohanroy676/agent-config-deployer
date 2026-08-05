"""Tests for core/conflict_resolver.py."""

import pytest

from core.conflict_resolver import (
    Conflict,
    ConflictReport,
    detect_conflicts,
    record_decision,
    resolve_plan,
)


def test_detect_conflicts_reports_existing_files(tmp_path):
    existing = tmp_path / "existing.txt"
    existing.write_text("hello", encoding="utf-8")
    missing = tmp_path / "missing.txt"

    report = detect_conflicts(tmp_path, [existing, missing])

    assert report.has_conflicts
    assert len(report.conflicts) == 1
    assert report.conflicts[0].path == existing
    assert not report.conflicts[0].is_dir


def test_detect_conflicts_reports_existing_dirs(tmp_path):
    existing_dir = tmp_path / "subdir"
    existing_dir.mkdir()

    report = detect_conflicts(tmp_path, [existing_dir])

    assert report.conflicts[0].is_dir


def test_detect_conflicts_no_conflicts(tmp_path):
    missing = tmp_path / "missing.txt"
    report = detect_conflicts(tmp_path, [missing])
    assert not report.has_conflicts
    assert report.conflicts == []


def test_record_decision_valid_choices(tmp_path):
    report = ConflictReport(conflicts=[Conflict(path=tmp_path / "a.txt")])
    record_decision(report, tmp_path / "a.txt", "overwrite")
    record_decision(report, tmp_path / "a.txt", "skip")
    record_decision(report, tmp_path / "a.txt", "merge")
    assert report.decisions[str(tmp_path / "a.txt")] == "merge"


def test_record_decision_rejects_invalid_choice(tmp_path):
    report = ConflictReport(conflicts=[Conflict(path=tmp_path / "a.txt")])
    with pytest.raises(ValueError):
        record_decision(report, tmp_path / "a.txt", "delete")


def test_resolve_plan_respects_decisions(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    c = tmp_path / "c.txt"
    report = ConflictReport(
        conflicts=[Conflict(path=a), Conflict(path=b), Conflict(path=c)]
    )
    record_decision(report, a, "overwrite")
    record_decision(report, b, "skip")
    record_decision(report, c, "merge")

    plan = resolve_plan(report)

    assert a in plan
    assert b not in plan
    assert c in plan


def test_resolve_plan_defaults_to_overwrite_when_no_decision(tmp_path):
    a = tmp_path / "a.txt"
    report = ConflictReport(conflicts=[Conflict(path=a)])
    plan = resolve_plan(report)
    assert plan == [a]


def test_resolve_plan_empty_when_no_conflicts(tmp_path):
    report = ConflictReport()
    assert resolve_plan(report) == []
