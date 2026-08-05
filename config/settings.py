"""Load and persist user settings from config/settings.json."""

import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "base_template_paths": {},
    "last_used": {"folder_path": "", "repo_url": "", "agent": ""},
}


def load_settings() -> dict:
    """Load settings from disk, falling back to defaults if missing/corrupt."""
    if not SETTINGS_PATH.exists():
        return json.loads(json.dumps(DEFAULT_SETTINGS))
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return json.loads(json.dumps(DEFAULT_SETTINGS))
    # Merge with defaults so new keys added later don't break old files.
    merged = json.loads(json.dumps(DEFAULT_SETTINGS))
    for key, value in data.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


def save_settings(settings: dict) -> None:
    """Persist settings to disk, creating the config dir if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


def get_base_template_path(agent_name: str) -> str:
    """Return the user-configured base template path for an agent, or empty string."""
    return load_settings().get("base_template_paths", {}).get(agent_name, "")


def set_base_template_path(agent_name: str, path: str) -> None:
    """Persist a base template path for an agent."""
    settings = load_settings()
    settings.setdefault("base_template_paths", {})[agent_name] = path
    save_settings(settings)
