"""Wizard step screens: source, agent select, content input, conflict resolution, summary."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.conflict_resolver import ConflictReport, record_decision


class SourceStep(ctk.CTkFrame):
    """Step 1: choose a local folder path and optional GitHub repo link."""

    def __init__(self, master, on_next):
        super().__init__(master)
        self.on_next = on_next

        ctk.CTkLabel(
            self,
            text="Step 1: Project Source",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 10))

        ctk.CTkLabel(self, text="Folder path (parent folder if cloning):").pack(
            anchor="w", padx=20
        )
        self.folder_var = tk.StringVar()
        folder_row = ctk.CTkFrame(self, fg_color="transparent")
        folder_row.pack(fill="x", padx=20, pady=(4, 8))
        self.folder_entry = ctk.CTkEntry(folder_row, textvariable=self.folder_var)
        self.folder_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            folder_row, text="Browse...", width=90, command=self._browse_folder
        ).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            self,
            text="GitHub repo URL (optional — leave empty to use the folder directly):",
        ).pack(anchor="w", padx=20)
        self.repo_var = tk.StringVar()
        self.repo_entry = ctk.CTkEntry(self, textvariable=self.repo_var)
        self.repo_entry.pack(fill="x", padx=20, pady=(4, 8))

        ctk.CTkButton(self, text="Next", command=self._next).pack(pady=20)

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def _next(self):
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showerror("Missing input", "Please enter a folder path.")
            return
        self.on_next({"folder_path": folder, "repo_url": self.repo_var.get().strip()})


class AgentStep(ctk.CTkFrame):
    """Step 2: select a coding agent."""

    def __init__(self, master, agents, on_next):
        super().__init__(master)
        self.on_next = on_next
        self.agents = agents

        ctk.CTkLabel(
            self, text="Step 2: Select Agent", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10))

        self.agent_var = tk.StringVar(value=agents[0]["name"] if agents else "")
        for agent in agents:
            ctk.CTkRadioButton(
                self, text=agent["name"], variable=self.agent_var, value=agent["name"]
            ).pack(anchor="w", padx=20, pady=4)

        ctk.CTkButton(self, text="Next", command=self._next).pack(pady=20)

    def _next(self):
        if not self.agent_var.get():
            messagebox.showerror("Missing input", "Please select an agent.")
            return
        self.on_next({"agent": self.agent_var.get()})


class PromptStep(ctk.CTkFrame):
    """Step 3: show the agent's prompt.md so the user can copy it into an AI chat."""

    def __init__(self, master, prompt_text: str, on_next):
        super().__init__(master)
        self.on_next = on_next
        self.prompt_text = prompt_text

        ctk.CTkLabel(
            self,
            text="Step 3: Generate Project-Specific Content",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            self,
            text=(
                "Copy the prompt below and paste it into Claude (or your AI chat) "
                "to generate the project-specific files. Then paste the results "
                "into the next step."
            ),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 8))

        self.textbox = ctk.CTkTextbox(self, height=280)
        self.textbox.pack(fill="both", expand=True, padx=20, pady=(4, 8))
        self.textbox.insert("1.0", prompt_text)
        self.textbox.configure(state="disabled")  # read-only, but text stays selectable

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 8))
        ctk.CTkButton(btn_row, text="Copy Prompt", command=self._copy_prompt).pack(
            side="left"
        )
        ctk.CTkButton(btn_row, text="Next", command=self._next).pack(
            side="right", padx=(8, 0)
        )

    def _copy_prompt(self):
        self.clipboard_clear()
        self.clipboard_append(self.prompt_text)
        self.update()  # keep clipboard data after the app closes

    def _next(self):
        self.on_next({})


class ContentPageState:
    """Pure navigation/save logic for the per-file content pages.

    Kept separate from the widget so it can be tested without a Tk root.
    """

    def __init__(self, project_files, descriptions=None):
        self.project_files = list(project_files)
        self.descriptions = descriptions or {}
        self.content_map: dict[str, str] = {}
        self.index = 0

    @property
    def current_filename(self) -> str:
        return self.project_files[self.index]

    @property
    def current_description(self) -> str:
        return self.descriptions.get(self.current_filename, "")

    @property
    def is_first(self) -> bool:
        return self.index == 0

    @property
    def is_last(self) -> bool:
        return self.index == len(self.project_files) - 1

    def save_current(self, text: str) -> None:
        """Persist the current page's content."""
        self.content_map[self.current_filename] = text

    def go_next(self) -> bool:
        """Advance to the next page. Returns True if moved, False if already on last."""
        if self.is_last:
            return False
        self.index += 1
        return True

    def go_back(self) -> bool:
        """Go to the previous page. Returns True if moved, False if already on first."""
        if self.is_first:
            return False
        self.index -= 1
        return True


class ContentPageController(ctk.CTkFrame):
    """Step 4: one page per project-specific file, auto-saving on navigation.

    Each page shows the step heading, the filename as a second heading, and a
    one-line description. Content is saved automatically when the user moves
    between pages — there is no explicit Save button.
    """

    def __init__(self, master, project_files, descriptions, on_next, on_back):
        super().__init__(master)
        self.on_next = on_next
        self.on_back = on_back
        self.state = ContentPageState(project_files, descriptions)

        self.heading_label = ctk.CTkLabel(
            self,
            text="Step 4: Project-Specific Content",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.heading_label.pack(pady=(20, 10))

        self.filename_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=15, weight="bold")
        )
        self.filename_label.pack(anchor="w", padx=20)

        self.desc_label = ctk.CTkLabel(self, text="", wraplength=640, justify="left")
        self.desc_label.pack(anchor="w", padx=20, pady=(2, 8))

        self.textbox = ctk.CTkTextbox(self, height=220)
        self.textbox.pack(fill="both", expand=True, padx=20, pady=(4, 8))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 8))
        self.back_btn = ctk.CTkButton(btn_row, text="Back", command=self._go_back)
        self.back_btn.pack(side="left")
        self.next_btn = ctk.CTkButton(btn_row, text="Next", command=self._go_next)
        self.next_btn.pack(side="right", padx=(8, 0))

        self._show_current()

    def _show_current(self):
        """Render the page for the current file, loading any saved content."""
        filename = self.state.current_filename
        self.filename_label.configure(text=filename)
        self.desc_label.configure(text=self.state.current_description)
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", self.state.content_map.get(filename, ""))
        self.back_btn.configure(
            text="Back" if not self.state.is_first else "Back to Prompt"
        )
        self.next_btn.configure(text="Next" if not self.state.is_last else "Finish")

    def _save_current(self):
        """Persist the current textbox content before navigating away."""
        self.state.save_current(self.textbox.get("1.0", "end-1c"))

    def _go_back(self):
        self._save_current()
        if not self.state.go_back():
            self.on_back()
        else:
            self._show_current()

    def _go_next(self):
        self._save_current()
        if not self.state.go_next():
            self.on_next({"content_map": self.state.content_map})
        else:
            self._show_current()


class ConflictStep(ctk.CTkFrame):
    """Step 5: show conflicts and ask the user how to proceed for each."""

    def __init__(self, master, report: ConflictReport, on_next):
        super().__init__(master)
        self.on_next = on_next
        self.report = report
        self.choice_vars: dict[str, tk.StringVar] = {}

        ctk.CTkLabel(
            self,
            text="Step 5: Resolve Conflicts",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 10))

        if not report.has_conflicts:
            ctk.CTkLabel(
                self, text="No conflicts found — all files will be written."
            ).pack(pady=20)
        else:
            ctk.CTkLabel(
                self,
                text="The following files/folders already exist. Choose how to proceed for each:",
            ).pack(anchor="w", padx=20)
            for conflict in report.conflicts:
                kind = "folder" if conflict.is_dir else "file"
                row = ctk.CTkFrame(self, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=4)
                ctk.CTkLabel(row, text=f"{conflict.path} ({kind})", anchor="w").pack(
                    side="left", fill="x", expand=True
                )
                var = tk.StringVar(value="overwrite")
                self.choice_vars[str(conflict.path)] = var
                ctk.CTkOptionMenu(
                    row, values=["overwrite", "skip", "merge"], variable=var, width=110
                ).pack(side="right")

        ctk.CTkButton(self, text="Next", command=self._next).pack(pady=20)

    def _next(self):
        for path, var in self.choice_vars.items():
            record_decision(self.report, Path(path), var.get())
        self.on_next({"report": self.report})


class SummaryStep(ctk.CTkFrame):
    """Step 6: show what was copied/skipped."""

    def __init__(self, master, written: list[Path], skipped: list[Path], on_finish):
        super().__init__(master)
        self.on_finish = on_finish

        ctk.CTkLabel(
            self, text="Step 6: Summary", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10))

        ctk.CTkLabel(self, text="Written files:", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=20
        )
        for path in written:
            ctk.CTkLabel(self, text=f"  {path}", anchor="w").pack(anchor="w", padx=20)

        ctk.CTkLabel(self, text="Skipped files:", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=20, pady=(10, 0)
        )
        if skipped:
            for path in skipped:
                ctk.CTkLabel(self, text=f"  {path}", anchor="w").pack(
                    anchor="w", padx=20
                )
        else:
            ctk.CTkLabel(self, text="  (none)", anchor="w").pack(anchor="w", padx=20)

        ctk.CTkButton(self, text="Finish", command=self.on_finish).pack(pady=20)
