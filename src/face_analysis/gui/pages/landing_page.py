"""Landing page: username entry and optional weight-coefficient editor.

This is the first screen the operator sees.  It lets them enter the client's
name and optionally adjust the feature-to-archetype weight mappings before
starting an analysis session.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from face_analysis.config.feature_weights import FeatureWeightsStore
from face_analysis.gui.theme import SPACE
from face_analysis.gui.widgets.feature_input import FeatureInputGrid


class LandingPage(ttk.Frame):
    """First page: collect the username and allow weight overrides."""

    def __init__(
        self,
        parent: tk.Widget,
        store: FeatureWeightsStore,
        username_var: tk.StringVar,
        on_confirm: Callable[[], None],
        **kwargs: object,
    ) -> None:
        super().__init__(parent, style="TFrame", **kwargs)
        self._store = store
        self._username_var = username_var
        self._on_confirm = on_confirm
        self._build()

    def _build(self) -> None:
        # Centered card holding the whole landing experience.
        card = ttk.Frame(self, style="Card.TFrame")
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(
            card,
            text="سیستم تحلیل چهره",
            style="Title.TLabel",
            anchor="e",
        ).pack(fill="x", padx=SPACE["xl"], pady=(SPACE["xl"], SPACE["xs"]))

        ttk.Label(
            card,
            text="تحلیل آرکیتایپ بر اساس ویژگی‌های چهره",
            style="Muted.TLabel",
            anchor="e",
        ).pack(fill="x", padx=SPACE["xl"], pady=(0, SPACE["lg"]))

        ttk.Separator(card, orient="horizontal").pack(
            fill="x", padx=SPACE["xl"], pady=(0, SPACE["sm"])
        )

        FeatureInputGrid(card, self._store).pack(
            fill="x", padx=SPACE["lg"], pady=SPACE["sm"]
        )

        ttk.Separator(card, orient="horizontal").pack(
            fill="x", padx=SPACE["xl"], pady=SPACE["sm"]
        )

        # Username row.
        user_frame = ttk.Frame(card, style="Card.TFrame")
        user_frame.pack(fill="x", padx=SPACE["xl"], pady=(SPACE["sm"], SPACE["xl"]))

        ttk.Button(
            user_frame,
            text="تأیید و ادامه",
            style="Accent.TButton",
            command=self._on_confirm,
        ).pack(side="left")

        entry = ttk.Entry(
            user_frame,
            textvariable=self._username_var,
            style="Modern.TEntry",
            justify="right",
            width=28,
        )
        entry.pack(side="right")
        entry.focus_set()

        ttk.Label(
            user_frame,
            text="نام کاربر:",
            style="Subheading.TLabel",
        ).pack(side="right", padx=SPACE["sm"])
