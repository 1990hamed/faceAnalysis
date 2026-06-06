"""Widget: three-column radio-button panel for selecting facial feature types.

:class:`RadioSelectorPanel` groups eyebrow, nose, and lips options into separate
columns.  Each column binds to a :class:`~tkinter.StringVar` owned by the parent
page.  A single "Confirm & Analyse" button fires the ``on_submit`` callback once
all selections are made.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from face_analysis.gui.theme import SPACE

_EYEBROW_OPTIONS = ["کمانی", "صاف", "باریک", "پیوسته"]
_NOSE_OPTIONS = ["کوچک", "بزرگ", "تیز", "عقابی"]
_LIPS_OPTIONS = ["قلوه", "نازک", "هر دو"]


class RadioSelectorPanel(ttk.Frame):
    """Three-column radio-button panel for eyebrow / nose / lips selection."""

    def __init__(
        self,
        parent: tk.Widget,
        eyebrow_var: tk.StringVar,
        nose_var: tk.StringVar,
        lips_var: tk.StringVar,
        on_submit: Callable[[], None],
        **kwargs: object,
    ) -> None:
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self._eyebrow_var = eyebrow_var
        self._nose_var = nose_var
        self._lips_var = lips_var
        self._on_submit = on_submit
        self._build()

    def _build(self) -> None:
        ttk.Label(
            self,
            text="ویژگی‌های چهره",
            style="Subheading.TLabel",
            anchor="e",
        ).pack(fill="x", padx=SPACE["md"], pady=(SPACE["md"], SPACE["sm"]))

        groups = ttk.Frame(self, style="Card.TFrame")
        groups.pack(fill="both", expand=True, padx=SPACE["md"])
        groups.columnconfigure([0, 1, 2], weight=1, uniform="features")

        self._add_group(groups, 0, "حالت ابرو", self._eyebrow_var, _EYEBROW_OPTIONS)
        self._add_group(groups, 1, "حالت بینی", self._nose_var, _NOSE_OPTIONS)
        self._add_group(groups, 2, "حالت لب", self._lips_var, _LIPS_OPTIONS)

        ttk.Button(
            self,
            text="تأیید و تحلیل",
            style="Accent.TButton",
            command=self._on_submit,
        ).pack(fill="x", padx=SPACE["md"], pady=SPACE["md"])

    def _add_group(
        self,
        parent: tk.Widget,
        col: int,
        label_text: str,
        variable: tk.StringVar,
        options: list[str],
    ) -> None:
        """Add a labelled column of radio buttons for one facial-feature group."""
        frame = ttk.Frame(parent, style="Card.TFrame")
        frame.grid(row=0, column=col, padx=SPACE["sm"], pady=SPACE["sm"], sticky="new")

        ttk.Label(
            frame,
            text=label_text,
            style="Muted.TLabel",
            anchor="e",
        ).pack(fill="x", pady=(0, SPACE["xs"]))

        for option in options:
            ttk.Radiobutton(
                frame,
                text=option,
                variable=variable,
                value=option,
                style="Modern.TRadiobutton",
            ).pack(fill="x", pady=1)
