"""Tests for core/agent_loader.py."""

import json
from pathlib import Path

import pytest

from core import agent_loader
from core.agent_loader import (
    AgentConfigError,
    _load_agent_file,
    get_agent,
    list_agents,
    load_prompt,
)


def test_list_agents_returns_agents(monkeypatch, tmp_path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "cline.json").write_text(
        json.dumps({"name": "Cline", "structure": {}}), encoding="utf-8"
    )
    monkeypatch.setattr(agent_loader, "AGENTS_DIR", agents_dir)

    agents = list_agents()

    assert len(agents) == 1
    assert agents[0]["name"] == "Cline"


def test_list_agents_empty_when_dir_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(agent_loader, "AGENTS_DIR", tmp_path / "nonexistent")
    assert list_agents() == []


def test_list_agents_skips_non_json(monkeypatch, tmp_path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "notes.txt").write_text("not json", encoding="utf-8")
    monkeypatch.setattr(agent_loader, "AGENTS_DIR", agents_dir)
    assert list_agents() == []


def test_get_agent_found(monkeypatch, tmp_path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "cline.json").write_text(
        json.dumps({"name": "Cline", "structure": {}}), encoding="utf-8"
    )
    monkeypatch.setattr(agent_loader, "AGENTS_DIR", agents_dir)

    agent = get_agent("cline")
    assert agent["name"] == "Cline"


def test_get_agent_not_found(monkeypatch, tmp_path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "cline.json").write_text(
        json.dumps({"name": "Cline", "structure": {}}), encoding="utf-8"
    )
    monkeypatch.setattr(agent_loader, "AGENTS_DIR", agents_dir)

    with pytest.raises(AgentConfigError):
        get_agent("claude")


def test_malformed_json_raises(monkeypatch, tmp_path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "bad.json").write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(agent_loader, "AGENTS_DIR", agents_dir)

    with pytest.raises(AgentConfigError):
        list_agents()


def test_missing_name_field_raises(monkeypatch, tmp_path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "bad.json").write_text(
        json.dumps({"structure": {}}), encoding="utf-8"
    )
    monkeypatch.setattr(agent_loader, "AGENTS_DIR", agents_dir)

    with pytest.raises(AgentConfigError):
        list_agents()


def test_load_prompt_returns_content(tmp_path):
    template = tmp_path / "template"
    template.mkdir()
    (template / "prompt.md").write_text("Copy me", encoding="utf-8")
    agent = {"name": "Cline", "base_template_path": str(template)}

    assert load_prompt(agent) == "Copy me"


def test_load_prompt_missing_file_raises(tmp_path):
    template = tmp_path / "template"
    template.mkdir()
    agent = {"name": "Cline", "base_template_path": str(template)}

    with pytest.raises(AgentConfigError):
        load_prompt(agent)


def test_load_prompt_missing_template_dir_raises(tmp_path):
    agent = {"name": "Cline", "base_template_path": str(tmp_path / "nonexistent")}

    with pytest.raises(AgentConfigError):
        load_prompt(agent)


def test_load_prompt_uses_override_path(tmp_path):
    default = tmp_path / "default"
    default.mkdir()
    (default / "prompt.md").write_text("Default prompt", encoding="utf-8")
    override = tmp_path / "override"
    override.mkdir()
    (override / "prompt.md").write_text("Override prompt", encoding="utf-8")
    agent = {"name": "Cline", "base_template_path": str(default)}

    assert load_prompt(agent, base_template_path=override) == "Override prompt"


def test_load_prompt_override_missing_file_raises(tmp_path):
    default = tmp_path / "default"
    default.mkdir()
    (default / "prompt.md").write_text("Default prompt", encoding="utf-8")
    override = tmp_path / "override"
    override.mkdir()
    agent = {"name": "Cline", "base_template_path": str(default)}

    with pytest.raises(AgentConfigError):
        load_prompt(agent, base_template_path=override)


# ---------------------------------------------------------------------------
# Agent config integrity (against the real agents/*.json files)
# ---------------------------------------------------------------------------
# The real agent configs are the source of truth for what gets deployed.
# These tests fail loudly if a config references a template file that doesn't
# exist or forgets a UI description, so wiring gaps are caught here instead of
# at deploy time.
REPO_ROOT = Path(__file__).resolve().parent.parent


def _real_agent_configs() -> list[tuple[Path, dict]]:
    agents_dir = REPO_ROOT / "agents"
    configs = []
    for path in sorted(agents_dir.glob("*.json")):
        configs.append((path, _load_agent_file(path)))
    return configs


def test_real_agent_configs_have_template_folder():
    """Every agent's base_template_path must point to an existing folder."""
    for path, config in _real_agent_configs():
        template = REPO_ROOT / config["base_template_path"]
        assert template.is_dir(), (
            f"{path.name}: base_template_path '{config['base_template_path']}' "
            f"does not exist"
        )


def test_real_agent_base_files_resolve_to_existing_templates():
    """Every base_files source must resolve to a real file under the template."""
    for path, config in _real_agent_configs():
        template = REPO_ROOT / config["base_template_path"]
        base_files = config.get("structure", {}).get("base_files", {})
        assert base_files, f"{path.name}: expected at least one base file"
        for src_rel in base_files:
            src = template / src_rel
            assert src.is_file(), f"{path.name}: base file source missing: {src_rel}"


def test_real_agent_project_files_have_descriptions():
    """Every project-specific file key needs a UI-facing description."""
    for path, config in _real_agent_configs():
        structure = config.get("structure", {})
        project_files = structure.get("project_specific_files", {})
        descriptions = structure.get("file_descriptions", {})
        assert project_files, f"{path.name}: expected project-specific files"
        for key in project_files:
            assert key in descriptions, (
                f"{path.name}: project-specific file '{key}' "
                f"has no file_descriptions entry"
            )


def test_real_agent_prompt_resolves():
    """Every agent's prompt.md must be readable so the Prompt step works."""
    for path, config in _real_agent_configs():
        prompt_text = load_prompt(config)
        assert prompt_text.strip(), f"{path.name}: prompt.md is empty"


def test_real_ci_template_is_configurable():
    """The deployed ci.yml must keep its configurability markers so users can
    adapt it to their stack without rewriting the workflow."""
    config = _load_agent_file(REPO_ROOT / "agents" / "cline.json")
    template = REPO_ROOT / config["base_template_path"]
    ci_path = template / "ci-template" / ".github" / "workflows" / "ci.yml"
    assert ci_path.is_file(), "ci.yml template missing"

    content = ci_path.read_text(encoding="utf-8")
    for marker in ("INSTALL_CMD", "LINT_CMD", "FORMAT_CMD", "TEST_CMD", "matrix"):
        assert marker in content, f"ci.yml is missing configurability marker: {marker}"
