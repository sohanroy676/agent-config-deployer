"""Design system for the Agent Config Deployer.

All colors/typography/radii live here so every screen draws from the same
design language. Colors are resolved from the current CustomTkinter
appearance mode at call time, so widgets created after a theme switch pick
up the right palette automatically.

The appearance mode can be toggled at runtime; MainWindow rebuilds the
current wizard step so all widgets refresh with the new palette.
"""

from __future__ import annotations

import customtkinter as ctk

# ---------------------------------------------------------------------------
# Spacing scale (px)
# ---------------------------------------------------------------------------
S_XS = 4
S_SM = 8
S_MD = 12
S_LG = 16
S_XL = 24
S_2XL = 32

# ---------------------------------------------------------------------------
# Corner radii
# ---------------------------------------------------------------------------
RADIUS_INPUT = 10
RADIUS_BUTTON = 10
RADIUS_CARD = 14
RADIUS_BADGE = 999  # pill

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"

SIZE_H1 = 22
SIZE_H2 = 18
SIZE_H3 = 15
SIZE_BODY = 13
SIZE_SMALL = 12
SIZE_CAPTION = 11
SIZE_BADGE = 11

# ---------------------------------------------------------------------------
# Palettes
# ---------------------------------------------------------------------------
_DARK = {
    "bg": "#0E1013",
    "surface": "#191C22",
    "surface_hover": "#22262E",
    "border": "#2C313B",
    "text": "#EAECEF",
    "text_secondary": "#A7AEB9",
    "text_muted": "#737B87",
    "accent": "#6366F1",
    "accent_hover": "#7B7FF3",
    "accent_text": "#FFFFFF",
    "success": "#2FB36A",
    "success_hover": "#38C977",
    "success_soft": "#122A1D",
    "success_text": "#5BD58F",
    "warning": "#EFAE2E",
    "warning_soft": "#2B2113",
    "warning_text": "#F4C069",
    "danger": "#EF5A5A",
    "danger_hover": "#FF6B6B",
    "danger_soft": "#32191C",
    "danger_text": "#FF9494",
    "info": "#5B8DEF",
    "info_soft": "#15273F",
    "info_text": "#8FB8F5",
}

_LIGHT = {
    "bg": "#F3F4F6",
    "surface": "#FFFFFF",
    "surface_hover": "#ECEEF1",
    "border": "#D9DDE3",
    "text": "#1B1E24",
    "text_secondary": "#535C68",
    "text_muted": "#8A93A0",
    "accent": "#4F46E5",
    "accent_hover": "#4338CA",
    "accent_text": "#FFFFFF",
    "success": "#17A95C",
    "success_hover": "#138050",
    "success_soft": "#E3F5EB",
    "success_text": "#0F7A44",
    "warning": "#D97706",
    "warning_soft": "#FDF0DC",
    "warning_text": "#92400E",
    "danger": "#DC2626",
    "danger_hover": "#C41E1E",
    "danger_soft": "#FDE8E8",
    "danger_text": "#B91C1C",
    "info": "#2563EB",
    "info_soft": "#E8F0FE",
    "info_text": "#1D4ED8",
}


def is_dark() -> bool:
    """True when the current appearance mode is dark."""
    return ctk.get_appearance_mode().lower() == "dark"


def _palette() -> dict:
    return _DARK if is_dark() else _LIGHT


def color(name: str) -> str:
    """Return a color token for the current appearance mode."""
    return _palette()[name]


# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------
def font(
    size: int,
    weight: str = "normal",
    family: str | None = None,
) -> ctk.CTkFont:
    """Create a CTkFont from the design system's type scale."""
    return ctk.CTkFont(family=family or FONT_FAMILY, size=size, weight=weight)


def h1() -> ctk.CTkFont:
    return font(SIZE_H1, weight="bold")


def h2() -> ctk.CTkFont:
    return font(SIZE_H2, weight="bold")


def h3() -> ctk.CTkFont:
    return font(SIZE_H3, weight="bold")


def body() -> ctk.CTkFont:
    return font(SIZE_BODY)


def small() -> ctk.CTkFont:
    return font(SIZE_SMALL)


def caption() -> ctk.CTkFont:
    return font(SIZE_CAPTION)


def mono() -> ctk.CTkFont:
    return font(SIZE_BODY, family=FONT_MONO)


# ---------------------------------------------------------------------------
# Widget factories
# ---------------------------------------------------------------------------
def make_heading(master, text: str, **kwargs) -> ctk.CTkLabel:
    """Page-level heading (H1)."""
    return ctk.CTkLabel(
        master,
        text=text,
        font=h1(),
        text_color=color("text"),
        anchor="w",
        **kwargs,
    )


def make_subheading(master, text: str, **kwargs) -> ctk.CTkLabel:
    """Section-level heading (H2)."""
    return ctk.CTkLabel(
        master,
        text=text,
        font=h2(),
        text_color=color("text"),
        anchor="w",
        **kwargs,
    )


def make_body(master, text: str, **kwargs) -> ctk.CTkLabel:
    """Body text, left-aligned and wrapping by default."""
    kwargs.setdefault("wraplength", 720)
    kwargs.setdefault("justify", "left")
    return ctk.CTkLabel(
        master,
        text=text,
        font=body(),
        text_color=color("text_secondary"),
        anchor="w",
        **kwargs,
    )


def make_caption(master, text: str, **kwargs) -> ctk.CTkLabel:
    """Small muted helper/caption text."""
    return ctk.CTkLabel(
        master,
        text=text,
        font=caption(),
        text_color=color("text_muted"),
        anchor="w",
        **kwargs,
    )


def make_card(master, **kwargs) -> ctk.CTkFrame:
    """Elevated surface container used across all steps."""
    kwargs.setdefault("fg_color", color("surface"))
    kwargs.setdefault("corner_radius", RADIUS_CARD)
    kwargs.setdefault("border_width", 1)
    kwargs.setdefault("border_color", color("border"))
    return ctk.CTkFrame(master, **kwargs)


def make_primary_button(master, text: str, command=None, **kwargs) -> ctk.CTkButton:
    """Primary call-to-action button."""
    kwargs.setdefault("fg_color", color("accent"))
    kwargs.setdefault("hover_color", color("accent_hover"))
    kwargs.setdefault("text_color", color("accent_text"))
    kwargs.setdefault("font", small())
    kwargs.setdefault("corner_radius", RADIUS_BUTTON)
    kwargs.setdefault("height", 34)
    return ctk.CTkButton(master, text=text, command=command, **kwargs)


def make_secondary_button(master, text: str, command=None, **kwargs) -> ctk.CTkButton:
    """Secondary (outline) button."""
    kwargs.setdefault("fg_color", "transparent")
    kwargs.setdefault("hover_color", color("surface_hover"))
    kwargs.setdefault("text_color", color("text_secondary"))
    kwargs.setdefault("border_width", 1)
    kwargs.setdefault("border_color", color("border"))
    kwargs.setdefault("font", small())
    kwargs.setdefault("corner_radius", RADIUS_BUTTON)
    kwargs.setdefault("height", 34)
    return ctk.CTkButton(master, text=text, command=command, **kwargs)


def make_ghost_button(master, text: str, command=None, **kwargs) -> ctk.CTkButton:
    """Borderless text button used for subtle actions."""
    kwargs.setdefault("fg_color", "transparent")
    kwargs.setdefault("hover_color", color("surface_hover"))
    kwargs.setdefault("text_color", color("text_secondary"))
    kwargs.setdefault("font", small())
    kwargs.setdefault("corner_radius", RADIUS_BUTTON)
    kwargs.setdefault("height", 34)
    return ctk.CTkButton(master, text=text, command=command, **kwargs)


def make_entry(
    master, textvariable=None, placeholder: str | None = None, **kwargs
) -> ctk.CTkEntry:
    """Standard text input styled by the design system."""
    kwargs.setdefault("fg_color", color("surface"))
    kwargs.setdefault("border_color", color("border"))
    kwargs.setdefault("border_width", 1)
    kwargs.setdefault("corner_radius", RADIUS_INPUT)
    kwargs.setdefault("height", 36)
    kwargs.setdefault("font", body())
    kwargs.setdefault("text_color", color("text"))
    kwargs.setdefault("placeholder_text", placeholder)
    return ctk.CTkEntry(master, textvariable=textvariable, **kwargs)
