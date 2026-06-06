"""Central design system for the GUI: color palette, fonts, spacing tokens, and
ttk style registration. Import :data:`COLORS`, :data:`FONTS`, :data:`SPACE` for
tokens and call :func:`apply_theme` once at startup to style every ttk widget.
"""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from tkinter import ttk

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------

# Modern, calm palette — deep slate surfaces with an indigo/violet accent.
COLORS: dict[str, str] = {
    "bg": "#0f172a",  # app background (slate-900)
    "surface": "#1e293b",  # cards / panels (slate-800)
    "surface_alt": "#273449",  # hovered / nested surface
    "border": "#334155",  # hairline borders (slate-700)
    "text": "#f1f5f9",  # primary text (slate-100)
    "text_muted": "#94a3b8",  # secondary text (slate-400)
    "accent": "#6366f1",  # primary action (indigo-500)
    "accent_hover": "#818cf8",  # indigo-400
    "accent_active": "#4f46e5",  # indigo-600
    "danger": "#ef4444",  # destructive (red-500)
    "danger_hover": "#f87171",  # red-400
    "danger_active": "#dc2626",  # red-600
    "success": "#22c55e",  # green-500
    "field": "#0b1220",  # input background
    "field_focus": "#13203a",  # focused input background
}

# Logical font roles → resolved at apply_theme() time to the registered family.
FONTS: dict[str, tuple[str, int, str]] = {}

# 8-pt spacing scale.
SPACE: dict[str, int] = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

_FONT_DIR = Path(__file__).parents[3] / "Font"
_FONT_FAMILY = "Vazirmatn"
_FALLBACK_FAMILY = "Segoe UI"


# ---------------------------------------------------------------------------
# Font registration
# ---------------------------------------------------------------------------


def _register_fonts() -> str:
    """Load the bundled Vazirmatn family so Tk can use it by name.

    Returns the family name actually available (Vazirmatn if registration
    succeeded, otherwise a sane system fallback).
    """
    if not _FONT_DIR.is_dir():
        return _FALLBACK_FAMILY

    if sys.platform == "win32":
        try:
            import ctypes

            gdi = ctypes.windll.gdi32
            fr_private = 0x10
            for ttf in _FONT_DIR.glob("Vazirmatn-*.ttf"):
                gdi.AddFontResourceExW(str(ttf), fr_private, 0)
        except Exception:
            return _FALLBACK_FAMILY

    # Verify Tk can actually see the family now.
    try:
        if _FONT_FAMILY in tkfont.families():
            return _FONT_FAMILY
    except tk.TclError:
        pass
    return _FONT_FAMILY  # registered with GDI; Tk usually resolves it by name


def _build_font_roles(family: str) -> None:
    FONTS.update(
        {
            "title": (family, 26, "bold"),
            "heading": (family, 18, "bold"),
            "subheading": (family, 14, "bold"),
            "body": (family, 12, "normal"),
            "body_lg": (family, 14, "normal"),
            "result": (family, 16, "bold"),
            "button": (family, 12, "bold"),
            "caption": (family, 10, "normal"),
        }
    )


# ---------------------------------------------------------------------------
# ttk style configuration
# ---------------------------------------------------------------------------


def apply_theme(root: tk.Tk) -> None:
    """Register fonts and configure every ttk style used by the app."""
    family = _register_fonts()
    _build_font_roles(family)

    root.configure(bg=COLORS["bg"])
    # Make the default Tk (non-ttk) widgets inherit sensible colors too.
    root.option_add("*background", COLORS["bg"])
    root.option_add("*foreground", COLORS["text"])

    style = ttk.Style(root)
    try:
        style.theme_use("clam")  # most themeable base on every platform
    except tk.TclError:
        pass

    # --- containers -------------------------------------------------------
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Surface.TFrame", background=COLORS["surface"])
    style.configure(
        "Card.TFrame",
        background=COLORS["surface"],
        relief="flat",
        borderwidth=0,
    )
    style.configure("Header.TFrame", background=COLORS["surface"])

    # --- labels -----------------------------------------------------------
    style.configure(
        "TLabel",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=FONTS["body"],
    )
    style.configure(
        "Surface.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=FONTS["body"],
    )
    style.configure(
        "Title.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=FONTS["title"],
    )
    style.configure(
        "Heading.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=FONTS["heading"],
    )
    style.configure(
        "Subheading.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=FONTS["subheading"],
    )
    style.configure(
        "Muted.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text_muted"],
        font=FONTS["body"],
    )
    style.configure(
        "Result.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["accent_hover"],
        font=FONTS["result"],
    )

    # --- buttons ----------------------------------------------------------
    # Accent (primary) button.
    style.configure(
        "Accent.TButton",
        background=COLORS["accent"],
        foreground="#ffffff",
        font=FONTS["button"],
        borderwidth=0,
        focusthickness=0,
        padding=(SPACE["md"], SPACE["sm"]),
        relief="flat",
    )
    style.map(
        "Accent.TButton",
        background=[
            ("pressed", COLORS["accent_active"]),
            ("active", COLORS["accent_hover"]),
        ],
        foreground=[("disabled", COLORS["text_muted"])],
    )

    # Secondary (ghost) button.
    style.configure(
        "Secondary.TButton",
        background=COLORS["surface_alt"],
        foreground=COLORS["text"],
        font=FONTS["button"],
        borderwidth=1,
        bordercolor=COLORS["border"],
        focusthickness=0,
        padding=(SPACE["md"], SPACE["sm"]),
        relief="flat",
    )
    style.map(
        "Secondary.TButton",
        background=[
            ("pressed", COLORS["border"]),
            ("active", COLORS["border"]),
        ],
    )

    # Danger button (exit).
    style.configure(
        "Danger.TButton",
        background=COLORS["surface_alt"],
        foreground=COLORS["danger_hover"],
        font=FONTS["button"],
        borderwidth=1,
        bordercolor=COLORS["border"],
        focusthickness=0,
        padding=(SPACE["md"], SPACE["sm"]),
        relief="flat",
    )
    style.map(
        "Danger.TButton",
        background=[
            ("pressed", COLORS["danger_active"]),
            ("active", COLORS["danger"]),
        ],
        foreground=[("active", "#ffffff")],
    )

    # --- entries ----------------------------------------------------------
    style.configure(
        "Modern.TEntry",
        fieldbackground=COLORS["field"],
        background=COLORS["field"],
        foreground=COLORS["text"],
        insertcolor=COLORS["accent_hover"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        borderwidth=1,
        relief="flat",
        padding=SPACE["sm"],
        font=FONTS["body"],
    )
    style.map(
        "Modern.TEntry",
        fieldbackground=[("focus", COLORS["field_focus"])],
        bordercolor=[("focus", COLORS["accent"])],
        lightcolor=[("focus", COLORS["accent"])],
        darkcolor=[("focus", COLORS["accent"])],
    )

    # --- radio buttons ----------------------------------------------------
    style.configure(
        "Modern.TRadiobutton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=FONTS["body_lg"],
        focusthickness=0,
        indicatorcolor=COLORS["field"],
        padding=(SPACE["sm"], SPACE["xs"]),
    )
    style.map(
        "Modern.TRadiobutton",
        background=[("active", COLORS["surface_alt"])],
        foreground=[("active", COLORS["accent_hover"])],
        indicatorcolor=[("selected", COLORS["accent"])],
    )

    # --- separators -------------------------------------------------------
    style.configure("TSeparator", background=COLORS["border"])
