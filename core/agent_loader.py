"""Load agent configuration JSONs and expose available agents to the UI."""

import json
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"


class AgentConfigError(Exception):
    """Raised when an agent config file is missing or malformed."""


def _load_agent_file(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        raise AgentConfigError(
            f"Could not read agent config {path.name}: {exc}"
        ) from exc
    if not isinstance(data, dict) or "name" not in data:
        raise AgentConfigError(f"Agent config {path.name} is missing a 'name' field")
    return data


def list_agents() -> list[dict]:
    """Return a list of agent config dicts, one per JSON file in agents/."""
    if not AGENTS_DIR.exists():
        return []
    agents = []
    for path in sorted(AGENTS_DIR.glob("*.json")):
        agents.append(_load_agent_file(path))
    return agents


def get_agent(agent_name: str) -> dict:
    """Return the config dict for a named agent, or raise AgentConfigError."""
    for agent in list_agents():
        if agent["name"].lower() == agent_name.lower():
            return agent
    raise AgentConfigError(f"No agent named '{agent_name}' found")
