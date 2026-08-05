"""Main application window / wizard controller."""

from pathlib import Path

import customtkinter as ctk

from core import agent_loader, git_handler
from core.conflict_resolver import detect_conflicts
from core.file_deployer import (
    DeployError,
    deploy_base_files,
    deploy_project_specific_files,
)
from ui.wizard_steps import (
    AgentStep,
    ConflictStep,
    ContentPageController,
    PromptStep,
    SourceStep,
    SummaryStep,
)

WINDOW_SIZE = "720x560"


class MainWindow(ctk.CTk):
    """Wizard controller that wires the step screens together."""

    def __init__(self):
        super().__init__()
        self.title("Agent Config Deployer")
        self.geometry(WINDOW_SIZE)

        self.agents = agent_loader.list_agents()
        # NOTE: must NOT be named `state` — that shadows Tk's `state()` method
        # and breaks CustomTkinter's internal window state handling.
        self.wizard_state: dict = {}
        self.current_step = None

        self._show_source_step()

    def _clear(self):
        if self.current_step is not None:
            self.current_step.destroy()
        self.current_step = None

    def _show_source_step(self):
        self._clear()
        self.current_step = SourceStep(self, on_next=self._on_source)
        self.current_step.pack(fill="both", expand=True)

    def _on_source(self, data: dict):
        self.wizard_state.update(data)
        self._show_agent_step()

    def _show_agent_step(self):
        self._clear()
        self.current_step = AgentStep(self, agents=self.agents, on_next=self._on_agent)
        self.current_step.pack(fill="both", expand=True)

    def _on_agent(self, data: dict):
        self.wizard_state.update(data)
        self._show_prompt_step()

    def _show_prompt_step(self):
        self._clear()
        try:
            agent = agent_loader.get_agent(self.wizard_state["agent"])
            prompt_text = agent_loader.load_prompt(agent)
        except agent_loader.AgentConfigError as exc:
            ctk.CTkLabel(self, text=f"Error: {exc}").pack(pady=20)
            ctk.CTkButton(self, text="Back", command=self._show_agent_step).pack(
                pady=10
            )
            return
        self.current_step = PromptStep(
            self, prompt_text=prompt_text, on_next=self._on_prompt
        )
        self.current_step.pack(fill="both", expand=True)

    def _on_prompt(self, data: dict):
        self.wizard_state.update(data)
        self._show_content_step()

    def _show_content_step(self):
        self._clear()
        agent = agent_loader.get_agent(self.wizard_state["agent"])
        structure = agent.get("structure", {})
        project_files = list(structure.get("project_specific_files", {}).keys())
        descriptions = structure.get("file_descriptions", {})
        self.current_step = ContentPageController(
            self,
            project_files=project_files,
            descriptions=descriptions,
            on_next=self._on_content,
            on_back=self._show_prompt_step,
        )
        self.current_step.pack(fill="both", expand=True)

    def _on_content(self, data: dict):
        self.wizard_state.update(data)
        self._show_conflict_step()

    def _show_conflict_step(self):
        self._clear()
        try:
            project_dir = self._resolve_project_dir()
            planned = self._planned_targets(project_dir)
            report = detect_conflicts(project_dir, planned)
        except (
            git_handler.GitCloneError,
            DeployError,
            agent_loader.AgentConfigError,
        ) as exc:
            ctk.CTkLabel(self, text=f"Error: {exc}").pack(pady=20)
            ctk.CTkButton(self, text="Back", command=self._show_source_step).pack(
                pady=10
            )
            return
        self.wizard_state["project_dir"] = project_dir
        self.wizard_state["report"] = report
        self.current_step = ConflictStep(self, report=report, on_next=self._on_conflict)
        self.current_step.pack(fill="both", expand=True)

    def _on_conflict(self, data: dict):
        self.wizard_state.update(data)
        self._run_deploy()

    def _run_deploy(self):
        self._clear()
        try:
            project_dir = self.wizard_state["project_dir"]
            report = self.wizard_state["report"]
            agent = agent_loader.get_agent(self.wizard_state["agent"])
            base_template_path = Path(agent.get("base_template_path", ""))

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
            ctk.CTkLabel(self, text=f"Deploy failed: {exc}").pack(pady=20)
            ctk.CTkButton(self, text="Back", command=self._show_source_step).pack(
                pady=10
            )
            return

        self.current_step = SummaryStep(
            self, written=written, skipped=skipped, on_finish=self.destroy
        )
        self.current_step.pack(fill="both", expand=True)

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
