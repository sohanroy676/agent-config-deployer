"""Main application window / wizard controller."""

import tkinter as tk
from pathlib import Path

import customtkinter as ctk

from config import settings
from core import agent_loader, git_handler
from core.conflict_resolver import detect_conflicts
from core.file_deployer import (
    DeployError,
    deploy_base_files,
    deploy_project_specific_files,
)
from ui import theme
from ui.components import ErrorView, LoadingView, StepIndicator
from ui.wizard_steps import (
    AgentStep,
    ConflictStep,
    ContentPageController,
    PromptStep,
    SourceStep,
    SummaryStep,
)

WINDOW_SIZE = "980x680"
WINDOW_MIN_SIZE = (820, 600)

STEP_NAMES = ["Source", "Agent", "Prompt", "Content", "Conflicts", "Deploy"]


class MainWindow(ctk.CTk):
    """Wizard controller that wires the step screens together."""

    def __init__(self):
        super().__init__()
        self.title("Agent Config Deployer")
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN_SIZE)

        self.agents = agent_loader.list_agents()
        # NOTE: must NOT be named `state` — that shadows Tk's `state()` method
        # and breaks CustomTkinter's internal window state handling.
        self.wizard_state: dict = {}
        self.current_step = None
        self._step_index = 0
        self._last_used = settings.get_last_used()

        self._build_shell()
        self._show_source_step()

    # ------------------------------------------------------------------
    # Shell layout
    # ------------------------------------------------------------------
    def _build_shell(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_footer()

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(
            row=1, column=0, sticky="nsew", padx=theme.S_2XL, pady=(0, theme.S_LG)
        )
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _build_header(self):
        self._header = ctk.CTkFrame(self, fg_color="transparent")
        header = self._header
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=theme.S_2XL,
            pady=(theme.S_LG, theme.S_MD),
        )
        header.grid_columnconfigure(0, weight=1)

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew")
        title_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_row,
            text="Agent Config Deployer",
            font=theme.h2(),
            text_color=theme.color("text"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.theme_toggle = ctk.CTkButton(
            title_row,
            text="🌙 Dark" if theme.is_dark() else "☀️ Light",
            width=96,
            height=30,
            font=theme.small(),
            fg_color=theme.color("surface"),
            hover_color=theme.color("surface_hover"),
            text_color=theme.color("text_secondary"),
            border_width=1,
            border_color=theme.color("border"),
            corner_radius=theme.RADIUS_BUTTON,
            command=self._toggle_theme,
        )
        self.theme_toggle.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            header,
            text="Deploy coding-agent configuration templates into any project.",
            font=theme.body(),
            text_color=theme.color("text_muted"),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.step_indicator = StepIndicator(header, STEP_NAMES, current_index=0)
        self.step_indicator.grid(row=2, column=0, sticky="w", pady=(theme.S_LG, 0))

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(
            row=2, column=0, sticky="ew", padx=theme.S_2XL, pady=(0, theme.S_LG)
        )
        footer.grid_columnconfigure(0, weight=1)

        self.footer_back = theme.make_secondary_button(
            footer, text="Back", command=self._footer_back
        )
        self.footer_back.grid(row=0, column=0, sticky="w")

        self.footer_next = theme.make_primary_button(
            footer, text="Next", command=self._footer_next
        )
        self.footer_next.grid(row=0, column=1, sticky="e")

    # ------------------------------------------------------------------
    # Theme switching
    # ------------------------------------------------------------------
    def _toggle_theme(self):
        new_mode = "Light" if theme.is_dark() else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.theme_toggle.configure(text="🌙 Dark" if theme.is_dark() else "☀️ Light")
        # Rebuild the current step so all widgets pick up the new palette.
        self._rebuild_current_step()

    def _rebuild_current_step(self):
        """Re-render the current wizard step after a theme change."""
        if self.current_step is None:
            return
        step = self.current_step
        # _clear() persists any in-progress content before destroying the step.
        self._clear()
        if isinstance(step, SourceStep):
            self._show_source_step()
        elif isinstance(step, AgentStep):
            self._show_agent_step()
        elif isinstance(step, PromptStep):
            self._show_prompt_step()
        elif isinstance(step, ContentPageController):
            self._show_content_step()
        elif isinstance(step, ConflictStep):
            self._show_conflict_step()
        elif isinstance(step, SummaryStep):
            self._show_summary_step()

    # ------------------------------------------------------------------
    # Footer actions
    # ------------------------------------------------------------------
    def _footer_back(self):
        if self.current_step is not None and hasattr(
            self.current_step, "on_footer_back"
        ):
            self.current_step.on_footer_back()
            # The step may have changed its footer labels (e.g. content pages),
            # but it may also have finished the wizard and destroyed the window.
            if self._window_alive():
                self._update_footer(self.current_step)

    def _footer_next(self):
        if self.current_step is not None and hasattr(
            self.current_step, "on_footer_next"
        ):
            self.current_step.on_footer_next()
            # The step may have changed its footer labels (e.g. content pages),
            # but it may also have finished the wizard and destroyed the window.
            if self._window_alive():
                self._update_footer(self.current_step)

    def _window_alive(self) -> bool:
        """True if the Tk window still exists (not destroyed by a step callback)."""
        try:
            return bool(self.winfo_exists())
        except tk.TclError:
            return False

    # ------------------------------------------------------------------
    # Step navigation
    # ------------------------------------------------------------------
    def _clear(self):
        if self.current_step is not None:
            # Persist any in-progress content before the step is destroyed so
            # back/forward navigation and theme rebuilds never lose it.
            if isinstance(self.current_step, ContentPageController):
                self.current_step._save_current()
                self.wizard_state["_content_state"] = self.current_step.state
            self.current_step.destroy()
        self.current_step = None

    def _set_step(self, step, index: int):
        self._clear()
        self._step_index = index
        self.step_indicator.destroy()
        self.step_indicator = StepIndicator(
            self._header, STEP_NAMES, current_index=index
        )
        self.step_indicator.grid(row=2, column=0, sticky="w", pady=(theme.S_LG, 0))
        self.current_step = step
        step.grid(row=0, column=0, sticky="nsew")
        self._update_footer(step)

    def _update_footer(self, step):
        """Configure footer buttons based on the step's capabilities."""
        has_back = hasattr(step, "on_footer_back")
        has_next = hasattr(step, "on_footer_next")

        if has_back:
            back_enabled = getattr(step, "back_enabled", True)
            self.footer_back.configure(
                text=getattr(step, "footer_back_label", "Back"),
                state="normal" if back_enabled else "disabled",
            )
            self.footer_back.grid()
        else:
            self.footer_back.grid_remove()

        if has_next:
            next_enabled = getattr(step, "next_enabled", True)
            self.footer_next.configure(
                text=getattr(step, "footer_next_label", "Next"),
                state="normal" if next_enabled else "disabled",
            )
            self.footer_next.grid()
        else:
            self.footer_next.grid_remove()

    # ------------------------------------------------------------------
    # Step 1: Source
    # ------------------------------------------------------------------
    def _show_source_step(self):
        step = SourceStep(
            self.content,
            on_next=self._on_source,
            initial_folder=self.wizard_state.get(
                "folder_path", self._last_used.get("folder_path", "")
            ),
            initial_repo=self.wizard_state.get(
                "repo_url", self._last_used.get("repo_url", "")
            ),
        )
        self._set_step(step, 0)

    def _on_source(self, data: dict):
        self.wizard_state.update(data)
        settings.update_last_used(
            folder_path=data.get("folder_path", ""),
            repo_url=data.get("repo_url", ""),
        )
        self._show_agent_step()

    # ------------------------------------------------------------------
    # Step 2: Agent
    # ------------------------------------------------------------------
    def _show_agent_step(self):
        step = AgentStep(
            self.content,
            agents=self.agents,
            on_next=self._on_agent,
            on_back=self._show_source_step,
            initial_agent=self.wizard_state.get(
                "agent", self._last_used.get("agent", "")
            ),
            template_paths=settings.load_settings().get("base_template_paths", {}),
        )
        self._set_step(step, 1)

    def _on_agent(self, data: dict):
        self.wizard_state.update(data)
        agent_name = data.get("agent", "")
        settings.update_last_used(agent=agent_name)
        template_path = data.get("template_path", "").strip()
        if template_path:
            settings.set_base_template_path(agent_name, template_path)
        else:
            settings.clear_base_template_path(agent_name)
        self._show_prompt_step()

    # ------------------------------------------------------------------
    # Step 3: Prompt
    # ------------------------------------------------------------------
    def _show_prompt_step(self):
        try:
            agent = agent_loader.get_agent(self.wizard_state["agent"])
            prompt_text = agent_loader.load_prompt(
                agent, base_template_path=self._effective_base_template_path(agent)
            )
        except agent_loader.AgentConfigError as exc:
            self._show_error("Prompt unavailable", str(exc), back=self._show_agent_step)
            return
        step = PromptStep(
            self.content,
            prompt_text=prompt_text,
            on_next=self._on_prompt,
            on_back=self._show_agent_step,
        )
        self._set_step(step, 2)

    def _on_prompt(self, data: dict):
        self.wizard_state.update(data)
        self._show_content_step()

    # ------------------------------------------------------------------
    # Step 4: Content
    # ------------------------------------------------------------------
    def _show_content_step(self):
        agent = agent_loader.get_agent(self.wizard_state["agent"])
        structure = agent.get("structure", {})
        project_files = list(structure.get("project_specific_files", {}).keys())
        descriptions = structure.get("file_descriptions", {})
        step = ContentPageController(
            self.content,
            project_files=project_files,
            descriptions=descriptions,
            on_next=self._on_content,
            on_back=self._show_prompt_step,
            state=self.wizard_state.get("_content_state"),
        )
        self._set_step(step, 3)

    def _on_content(self, data: dict):
        self.wizard_state.update(data)
        self._show_conflict_step()

    # ------------------------------------------------------------------
    # Step 5: Conflicts
    # ------------------------------------------------------------------
    def _show_conflict_step(self):
        self._show_loading("Checking for existing files…")
        try:
            project_dir = self._resolve_project_dir()
            planned = self._planned_targets(project_dir)
            report = detect_conflicts(project_dir, planned)
        except (
            git_handler.GitCloneError,
            DeployError,
            agent_loader.AgentConfigError,
        ) as exc:
            self._show_error(
                "Could not check for conflicts", str(exc), back=self._show_source_step
            )
            return
        self.wizard_state["project_dir"] = project_dir
        self.wizard_state["report"] = report
        step = ConflictStep(
            self.content,
            report=report,
            on_next=self._on_conflict,
            on_back=self._show_content_step,
        )
        self._set_step(step, 4)

    def _on_conflict(self, data: dict):
        self.wizard_state.update(data)
        self._run_deploy()

    # ------------------------------------------------------------------
    # Step 6: Deploy / Summary
    # ------------------------------------------------------------------
    def _run_deploy(self):
        self._show_loading("Deploying files…")
        try:
            project_dir = self.wizard_state["project_dir"]
            report = self.wizard_state["report"]
            agent = agent_loader.get_agent(self.wizard_state["agent"])
            base_template_path = self._effective_base_template_path(agent)

            written = deploy_base_files(agent, base_template_path, project_dir, report)
            written += deploy_project_specific_files(
                agent, project_dir, self.wizard_state.get("content_map", {}), report
            )
            skipped = [
                c.path
                for c in report.conflicts
                if report.decisions.get(str(c.path)) == "skip"
            ]
        except (DeployError, agent_loader.AgentConfigError) as exc:
            self._show_error("Deploy failed", str(exc), back=self._show_source_step)
            return

        self._show_summary_step(written, skipped)

    def _show_summary_step(self, written=None, skipped=None):
        if written is None:
            written = self.wizard_state.get("written", [])
        if skipped is None:
            skipped = self.wizard_state.get("skipped", [])
        step = SummaryStep(
            self.content, written=written, skipped=skipped, on_finish=self.destroy
        )
        self.wizard_state["written"] = written
        self.wizard_state["skipped"] = skipped
        self._set_step(step, 5)

    # ------------------------------------------------------------------
    # Shared states
    # ------------------------------------------------------------------
    def _show_loading(self, message: str):
        self._clear()
        self.current_step = LoadingView(self.content, message=message)
        self.current_step.grid(row=0, column=0, sticky="nsew")
        self._update_footer(self.current_step)
        self.update_idletasks()
        self.update()

    def _show_error(self, title: str, message: str, back):
        self._clear()
        self.current_step = ErrorView(
            self.content, title=title, message=message, on_back=back
        )
        self.current_step.grid(row=0, column=0, sticky="nsew")
        self._update_footer(self.current_step)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _effective_base_template_path(self, agent: dict) -> Path:
        """Return the user-configured base template path for an agent if set,
        otherwise the agent config's default."""
        configured = settings.get_base_template_path(agent.get("name", ""))
        return Path(configured or agent.get("base_template_path", ""))

    def _resolve_project_dir(self) -> Path:
        """Clone the repo if a URL is given, else use the folder path directly."""
        folder = Path(self.wizard_state["folder_path"])
        repo_url = self.wizard_state.get("repo_url", "")
        if repo_url:
            return git_handler.clone_repo(repo_url, folder)
        return folder

    def _planned_targets(self, project_dir: Path) -> list[Path]:
        """Compute all absolute target paths the deployer would write."""
        agent = agent_loader.get_agent(self.wizard_state["agent"])
        structure = agent.get("structure", {})
        targets = []
        for dst_rel in structure.get("base_files", {}).values():
            targets.append(project_dir / dst_rel)
        for dst_rel in structure.get("project_specific_files", {}).values():
            targets.append(project_dir / dst_rel)
        return targets
