"""Regression tests for ui/main_window.py.

Note: only ONE Tk root window may be created per test process — a second
`MainWindow()` after a `.destroy()` fails with a TclError in some Python
builds, so all assertions share a single window instance.
"""

import tkinter as tk

from ui.main_window import MainWindow
from ui.wizard_steps import ContentPageController, PromptStep


def test_main_window_does_not_shadow_tk_state_method():
    """Regression: the wizard data dict must not shadow Tk's state() method.

    Previously `self.state` (a dict) hid the inherited `state()` method, so
    CustomTkinter's internal call `self.state(...)` raised
    TypeError: 'dict' object is not callable on startup.
    """
    app = MainWindow()
    app.withdraw()  # keep the window hidden during tests
    try:
        # The inherited Tk state() method must still be callable.
        assert callable(app.state)
        result = app.state("normal")
        assert isinstance(result, str) or result is None

        # Wizard data must live under a non-colliding attribute name.
        assert isinstance(app.wizard_state, dict)

        # Steps update the wizard_state dict in place.
        app.wizard_state["folder_path"] = "C:/some/folder"
        assert app.wizard_state["folder_path"] == "C:/some/folder"

        # Regression: clicking Finish on the summary step destroys the window;
        # the footer refresh must not touch widgets that no longer exist.
        from pathlib import Path

        app._show_summary_step(written=[Path("C:/x/AGENTS.md")], skipped=[])
        app._footer_next()  # must not raise TclError
    finally:
        # The Finish action above destroys the window; only destroy if alive.
        try:
            if app.winfo_exists():
                app.destroy()
        except tk.TclError:
            pass


def test_content_persists_when_navigating_back_to_prompt():
    """Regression: content typed on the content step must survive a
    back-navigation to the prompt step and a return to the content step.

    Previously the ContentPageState was only persisted on forward navigation,
    so going back to the prompt step destroyed the controller and its saved
    content, and returning to the content step started from an empty state.
    """
    app = MainWindow()
    app.withdraw()
    try:
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
    finally:
        try:
            if app.winfo_exists():
                app.destroy()
        except tk.TclError:
            pass
