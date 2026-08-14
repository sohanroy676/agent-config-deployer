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


def test_deploy_base_files_ci_adr_checklist(tmp_path):
    """New base files (CI workflow, dependabot, ADR templates, checklist) deploy to correct locations."""
    template = tmp_path / "template"
    (template / "ci-template" / ".github" / "workflows").mkdir(parents=True)
    (template / "ci-template" / ".github" / "workflows" / "ci.yml").write_text(
        "name: CI\n", encoding="utf-8"
    )
    (template / "ci-template" / ".github" / "dependabot.yml").write_text(
        "version: 2\n", encoding="utf-8"
    )
    (template / "docs-adr-template").mkdir(parents=True)
    (template / "docs-adr-template" / "adr-template.md").write_text(
        "# ADR template\n", encoding="utf-8"
    )
    (
        template / "docs-adr-template" / "0001-record-architecture-decisions.md"
    ).write_text("# ADR-0001\n", encoding="utf-8")
    (template / "PRE-DEPLOY-CHECKLIST.md").write_text("# Checklist\n", encoding="utf-8")

    config = {
        "name": "Cline",
        "base_template_path": str(template),
        "structure": {
            "base_files": {
                "ci-template/.github/workflows/ci.yml": ".github/workflows/ci.yml",
                "ci-template/.github/dependabot.yml": ".github/dependabot.yml",
                "docs-adr-template/adr-template.md": "docs/adr/adr-template.md",
                "docs-adr-template/0001-record-architecture-decisions.md": "docs/adr/0001-record-architecture-decisions.md",
                "PRE-DEPLOY-CHECKLIST.md": "PRE-DEPLOY-CHECKLIST.md",
            }
        },
    }
    project = tmp_path / "project"
    project.mkdir()
    report = ConflictReport()

    written = deploy_base_files(config, template, project, report)

    assert (project / ".github" / "workflows" / "ci.yml").exists()
    assert (project / ".github" / "dependabot.yml").exists()
    assert (project / "docs" / "adr" / "adr-template.md").exists()
    assert (project / "docs" / "adr" / "0001-record-architecture-decisions.md").exists()
    assert (project / "PRE-DEPLOY-CHECKLIST.md").exists()
    assert len(written) == 5


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
