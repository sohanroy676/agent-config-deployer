"""Tests for core/file_deployer.py."""

from pathlib import Path

import pytest

from core.conflict_resolver import Conflict, ConflictReport, record_decision
from core.file_deployer import (
    DeployError,
    deploy_base_files,
    deploy_project_specific_files,
)

AGENT_CONFIG = {
    "name": "Cline",
    "base_template_path": "templates/cline",
    "structure": {
        "base_files": {
            ".clinerules-base/01-security.md": ".clinerules/01-security.md",
            ".gitignore": ".gitignore",
        },
        "project_specific_files": {
            "AGENTS.md": "AGENTS.md",
            "tech-stack.md": "memory-bank/tech-stack.md",
            "ROADMAP.md": "ROADMAP.md",
        },
    },
}


def _make_template(tmp_path) -> Path:
    template = tmp_path / "template"
    (template / ".clinerules-base").mkdir(parents=True)
    (template / ".clinerules-base" / "01-security.md").write_text(
        "# security\n", encoding="utf-8"
    )
    (template / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    return template


def test_deploy_base_files_copies_into_structure(tmp_path):
    template = _make_template(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    report = ConflictReport()

    written = deploy_base_files(AGENT_CONFIG, template, project, report)

    assert (project / ".clinerules" / "01-security.md").exists()
    assert (project / ".gitignore").exists()
    assert len(written) == 2


def test_deploy_base_files_missing_template_raises(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    report = ConflictReport()
    with pytest.raises(DeployError):
        deploy_base_files(AGENT_CONFIG, tmp_path / "nonexistent", project, report)


def test_deploy_base_files_missing_template_file_raises(tmp_path):
    template = _make_template(tmp_path)
    (template / ".gitignore").unlink()
    project = tmp_path / "project"
    project.mkdir()
    report = ConflictReport()
    with pytest.raises(DeployError):
        deploy_base_files(AGENT_CONFIG, template, project, report)


def test_deploy_base_files_skip_existing(tmp_path):
    template = _make_template(tmp_path)
    project = tmp_path / "project"
    (project / ".clinerules").mkdir(parents=True)
    (project / ".clinerules" / "01-security.md").write_text(
        "existing", encoding="utf-8"
    )
    report = ConflictReport(
        conflicts=[Conflict(path=project / ".clinerules" / "01-security.md")]
    )
    record_decision(report, project / ".clinerules" / "01-security.md", "skip")

    written = deploy_base_files(AGENT_CONFIG, template, project, report)

    assert (project / ".clinerules" / "01-security.md").read_text(
        encoding="utf-8"
    ) == "existing"
    assert (project / ".clinerules" / "01-security.md") not in written


def test_deploy_base_files_overwrite_existing(tmp_path):
    template = _make_template(tmp_path)
    project = tmp_path / "project"
    (project / ".clinerules").mkdir(parents=True)
    (project / ".clinerules" / "01-security.md").write_text("old", encoding="utf-8")
    report = ConflictReport(
        conflicts=[Conflict(path=project / ".clinerules" / "01-security.md")]
    )
    record_decision(report, project / ".clinerules" / "01-security.md", "overwrite")

    deploy_base_files(AGENT_CONFIG, template, project, report)

    assert (project / ".clinerules" / "01-security.md").read_text(
        encoding="utf-8"
    ) == "# security\n"


def test_deploy_base_files_merge_gitignore(tmp_path):
    template = _make_template(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    (project / ".gitignore").write_text("venv/\n", encoding="utf-8")
    report = ConflictReport(conflicts=[Conflict(path=project / ".gitignore")])
    record_decision(report, project / ".gitignore", "merge")

    deploy_base_files(AGENT_CONFIG, template, project, report)

    content = (project / ".gitignore").read_text(encoding="utf-8")
    assert "venv/" in content
    assert "node_modules/" in content


def test_deploy_project_specific_files_writes_content(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    report = ConflictReport()
    content_map = {
        "AGENTS.md": "# AGENTS\n",
        "tech-stack.md": "# Tech Stack\n",
    }

    written = deploy_project_specific_files(AGENT_CONFIG, project, content_map, report)

    assert (project / "AGENTS.md").read_text(encoding="utf-8") == "# AGENTS\n"
    assert (project / "memory-bank" / "tech-stack.md").read_text(
        encoding="utf-8"
    ) == "# Tech Stack\n"
    assert len(written) == 2


def test_deploy_project_specific_files_skips_missing_content(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    report = ConflictReport()

    written = deploy_project_specific_files(AGENT_CONFIG, project, {}, report)

    assert written == []
    assert not (project / "AGENTS.md").exists()


def test_deploy_project_specific_files_skip_existing(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("keep me", encoding="utf-8")
    report = ConflictReport(conflicts=[Conflict(path=project / "AGENTS.md")])
    record_decision(report, project / "AGENTS.md", "skip")
    content_map = {"AGENTS.md": "new content"}

    deploy_project_specific_files(AGENT_CONFIG, project, content_map, report)

    assert (project / "AGENTS.md").read_text(encoding="utf-8") == "keep me"


def test_deploy_project_specific_files_skips_empty_content(tmp_path):
    """Empty content must not overwrite a pre-deployed base template (e.g. ROADMAP).

    The blank template is copied by deploy_base_files; if the user leaves the
    content page blank, that template must survive untouched.
    """
    project = tmp_path / "project"
    project.mkdir()
    (project / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    report = ConflictReport()
    content_map = {"ROADMAP.md": ""}

    written = deploy_project_specific_files(AGENT_CONFIG, project, content_map, report)

    assert written == []
    assert (project / "ROADMAP.md").read_text(encoding="utf-8") == "# Roadmap\n"


def test_deploy_project_specific_files_skips_whitespace_content(tmp_path):
    """Whitespace-only content must be treated like blank content."""
    project = tmp_path / "project"
    project.mkdir()
    (project / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    report = ConflictReport()
    content_map = {"ROADMAP.md": "   \n  "}

    written = deploy_project_specific_files(AGENT_CONFIG, project, content_map, report)

    assert written == []
    assert (project / "ROADMAP.md").read_text(encoding="utf-8") == "# Roadmap\n"


def test_deploy_project_specific_files_nonblank_overwrites_template(tmp_path):
    """Non-blank content must overwrite the pre-deployed template."""
    project = tmp_path / "project"
    project.mkdir()
    (project / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    report = ConflictReport()
    content_map = {"ROADMAP.md": "# My Plan\n\n## Now\n- Build X\n"}

    written = deploy_project_specific_files(AGENT_CONFIG, project, content_map, report)

    assert (project / "ROADMAP.md").read_text(
        encoding="utf-8"
    ) == "# My Plan\n\n## Now\n- Build X\n"
    assert (project / "ROADMAP.md") in written
