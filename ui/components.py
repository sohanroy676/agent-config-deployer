"""Reusable UI components built on the design system in ui/theme.py.

These composite widgets are shared across all wizard steps so the app has a
single, consistent component vocabulary: cards, badges, notices, form fields,
the step indicator, loading/error/empty states, and the segmented choice
control used for conflict resolution.
"""

from __future__ import annotations

import customtkinter as ctk

from ui import theme


# ---------------------------------------------------------------------------
# Pure state logic (testable without a Tk root)
# ---------------------------------------------------------------------------
class StepIndicatorState:
    """Pure state for the wizard step rail.

    Given the total number of steps and the current index, computes which
    steps are completed, active, or upcoming.
    """

    def __init__(self, step_names: list[str], current_index: int = 0):
        self.step_names = list(step_names)
        self.current_index = current_index

    @property
    def total(self) -> int:
        return len(self.step_names)

    def is_completed(self, index: int) -> bool:
        return index < self.current_index

    def is_current(self, index: int) -> bool:
        return index == self.current_index

    def is_upcoming(self, index: int) -> bool:
        return index > self.current_index


# ---------------------------------------------------------------------------
# Badge
# ---------------------------------------------------------------------------
class Badge(ctk.CTkLabel):
    """Small pill label used for file/folder type tags."""

    def __init__(self, master, text: str, kind: str = "neutral", **kwargs):
        soft = {
            "neutral": theme.color("surface_hover"),
            "success": theme.color("success_soft"),
            "warning": theme.color("warning_soft"),
            "danger": theme.color("danger_soft"),
            "info": theme.color("info_soft"),
            "accent": theme.color("accent"),
        }
        text_color = {
            "neutral": theme.color("text_secondary"),
            "success": theme.color("success_text"),
            "warning": theme.color("warning_text"),
            "danger": theme.color("danger_text"),
            "info": theme.color("info_text"),
            "accent": theme.color("accent_text"),
        }
        kwargs.setdefault("fg_color", soft.get(kind, soft["neutral"]))
        kwargs.setdefault("text_color", text_color.get(kind, text_color["neutral"]))
        kwargs.setdefault("font", theme.font(theme.SIZE_BADGE, weight="bold"))
        kwargs.setdefault("corner_radius", theme.RADIUS_BADGE)
        kwargs.setdefault("height", 20)
        kwargs.setdefault("padx", 8)
        super().__init__(master, text=text, **kwargs)


# ---------------------------------------------------------------------------
# Card
# ---------------------------------------------------------------------------
class Card(ctk.CTkFrame):
    """Elevated surface container with consistent padding."""

    def __init__(self, master, padding: int = theme.S_LG, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color=theme.color("surface"),
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.color("border"),
        )
        self.padding = padding
        self._body = ctk.CTkFrame(self, fg_color="transparent")
        self._body.pack(fill="both", expand=True, padx=padding, pady=padding)

    def body(self) -> ctk.CTkFrame:
        """Return the padded inner container for content."""
        return self._body


# ---------------------------------------------------------------------------
# InlineNotice
# ---------------------------------------------------------------------------
class InlineNotice(ctk.CTkFrame):
    """Color-coded info/success/warning/danger banner."""

    def __init__(self, master, text: str, kind: str = "info", **kwargs):
        soft = {
            "info": theme.color("info_soft"),
            "success": theme.color("success_soft"),
            "warning": theme.color("warning_soft"),
            "danger": theme.color("danger_soft"),
        }
        text_color = {
            "info": theme.color("info_text"),
            "success": theme.color("success_text"),
            "warning": theme.color("warning_text"),
            "danger": theme.color("danger_text"),
        }
        super().__init__(
            master,
            fg_color=soft.get(kind, soft["info"]),
            corner_radius=theme.RADIUS_CARD,
            **kwargs,
        )
        self.label = ctk.CTkLabel(
            self,
            text=text,
            font=theme.small(),
            text_color=text_color.get(kind, text_color["info"]),
            justify="left",
            anchor="w",
            wraplength=680,
        )
        self.label.pack(fill="x", padx=theme.S_LG, pady=theme.S_MD)


# ---------------------------------------------------------------------------
# FormField
# ---------------------------------------------------------------------------
class FormField(ctk.CTkFrame):
    """Label + input + hint + inline error message.

    The component owns its input: pass ``placeholder`` / ``textvariable`` and
    it creates the entry itself, so the entry's parent is this frame.

    Call ``set_error`` to show an error state (red border + message) or
    ``clear_error`` to reset it.
    """

    def __init__(
        self,
        master,
        label: str,
        placeholder: str | None = None,
        textvariable=None,
        hint: str | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text=label,
            font=theme.small(),
            text_color=theme.color("text"),
            anchor="w",
        )
        self.label.pack(fill="x", pady=(0, theme.S_XS))

        self.input_widget = theme.make_entry(
            self, textvariable=textvariable, placeholder=placeholder
        )
        self.input_widget.pack(fill="x")

        self.hint_label = ctk.CTkLabel(
            self,
            text=hint or "",
            font=theme.caption(),
            text_color=theme.color("text_muted"),
            anchor="w",
            justify="left",
            wraplength=680,
        )
        self.hint_label.pack(fill="x", pady=(theme.S_XS, 0))

        self.error_label = ctk.CTkLabel(
            self,
            text="",
            font=theme.caption(),
            text_color=theme.color("danger_text"),
            anchor="w",
            justify="left",
            wraplength=680,
        )
        self.error_label.pack(fill="x", pady=(theme.S_XS, 0))

    def set_error(self, message: str) -> None:
        """Show an inline error and mark the input as invalid."""
        self.error_label.configure(text=message)
        self.input_widget.configure(border_color=theme.color("danger"))

    def clear_error(self) -> None:
        """Hide the inline error and restore the normal border."""
        self.error_label.configure(text="")
        self.input_widget.configure(border_color=theme.color("border"))


# ---------------------------------------------------------------------------
# StepIndicator
# ---------------------------------------------------------------------------
class StepIndicator(ctk.CTkFrame):
    """Horizontal wizard progress rail.

    Completed steps show a checkmark, the current step is highlighted with the
    accent color, and upcoming steps are muted.
    """

    def __init__(self, master, step_names: list[str], current_index: int = 0, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.state = StepIndicatorState(step_names, current_index)
        self._dots: list[ctk.CTkFrame] = []
        self._labels: list[ctk.CTkLabel] = []
        self._build()

    def _build(self) -> None:
        for i, name in enumerate(self.state.step_names):
            if i > 0:
                connector = ctk.CTkFrame(
                    self,
                    width=28,
                    height=2,
                    fg_color=(
                        theme.color("accent")
                        if self.state.is_completed(i)
                        else theme.color("border")
                    ),
                )
                connector.pack(side="left", padx=(theme.S_XS, theme.S_XS), pady=(0, 18))

            dot = ctk.CTkFrame(
                self,
                width=26,
                height=26,
                corner_radius=13,
                fg_color=(
                    theme.color("accent")
                    if self.state.is_current(i)
                    else (
                        theme.color("success")
                        if self.state.is_completed(i)
                        else theme.color("surface_hover")
                    )
                ),
                border_width=1,
                border_color=(
                    theme.color("accent")
                    if self.state.is_current(i)
                    else theme.color("border")
                ),
            )
            dot.pack(side="left")
            dot.pack_propagate(False)

            dot_text = "✓" if self.state.is_completed(i) else str(i + 1)
            dot_label = ctk.CTkLabel(
                dot,
                text=dot_text,
                font=theme.font(theme.SIZE_SMALL, weight="bold"),
                text_color=(
                    theme.color("accent_text")
                    if self.state.is_current(i) or self.state.is_completed(i)
                    else theme.color("text_muted")
                ),
            )
            dot_label.place(relx=0.5, rely=0.5, anchor="center")

            name_label = ctk.CTkLabel(
                self,
                text=name,
                font=theme.caption(),
                text_color=(
                    theme.color("text")
                    if self.state.is_current(i)
                    else theme.color("text_muted")
                ),
            )
            name_label.pack(side="left", padx=(theme.S_XS, 0), pady=(0, 18))

            self._dots.append(dot)
            self._labels.append(name_label)


# ---------------------------------------------------------------------------
# SegmentedChoice
# ---------------------------------------------------------------------------
class SegmentedChoice(ctk.CTkFrame):
    """Pill-style segmented control mapping display labels to values.

    Used for conflict resolution (Overwrite / Skip / Merge).
    """

    def __init__(
        self,
        master,
        options: dict[str, str],
        value: str | None = None,
        command=None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.options = options  # display label -> stored value
        self._command = command
        self._var = ctk.StringVar(value=self._label_for(value) if value else "")

        self.segment = ctk.CTkSegmentedButton(
            self,
            values=list(options.keys()),
            variable=self._var,
            command=self._on_change,
            font=theme.small(),
            fg_color=theme.color("surface_hover"),
            selected_color=theme.color("accent"),
            selected_hover_color=theme.color("accent_hover"),
            unselected_color=theme.color("surface_hover"),
            unselected_hover_color=theme.color("surface"),
            text_color=theme.color("text_secondary"),
            text_color_disabled=theme.color("text_muted"),
            height=30,
            corner_radius=theme.RADIUS_BUTTON,
        )
        self.segment.pack()

    def _label_for(self, value: str | None) -> str | None:
        if value is None:
            return None
        for label, stored in self.options.items():
            if stored == value:
                return label
        return None

    def _on_change(self, _label: str) -> None:
        if self._command is not None:
            self._command(self.get())

    def get(self) -> str:
        """Return the stored value for the currently selected label."""
        label = self._var.get()
        return self.options.get(label, "")

    def set(self, value: str) -> None:
        """Select the option whose stored value matches ``value``."""
        label = self._label_for(value)
        if label:
            self._var.set(label)


# ---------------------------------------------------------------------------
# LoadingView
# ---------------------------------------------------------------------------
class LoadingView(ctk.CTkFrame):
    """Full-area loading state with an indeterminate progress bar."""

    def __init__(self, master, message: str = "Working…", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.grid(row=0, column=0)

        self.status_label = ctk.CTkLabel(
            inner,
            text=message,
            font=theme.body(),
            text_color=theme.color("text_secondary"),
        )
        self.status_label.pack(pady=(0, theme.S_LG))

        self.progress = ctk.CTkProgressBar(
            inner,
            width=280,
            height=6,
            corner_radius=3,
            fg_color=theme.color("surface_hover"),
            progress_color=theme.color("accent"),
            mode="indeterminate",
        )
        self.progress.pack()
        self.progress.start()

    def set_message(self, message: str) -> None:
        self.status_label.configure(text=message)

    def stop(self) -> None:
        self.progress.stop()


# ---------------------------------------------------------------------------
# ErrorView
# ---------------------------------------------------------------------------
class ErrorView(ctk.CTkFrame):
    """Full-area error state with a title, message, and a back action."""

    def __init__(self, master, title: str, message: str, on_back, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.grid(row=0, column=0)

        icon = ctk.CTkLabel(
            inner,
            text="⚠",
            font=theme.font(40),
            text_color=theme.color("danger_text"),
        )
        icon.pack(pady=(0, theme.S_MD))

        ctk.CTkLabel(
            inner,
            text=title,
            font=theme.h2(),
            text_color=theme.color("text"),
        ).pack(pady=(0, theme.S_SM))

        ctk.CTkLabel(
            inner,
            text=message,
            font=theme.body(),
            text_color=theme.color("text_secondary"),
            wraplength=520,
            justify="center",
        ).pack(pady=(0, theme.S_XL))

        theme.make_secondary_button(inner, text="Back", command=on_back).pack()


# ---------------------------------------------------------------------------
# EmptyState
# ---------------------------------------------------------------------------
class EmptyState(ctk.CTkFrame):
    """Full-area empty state with an icon, title, and description."""

    def __init__(self, master, title: str, description: str, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.grid(row=0, column=0)

        ctk.CTkLabel(
            inner,
            text="📄",
            font=theme.font(40),
            text_color=theme.color("text_muted"),
        ).pack(pady=(0, theme.S_MD))

        ctk.CTkLabel(
            inner,
            text=title,
            font=theme.h3(),
            text_color=theme.color("text"),
        ).pack(pady=(0, theme.S_SM))

        ctk.CTkLabel(
            inner,
            text=description,
            font=theme.body(),
            text_color=theme.color("text_secondary"),
            wraplength=520,
            justify="center",
        ).pack()
