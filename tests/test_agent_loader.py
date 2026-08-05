"""Tests for core/agent_loader.py."""

import json

import pytest

from core import agent_loader
from core.agent_loader import AgentConfigError, get_agent, list_agents, load_prompt


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
