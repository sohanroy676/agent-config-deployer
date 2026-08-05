"""Tests for the per-file content pages logic (ContentPageState)."""

from ui.wizard_steps import ContentPageState

FILES = ["AGENTS.md", "tech-stack.md", "architecture.md"]
DESCRIPTIONS = {
    "AGENTS.md": "Short summary.",
    "tech-stack.md": "Stack details.",
    "architecture.md": "Architecture details.",
}


def test_state_starts_on_first_file():
    state = ContentPageState(FILES, DESCRIPTIONS)
    assert state.current_filename == "AGENTS.md"
    assert state.current_description == "Short summary."
    assert state.is_first
    assert not state.is_last


def test_state_go_next_advances():
    state = ContentPageState(FILES, DESCRIPTIONS)
    assert state.go_next() is True
    assert state.current_filename == "tech-stack.md"
    assert state.current_description == "Stack details."
    assert not state.is_first
    assert not state.is_last


def test_state_go_next_at_last_returns_false():
    state = ContentPageState(FILES, DESCRIPTIONS)
    state.index = len(FILES) - 1
    assert state.is_last
    assert state.go_next() is False
    assert state.current_filename == "architecture.md"


def test_state_go_back_at_first_returns_false():
    state = ContentPageState(FILES, DESCRIPTIONS)
    assert state.go_back() is False
    assert state.current_filename == "AGENTS.md"


def test_state_save_and_restore():
    state = ContentPageState(FILES, DESCRIPTIONS)
    state.save_current("agents content")
    assert state.content_map["AGENTS.md"] == "agents content"


def test_state_missing_description_defaults_empty():
    state = ContentPageState(FILES, {})
    assert state.current_description == ""


def test_state_full_flow():
    """Navigate through all pages, saving content, and verify the map."""
    state = ContentPageState(FILES, DESCRIPTIONS)
    state.save_current("agents content")
    state.go_next()  # -> tech-stack.md
    state.save_current("stack content")
    state.go_next()  # -> architecture.md
    state.save_current("arch content")

    assert state.content_map == {
        "AGENTS.md": "agents content",
        "tech-stack.md": "stack content",
        "architecture.md": "arch content",
    }
    assert state.is_last
