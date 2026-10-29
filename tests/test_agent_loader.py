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
    for path, config in _real_agent_configs():
        template = REPO_ROOT / config["base_template_path"]
        ci_path = template / "ci-template" / ".github" / "workflows" / "ci.yml"
        assert ci_path.is_file(), f"{path.name}: ci.yml template missing"

        content = ci_path.read_text(encoding="utf-8")
        for marker in ("INSTALL_CMD", "LINT_CMD", "FORMAT_CMD", "TEST_CMD", "matrix"):
            assert (
                marker in content
            ), f"{path.name}: ci.yml is missing configurability marker: {marker}"


def test_real_agents_list_includes_cline_and_claude_code():
    names = {agent["name"] for agent in list_agents()}
    assert {"Cline", "Claude Code"} <= names


def test_real_agent_paths_stay_inside_template_and_project():
    """No `..` or absolute paths in base_files/project_specific_files: sources
    must stay inside the template folder, destinations inside the project."""
    for path, config in _real_agent_configs():
        structure = config["structure"]
        for section in ("base_files", "project_specific_files"):
            for src, dst in structure.get(section, {}).items():
                for rel in (src, dst):
                    p = Path(rel)
                    assert not p.is_absolute(), f"{path.name}: absolute path {rel}"
                    assert ".." not in p.parts, f"{path.name}: '..' in path {rel}"


# Files that must stay byte-identical between the Cline and Claude Code
# templates (template-relative path in cline -> path in claude-code).
_SHARED_TEMPLATE_FILES = {
    **{
        f".clinerules-base/{n}": f"rules/{n}"
        for n in (
            "01-security.md",
            "02-commit-style.md",
            "03-testing.md",
            "04-code-quality-review.md",
            "05-git-workflow.md",
            "06-session-efficiency.md",
        )
    },
    **{
        f"memory-bank-template/{n}": f"memory-bank-template/{n}"
        for n in (
            "activeContext.md",
            "progress.md",
            "projectBrief.md",
            "systemPatterns.md",
        )
    },
    **{
        f"project-specific-template/{n}": f"project-specific-template/{n}"
        for n in ("CHANGELOG.md", "ROADMAP.md", "architecture.md", "tech-stack.md")
    },
    "ci-template/.github/workflows/ci.yml": "ci-template/.github/workflows/ci.yml",
    "ci-template/.github/dependabot.yml": "ci-template/.github/dependabot.yml",
    "docs-adr-template/adr-template.md": "docs-adr-template/adr-template.md",
    ".gitignore": ".gitignore",
}


def test_shared_template_files_have_not_drifted():
    cline = REPO_ROOT / "templates" / "cline"
    claude = REPO_ROOT / "templates" / "claude-code"
    for src, dst in _SHARED_TEMPLATE_FILES.items():
        assert (cline / src).read_bytes() == (
            claude / dst
        ).read_bytes(), (
            f"templates/claude-code/{dst} drifted from templates/cline/{src}"
        )


def _claude_code_config() -> dict:
    return _load_agent_file(REPO_ROOT / "agents" / "claude_code.json")


def test_claude_code_has_no_agents_md_or_cline_references():
    config = _claude_code_config()
    structure = config["structure"]
    assert "AGENTS.md" not in structure["project_specific_files"]
    template = REPO_ROOT / config["base_template_path"]
    for f in template.rglob("*"):
        if f.is_file() and f.name != "README.md":  # README is not deployed
            assert (
                "cline" not in f.read_text(encoding="utf-8").lower()
            ), f"{f.relative_to(template)} mentions Cline"


def test_claude_code_md_imports_resolve_to_deployed_files():
    """Every @import in the deployed CLAUDE.md must name a file the agent
    config actually deploys, and the auto-loaded rules must not be imported."""
    import re

    config = _claude_code_config()
    structure = config["structure"]
    deployed = set(structure["base_files"].values()) | set(
        structure["project_specific_files"].values()
    )
    text = (REPO_ROOT / config["base_template_path"] / "CLAUDE.md").read_text(
        encoding="utf-8"
    )
    imports = re.findall(r"^@(\S+)$", text, flags=re.MULTILINE)
    assert imports, "CLAUDE.md template has no @imports"
    for target in imports:
        assert target in deployed, f"CLAUDE.md imports undeployed file: {target}"
        assert not target.startswith(
            ".claude/rules/"
        ), f"{target} is auto-loaded; importing it would load it twice"


def test_claude_code_commands_have_description_frontmatter():
    config = _claude_code_config()
    template = REPO_ROOT / config["base_template_path"]
    commands = sorted((template / "commands").glob("*.md"))
    assert {c.stem for c in commands} == {"commit", "debug", "new-feature"}
    for cmd in commands:
        lines = cmd.read_text(encoding="utf-8").splitlines()
        assert lines[0] == "---", f"{cmd.name}: missing frontmatter"
        end = lines.index("---", 1)
        assert any(l.startswith("description:") for l in lines[1:end]), cmd.name


def test_claude_code_settings_template_denies_secrets_and_asks_on_git():
    import json

    config = _claude_code_config()
    settings_path = REPO_ROOT / config["base_template_path"] / "settings.json"
    perms = json.loads(settings_path.read_text(encoding="utf-8"))["permissions"]
    assert "Read(./.env)" in perms["deny"]
    for cmd in ("git push", "git reset --hard", "git rebase"):
        assert any(cmd in rule for rule in perms["ask"]), f"no ask rule for {cmd}"
