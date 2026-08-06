"""Entry point for the Agent Config Deployer app."""

import tkinter as tk

import customtkinter as ctk

from ui.main_window import MainWindow


def _build_app_icon() -> tk.PhotoImage:
    """Draw a simple rounded-square app icon without any image file dependency."""
    canvas = tk.Canvas(width=64, height=64, highlightthickness=0, bg="#0E1013")
    canvas.create_rectangle(4, 4, 60, 60, fill="#6366F1", outline="")
    canvas.create_text(32, 34, text="⚙", fill="#FFFFFF", font=("Segoe UI", 30))
    canvas.update_idletasks()
    return tk.PhotoImage(canvas.postscript(colormode="color"))


def main():
    # Follow the system appearance but default to dark for a polished first look.
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = MainWindow()
    try:
        app.iconphoto(True, _build_app_icon())
    except tk.TclError:
        pass  # icon is purely cosmetic — never block startup on it
    app.mainloop()


if __name__ == "__main__":
    main()
