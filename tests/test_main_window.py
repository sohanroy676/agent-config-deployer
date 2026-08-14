"""Regression tests for ui/main_window.py.

IMPORTANT: only ONE Tk root window may be created per test process on this
machine (Python 3.14 has a flaky Tk install — a second `MainWindow()` after a
`.destroy()` intermittently raises `_tkinter.TclError`). All assertions
therefore share a single window instance inside one test function.
"""

import tkinter as tk
from pathlib import Path

from config import settings
from ui.main_window import MainWindow
from ui.wizard_steps import ContentPageController, PromptStep


def test_main_window_wizard_behaviors(monkeypatch, tmp_path):
    """All MainWindow behaviors using a single window instance:

    - The wizard data dict must not shadow Tk's state() method.
    - The Source/Agent steps pre-fill from the last-used settings.
    - Advancing from Source/Agent persists last-used values and the per-agent
      base template path.
    - A configured base template path overrides the agent config default, and
      an empty value clears it (falling back to the default).
    - Content typed on the content step survives back-navigation to the prompt
      step and a return to the content step.
    - Clicking Finish on the summary step destroys the window without the
      footer refresh raising a TclError.
    """
    path = tmp_path / "settings.json"
    monkeypatch.setattr(settings, "SETTINGS_PATH", path)
    settings.update_last_used(
        folder_path="C:/saved/folder",
        repo_url="https://github.com/x/y",
        agent="Cline",
    )
    settings.set_base_template_path("Cline", "C:/custom/templates")

    app = MainWindow()
    app.withdraw()  # keep the window hidden during tests
    try:
        # --- Settings wiring: prefill + persist ---------------------------
        # Source step pre-fills from last-used folder/repo.
        assert app.current_step.folder_var.get() == "C:/saved/folder"
        assert app.current_step.repo_var.get() == "https://github.com/x/y"

        # Agent step pre-selects the last-used agent.
        app._show_agent_step()
        assert app.current_step.selected.get() == "Cline"

        # Advancing from Source persists the folder/repo as last-used.
        app._on_source({"folder_path": "D:/new", "repo_url": "https://github.com/a/b"})
        loaded = settings.get_last_used()
        assert loaded["folder_path"] == "D:/new"
        assert loaded["repo_url"] == "https://github.com/a/b"

        # Advancing from Agent persists the agent and its template path.
        app._on_agent({"agent": "Cline", "template_path": "C:/custom/templates"})
        assert settings.get_last_used()["agent"] == "Cline"
        assert settings.get_base_template_path("Cline") == "C:/custom/templates"

        # A configured base template path overrides the agent config default.
        agent = {"name": "Cline", "base_template_path": "templates/cline"}
        assert app._effective_base_template_path(agent) == Path("C:/custom/templates")

        # An empty template path clears the saved override, falling back to
        # the agent config default.
        app._on_agent({"agent": "Cline", "template_path": ""})
        assert settings.get_base_template_path("Cline") == ""
        assert app._effective_base_template_path(agent) == Path("templates/cline")

        # --- Content persists across back-navigation ----------------------
        app.wizard_state["agent"] = "Cline"
        app._show_content_step()
        controller = app.current_step
        assert isinstance(controller, ContentPageController)
        controller.textbox.insert("1.0", "my project content")

        # Go back to the prompt step (first content page -> back exits).
        app._footer_back()
        assert isinstance(app.current_step, PromptStep)

        # Return to the content step — content must still be there.
        app._show_content_step()
        controller = app.current_step
        assert isinstance(controller, ContentPageController)
        assert controller.state.content_map.get("AGENTS.md") == "my project content"

        # --- Wizard data must not shadow Tk's state() method --------------
        assert callable(app.state)
        result = app.state("normal")
        assert isinstance(result, str) or result is None
        assert isinstance(app.wizard_state, dict)

        # --- Summary Finish destroys the window without a TclError --------
        app._show_summary_step(written=[Path("C:/x/AGENTS.md")], skipped=[])
        app._footer_next()  # must not raise TclError
    finally:
        # The Finish action above destroys the window; only destroy if alive.
        try:
            if app.winfo_exists():
                app.destroy()
        except tk.TclError:
            pass
