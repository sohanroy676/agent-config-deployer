"""Tests for the pure state logic behind the redesigned UI components."""

from ui.components import StepIndicatorState
from ui.wizard_steps import ContentPageState

FILES = ["AGENTS.md", "tech-stack.md", "architecture.md"]
DESCRIPTIONS = {
    "AGENTS.md": "Short summary.",
    "tech-stack.md": "Stack details.",
    "architecture.md": "Architecture details.",
}


# ---------------------------------------------------------------------------
# StepIndicatorState
# ---------------------------------------------------------------------------
def test_step_indicator_state_properties():
    state = StepIndicatorState(["Source", "Agent", "Prompt"], current_index=1)
    assert state.total == 3
    assert state.is_completed(0)
    assert state.is_current(1)
    assert state.is_upcoming(2)


def test_step_indicator_state_boundaries():
    state = StepIndicatorState(["Source", "Agent", "Prompt"], current_index=0)
    assert not state.is_completed(0)
    assert not state.is_upcoming(0)
    assert state.is_upcoming(1)
    assert state.is_upcoming(2)


def test_step_indicator_state_last_step():
    state = StepIndicatorState(["Source", "Agent", "Prompt"], current_index=2)
    assert state.is_completed(0)
    assert state.is_completed(1)
    assert state.is_current(2)
    assert not state.is_upcoming(2)


def test_step_indicator_state_empty():
    state = StepIndicatorState([], current_index=0)
    assert state.total == 0


# ---------------------------------------------------------------------------
# ContentPageState page counters
# ---------------------------------------------------------------------------
def test_content_state_page_counters():
    state = ContentPageState(FILES, DESCRIPTIONS)
    assert state.page_number == 1
    assert state.total_pages == 3
    state.go_next()
    assert state.page_number == 2
    state.go_next()
    assert state.page_number == 3
    assert state.is_last


def test_content_state_page_counters_single_file():
    state = ContentPageState(["AGENTS.md"], {})
    assert state.page_number == 1
    assert state.total_pages == 1
    assert state.is_first
    assert state.is_last
