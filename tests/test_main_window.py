"""Regression tests for ui/main_window.py.

Note: only ONE Tk root window may be created per test process — a second
`MainWindow()` after a `.destroy()` fails with a TclError in some Python
builds, so all assertions share a single window instance.
"""

import tkinter as tk

from ui.main_window import MainWindow


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
