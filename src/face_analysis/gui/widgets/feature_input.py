"""Widget: editable grid of feature-to-archetype weight entries.

:class:`FeatureInputGrid` renders one labelled :class:`~tkinter.ttk.Entry` per
feature from the active :class:`~face_analysis.config.feature_weights.FeatureWeightsStore`.
An "Update weights" button calls :meth:`~face_analysis.config.feature_weights.FeatureWeightsStore.update_many`
to validate and persist all entries atomically.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from face_analysis.config.feature_weights import FeatureWeightsStore
from face_analysis.gui.theme import SPACE


class FeatureInputGrid(ttk.Frame):
    """Editable weight-entry grid that lets the user override archetype mappings."""

    _COLUMNS = 3

    def __init__(
        self,
        parent: tk.Widget,
        store: FeatureWeightsStore,
        on_update: Callable[[], None] | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self._store = store
        self._on_update = on_update
        self._entries: dict[str, ttk.Entry] = {}
        self._build()

    def _build(self) -> None:
        header = ttk.Label(
            self,
            text="ضرایب آرکیتایپ",
            style="Subheading.TLabel",
            anchor="e",
        )
        header.pack(fill="x", padx=SPACE["md"], pady=(SPACE["md"], SPACE["xs"]))

        ttk.Label(
            self,
            text="برای هر ویژگی، شماره آرکیتایپ‌ها را با کاما جدا کنید (۱ تا ۷).",
            style="Muted.TLabel",
            anchor="e",
        ).pack(fill="x", padx=SPACE["md"], pady=(0, SPACE["sm"]))

        grid = ttk.Frame(self, style="Card.TFrame")
        grid.pack(fill="x", padx=SPACE["md"], pady=(0, SPACE["sm"]))
        for c in range(self._COLUMNS):
            grid.columnconfigure(c, weight=1, uniform="weights")

        weights = self._store.all()
        row, col = 0, 0
        for feature, value in weights.items():
            cell = ttk.Frame(grid, style="Card.TFrame")
            cell.grid(
                row=row,
                column=col,
                padx=SPACE["sm"],
                pady=SPACE["xs"],
                sticky="ew",
            )

            ttk.Label(
                cell,
                text=feature,
                style="Muted.TLabel",
                anchor="e",
            ).pack(fill="x")

            entry = ttk.Entry(cell, style="Modern.TEntry", justify="center")
            entry.insert(0, value)
            entry.pack(fill="x", pady=(SPACE["xs"], 0))
            self._entries[feature] = entry

            col += 1
            if col >= self._COLUMNS:
                col = 0
                row += 1

        ttk.Button(
            self,
            text="به‌روزرسانی ضرایب",
            style="Secondary.TButton",
            command=self._apply,
        ).pack(anchor="e", padx=SPACE["md"], pady=(SPACE["xs"], SPACE["md"]))

    def _apply(self) -> None:
        """Collect current entry values, validate via the store, and fire the optional callback."""
        raw_values = {f: e.get() for f, e in self._entries.items()}
        if self._store.update_many(raw_values):
            if self._on_update:
                self._on_update()
