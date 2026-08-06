"""Wizard step screens: source, agent select, content input, conflict resolution, summary.

Each step is a ``ctk.CTkFrame`` placed in the main window's content area. Steps
that want the shared footer's Back/Next buttons expose ``on_footer_back`` and
``on_footer_next`` methods plus footer metadata (labels and enable flags) so
the MainWindow footer stays in sync with the active step.
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from core.conflict_resolver import ConflictReport, record_decision
from ui import theme
from ui.components import (
    Badge,
    Card,
    EmptyState,
    FormField,
    InlineNotice,
    SegmentedChoice,
)

CONFLICT_OPTIONS = {"Overwrite": "overwrite", "Skip": "skip", "Merge": "merge"}


class SourceStep(ctk.CTkFrame):
    """Step 1: choose a local folder path and optional GitHub repo link."""

    back_enabled = False
    next_enabled = True
    footer_back_label = "Back"
    footer_next_label = "Next"

    def __init__(
        self, master, on_next, initial_folder: str = "", initial_repo: str = ""
    ):
        super().__init__(master, fg_color="transparent")
        self.on_next = on_next
        self.folder_var = tk.StringVar(value=initial_folder)
        self.repo_var = tk.StringVar(value=initial_repo)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        theme.make_heading(self, text="Project Source").grid(
            row=0, column=0, sticky="w", pady=(0, theme.S_XS)
        )
        theme.make_body(
            self,
            text="Choose where the agent configuration should be deployed.",
        ).grid(row=1, column=0, sticky="w", pady=(0, theme.S_XL))

        card = Card(self)
        card.grid(row=2, column=0, sticky="nsew")
        body = card.body()
        body.grid_columnconfigure(0, weight=1)

        # Folder path
        self.folder_field = FormField(
            body,
            label="Folder path",
            textvariable=self.folder_var,
            placeholder="C:\\path\\to\\project",
            hint="The project folder. If you provide a repo URL below, this is the parent folder the repo is cloned into.",
        )
        self.folder_field.grid(row=0, column=0, sticky="ew", pady=(0, theme.S_LG))
        self.folder_entry = self.folder_field.input_widget

        browse_row = ctk.CTkFrame(body, fg_color="transparent")
        browse_row.grid(row=1, column=0, sticky="ew", pady=(0, theme.S_XL))
        browse_row.grid_columnconfigure(0, weight=1)
        theme.make_secondary_button(
            browse_row, text="Browse…", width=110, command=self._browse_folder
        ).grid(row=0, column=1, sticky="e")

        # Repo URL
        self.repo_field = FormField(
            body,
            label="GitHub repo URL (optional)",
            textvariable=self.repo_var,
            placeholder="https://github.com/user/repo",
            hint="Leave empty to use the folder directly. Public repos only.",
        )
        self.repo_field.grid(row=2, column=0, sticky="ew")
        self.repo_entry = self.repo_field.input_widget

        self.folder_entry.bind("<Return>", lambda _e: self.on_footer_next())
        self.repo_entry.bind("<Return>", lambda _e: self.on_footer_next())

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
            self.folder_field.clear_error()

    def _validate(self) -> bool:
        folder = self.folder_var.get().strip()
        if not folder:
            self.folder_field.set_error("Please enter a folder path.")
            return False
        self.folder_field.clear_error()
        return True

    def on_footer_back(self):
        # First step — nothing to go back to (footer back is hidden).
        pass

    def on_footer_next(self):
        if not self._validate():
            return
        self.on_next(
            {
                "folder_path": self.folder_var.get().strip(),
                "repo_url": self.repo_var.get().strip(),
            }
        )


class AgentStep(ctk.CTkFrame):
    """Step 2: select a coding agent from selectable cards."""

    back_enabled = True
    next_enabled = True
    footer_back_label = "Back"
    footer_next_label = "Next"

    def __init__(self, master, agents, on_next, on_back, initial_agent: str = ""):
        super().__init__(master, fg_color="transparent")
        self.on_next = on_next
        self.on_back = on_back
        self.agents = agents
        default = agents[0]["name"] if agents else ""
        self.selected = tk.StringVar(value=initial_agent or default)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        theme.make_heading(self, text="Select Agent").grid(
            row=0, column=0, sticky="w", pady=(0, theme.S_XS)
        )
        theme.make_body(
            self,
            text="Choose which coding agent's configuration to deploy.",
        ).grid(row=1, column=0, sticky="w", pady=(0, theme.S_XL))

        if not agents:
            EmptyState(
                self,
                title="No agents found",
                description="Add an agent config JSON to the agents/ folder and restart the app.",
            ).grid(row=2, column=0, sticky="nsew")
            return

        self.list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.list_frame.grid(row=2, column=0, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)

        for agent in self.agents:
            self._build_agent_card(self.list_frame, agent)

    def _build_agent_card(self, master, agent: dict):
        name = agent.get("name", "Unknown")
        version = agent.get("version", "")
        description = agent.get("description", "")
        is_selected = self.selected.get() == name

        card = ctk.CTkFrame(
            master,
            fg_color=theme.color("surface"),
            corner_radius=theme.RADIUS_CARD,
            border_width=2 if is_selected else 1,
            border_color=(
                theme.color("accent") if is_selected else theme.color("border")
            ),
            cursor="hand2",
        )
        card.grid(
            row=len(master.winfo_children()) - 1,
            column=0,
            sticky="ew",
            pady=(0, theme.S_MD),
        )
        card.grid_columnconfigure(0, weight=1)

        radio = ctk.CTkRadioButton(
            card,
            text="",
            variable=self.selected,
            value=name,
            command=lambda: self._select(name),
            fg_color=theme.color("accent"),
            hover_color=theme.color("accent_hover"),
            border_color=theme.color("border"),
        )
        radio.grid(
            row=0, column=0, rowspan=2, padx=(theme.S_LG, theme.S_MD), pady=theme.S_LG
        )

        name_row = ctk.CTkFrame(card, fg_color="transparent")
        name_row.grid(row=0, column=1, sticky="ew", pady=(theme.S_LG, 0))
        name_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            name_row,
            text=name,
            font=theme.h3(),
            text_color=theme.color("text"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        if version:
            Badge(name_row, text=f"v{version}", kind="neutral").grid(
                row=0, column=1, sticky="e", padx=(theme.S_SM, theme.S_LG)
            )

        ctk.CTkLabel(
            card,
            text=description or "No description available.",
            font=theme.body(),
            text_color=theme.color("text_secondary"),
            anchor="w",
            justify="left",
            wraplength=640,
        ).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, theme.S_LG),
            pady=(theme.S_XS, theme.S_LG),
        )

        card.bind("<Button-1>", lambda _e: self._select(name))
        radio.bind("<Button-1>", lambda _e: self._select(name))

    def _select(self, name: str):
        self.selected.set(name)
        self._refresh_selection()

    def _refresh_selection(self):
        """Rebuild the card list so the selected card gets the accent border."""
        self.list_frame.destroy()
        self.list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.list_frame.grid(row=2, column=0, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)
        for agent in self.agents:
            self._build_agent_card(self.list_frame, agent)

    def on_footer_back(self):
        self.on_back()

    def on_footer_next(self):
        if not self.selected.get():
            return
        self.on_next({"agent": self.selected.get()})


class PromptStep(ctk.CTkFrame):
    """Step 3: show the agent's prompt.md so the user can copy it into an AI chat."""

    back_enabled = True
    next_enabled = True
    footer_back_label = "Back"
    footer_next_label = "Next"

    def __init__(self, master, prompt_text: str, on_next, on_back):
        super().__init__(master, fg_color="transparent")
        self.on_next = on_next
        self.on_back = on_back
        self.prompt_text = prompt_text

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        theme.make_heading(self, text="Generate Project-Specific Content").grid(
            row=0, column=0, sticky="w", pady=(0, theme.S_XS)
        )
        theme.make_body(
            self,
            text=(
                "Copy the prompt below, add your project details as instructed in the prompt and paste it "
                "into Claude (or your AI chat) to generate the project-specific files. Then paste the results "
                "into the next step."
            ),
        ).grid(row=1, column=0, sticky="w", pady=(0, theme.S_XL))

        card = Card(self)
        card.grid(row=2, column=0, sticky="nsew")
        body = card.body()
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(
            body,
            font=theme.mono(),
            fg_color=theme.color("bg"),
            border_width=1,
            border_color=theme.color("border"),
            corner_radius=theme.RADIUS_INPUT,
            text_color=theme.color("text"),
            wrap="word",
        )
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.insert("1.0", prompt_text)
        self.textbox.configure(state="disabled")  # read-only, but text stays selectable

        action_row = ctk.CTkFrame(body, fg_color="transparent")
        action_row.grid(row=1, column=0, sticky="ew", pady=(theme.S_LG, 0))
        action_row.grid_columnconfigure(0, weight=1)

        self.copy_btn = theme.make_secondary_button(
            action_row, text="Copy Prompt", width=120, command=self._copy_prompt
        )
        self.copy_btn.grid(row=0, column=0, sticky="w")

        self.copy_feedback = ctk.CTkLabel(
            action_row,
            text="",
            font=theme.small(),
            text_color=theme.color("success_text"),
            anchor="w",
        )
        self.copy_feedback.grid(row=0, column=1, sticky="w", padx=(theme.S_MD, 0))

    def _copy_prompt(self):
        self.clipboard_clear()
        self.clipboard_append(self.prompt_text)
        self.update()  # keep clipboard data after the app closes
        self.copy_feedback.configure(text="✓ Copied to clipboard")
        self.after(2000, lambda: self.copy_feedback.configure(text=""))

    def on_footer_back(self):
        self.on_back()

    def on_footer_next(self):
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

    @property
    def page_number(self) -> int:
        return self.index + 1

    @property
    def total_pages(self) -> int:
        return len(self.project_files)

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

    back_enabled = True
    next_enabled = True

    def __init__(
        self, master, project_files, descriptions, on_next, on_back, state=None
    ):
        super().__init__(master, fg_color="transparent")
        self.on_next = on_next
        self.on_back = on_back
        self.state = state or ContentPageState(project_files, descriptions)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        theme.make_heading(self, text="Project-Specific Content").grid(
            row=0, column=0, sticky="w", pady=(0, theme.S_XS)
        )
        theme.make_body(
            self,
            text="Paste the content generated from the prompt for each file. Content is saved automatically as you navigate.",
        ).grid(row=1, column=0, sticky="w", pady=(0, theme.S_LG))

        # Page progress strip
        self.progress_label = ctk.CTkLabel(
            self,
            text="",
            font=theme.caption(),
            text_color=theme.color("text_muted"),
            anchor="w",
        )
        self.progress_label.grid(row=2, column=0, sticky="w", pady=(0, theme.S_MD))

        card = Card(self)
        card.grid(row=3, column=0, sticky="nsew")
        body = card.body()
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(2, weight=1)

        # Filename heading + badge
        file_row = ctk.CTkFrame(body, fg_color="transparent")
        file_row.grid(row=0, column=0, sticky="ew")
        file_row.grid_columnconfigure(0, weight=1)

        self.filename_label = ctk.CTkLabel(
            file_row,
            text="",
            font=theme.h3(),
            text_color=theme.color("text"),
            anchor="w",
        )
        self.filename_label.grid(row=0, column=0, sticky="w")

        self.file_badge = Badge(file_row, text="FILE", kind="info")
        self.file_badge.grid(row=0, column=1, sticky="e")

        self.desc_label = ctk.CTkLabel(
            body,
            text="",
            font=theme.body(),
            text_color=theme.color("text_secondary"),
            anchor="w",
            justify="left",
            wraplength=720,
        )
        self.desc_label.grid(
            row=1, column=0, sticky="ew", pady=(theme.S_SM, theme.S_LG)
        )

        self.textbox = ctk.CTkTextbox(
            body,
            font=theme.mono(),
            fg_color=theme.color("bg"),
            border_width=1,
            border_color=theme.color("border"),
            corner_radius=theme.RADIUS_INPUT,
            text_color=theme.color("text"),
            wrap="word",
        )
        self.textbox.grid(row=2, column=0, sticky="nsew")

        self._show_current()

    @property
    def footer_back_label(self) -> str:
        return "Back" if not self.state.is_first else "Back to Prompt"

    @property
    def footer_next_label(self) -> str:
        return "Next" if not self.state.is_last else "Deploy"

    def _show_current(self):
        """Render the page for the current file, loading any saved content."""
        filename = self.state.current_filename
        self.filename_label.configure(text=filename)
        self.desc_label.configure(text=self.state.current_description)
        self.progress_label.configure(
            text=f"File {self.state.page_number} of {self.state.total_pages}"
        )
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", self.state.content_map.get(filename, ""))
        self.textbox.focus_set()

    def _save_current(self):
        """Persist the current textbox content before navigating away."""
        self.state.save_current(self.textbox.get("1.0", "end-1c"))

    def on_footer_back(self):
        self._save_current()
        if not self.state.go_back():
            self.on_back()
        else:
            self._show_current()

    def on_footer_next(self):
        self._save_current()
        if not self.state.go_next():
            self.on_next({"content_map": self.state.content_map})
        else:
            self._show_current()


class ConflictStep(ctk.CTkFrame):
    """Step 5: show conflicts and ask the user how to proceed for each."""

    back_enabled = True
    next_enabled = True
    footer_back_label = "Back"
    footer_next_label = "Deploy"

    def __init__(self, master, report: ConflictReport, on_next, on_back):
        super().__init__(master, fg_color="transparent")
        self.on_next = on_next
        self.on_back = on_back
        self.report = report

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        theme.make_heading(self, text="Resolve Conflicts").grid(
            row=0, column=0, sticky="w", pady=(0, theme.S_XS)
        )

        if not report.has_conflicts:
            theme.make_body(
                self,
                text="No existing files will be overwritten.",
            ).grid(row=1, column=0, sticky="w", pady=(0, theme.S_XL))
            InlineNotice(
                self,
                text="No conflicts found — all files will be written.",
                kind="success",
            ).grid(row=2, column=0, sticky="ew")
            return

        theme.make_body(
            self,
            text="The following files/folders already exist. Choose how to proceed for each:",
        ).grid(row=1, column=0, sticky="w", pady=(0, theme.S_XL))

        list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)

        for conflict in report.conflicts:
            self._build_conflict_card(list_frame, conflict)

    def _build_conflict_card(self, master, conflict):
        kind = "folder" if conflict.is_dir else "file"
        path_key = str(conflict.path)
        initial = self.report.decisions.get(path_key, "overwrite")

        card = Card(master, padding=theme.S_MD)
        card.grid(
            row=len(master.winfo_children()) - 1,
            column=0,
            sticky="ew",
            pady=(0, theme.S_MD),
        )
        body = card.body()
        body.grid_columnconfigure(0, weight=1)

        top_row = ctk.CTkFrame(body, fg_color="transparent")
        top_row.grid(row=0, column=0, sticky="ew")
        top_row.grid_columnconfigure(0, weight=1)

        Badge(
            top_row,
            text=kind.upper(),
            kind="warning" if conflict.is_dir else "info",
        ).grid(row=0, column=0, sticky="w")

        path_label = ctk.CTkLabel(
            top_row,
            text=path_key,
            font=theme.small(),
            text_color=theme.color("text"),
            anchor="w",
            justify="left",
            wraplength=520,
        )
        path_label.grid(row=1, column=0, sticky="ew", pady=(theme.S_SM, theme.S_MD))

        choice = SegmentedChoice(
            body,
            options=CONFLICT_OPTIONS,
            value=initial,
            command=lambda value, key=path_key: record_decision(
                self.report, Path(key), value
            ),
        )
        choice.grid(row=2, column=0, sticky="w")

    def on_footer_back(self):
        self.on_back()

    def on_footer_next(self):
        self.on_next({"report": self.report})


class SummaryStep(ctk.CTkFrame):
    """Step 6: show what was copied/skipped."""

    back_enabled = False
    next_enabled = True
    footer_back_label = "Back"
    footer_next_label = "Finish"

    def __init__(self, master, written: list[Path], skipped: list[Path], on_finish):
        super().__init__(master, fg_color="transparent")
        self.on_finish = on_finish

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Success header
        ctk.CTkLabel(
            self,
            text="✓",
            font=theme.font(40, weight="bold"),
            text_color=theme.color("success_text"),
        ).grid(row=0, column=0, pady=(0, theme.S_SM))

        theme.make_heading(self, text="Deployment Complete").grid(
            row=1, column=0, sticky="w", pady=(0, theme.S_XS)
        )
        theme.make_body(
            self,
            text="Your agent configuration has been deployed to the project folder.",
        ).grid(row=2, column=0, sticky="w", pady=(0, theme.S_XL))

        list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        list_frame.grid(row=3, column=0, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)

        # Written section
        written_card = Card(list_frame)
        written_card.grid(row=0, column=0, sticky="ew", pady=(0, theme.S_MD))
        written_body = written_card.body()
        written_body.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            written_body,
            text=f"Written files ({len(written)})",
            font=theme.h3(),
            text_color=theme.color("text"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, theme.S_MD))

        if written:
            for i, path in enumerate(written):
                row = ctk.CTkFrame(written_body, fg_color="transparent")
                row.grid(row=i + 1, column=0, sticky="ew", pady=(0, theme.S_XS))
                row.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(
                    row,
                    text="✓",
                    font=theme.small(),
                    text_color=theme.color("success_text"),
                ).grid(row=0, column=0, sticky="w")
                ctk.CTkLabel(
                    row,
                    text=str(path),
                    font=theme.small(),
                    text_color=theme.color("text_secondary"),
                    anchor="w",
                    justify="left",
                    wraplength=640,
                ).grid(row=0, column=1, sticky="w", padx=(theme.S_SM, 0))
        else:
            ctk.CTkLabel(
                written_body,
                text="Nothing was written.",
                font=theme.body(),
                text_color=theme.color("text_muted"),
                anchor="w",
            ).grid(row=1, column=0, sticky="w")

        # Skipped section
        skipped_card = Card(list_frame)
        skipped_card.grid(row=1, column=0, sticky="ew")
        skipped_body = skipped_card.body()
        skipped_body.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            skipped_body,
            text=f"Skipped files ({len(skipped)})",
            font=theme.h3(),
            text_color=theme.color("text"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, theme.S_MD))

        if skipped:
            for i, path in enumerate(skipped):
                row = ctk.CTkFrame(skipped_body, fg_color="transparent")
                row.grid(row=i + 1, column=0, sticky="ew", pady=(0, theme.S_XS))
                row.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(
                    row,
                    text="–",
                    font=theme.small(),
                    text_color=theme.color("text_muted"),
                ).grid(row=0, column=0, sticky="w")
                ctk.CTkLabel(
                    row,
                    text=str(path),
                    font=theme.small(),
                    text_color=theme.color("text_secondary"),
                    anchor="w",
                    justify="left",
                    wraplength=640,
                ).grid(row=0, column=1, sticky="w", padx=(theme.S_SM, 0))
        else:
            ctk.CTkLabel(
                skipped_body,
                text="Nothing was skipped.",
                font=theme.body(),
                text_color=theme.color("text_muted"),
                anchor="w",
            ).grid(row=1, column=0, sticky="w")

    def on_footer_back(self):
        # No back from summary.
        pass

    def on_footer_next(self):
        self.on_finish()
