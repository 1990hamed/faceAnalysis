"""Root application controller: owns shared state and drives page transitions.

:class:`GUIApp` is instantiated once in ``main.py``.  It holds the single
:class:`~face_analysis.config.feature_weights.FeatureWeightsStore` instance and
the ``username`` :class:`~tkinter.StringVar` that flow through all pages.
Page transitions are handled by ``_swap``, which destroys the current frame
before packing the next one.
"""

import tkinter as tk
from tkinter import ttk

from face_analysis.config.feature_weights import FeatureWeightsStore
from face_analysis.gui.pages.analysis_page import AnalysisPage
from face_analysis.gui.pages.instructions_page import InstructionsPage
from face_analysis.gui.pages.landing_page import LandingPage


class GUIApp:
    """Root application controller — owns the Tk window, shared state, and page transitions."""

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._store = FeatureWeightsStore()
        self._username_var = tk.StringVar()

        self._frame: ttk.Frame | None = None

    # ------------------------------------------------------------------
    # Page transitions
    # ------------------------------------------------------------------

    def _swap(self, new_frame: ttk.Frame) -> None:
        """Destroy the current page frame and display *new_frame* in its place."""
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(expand=True, fill="both")

    def show_landing(self) -> None:
        """Navigate to the landing page (username input + weight editor)."""
        self._swap(
            LandingPage(
                self._root,
                store=self._store,
                username_var=self._username_var,
                on_confirm=self.show_instructions,
            )
        )

    def show_instructions(self) -> None:
        """Navigate to the instructions page."""
        self._swap(InstructionsPage(self._root, on_continue=self.show_analysis))

    def show_analysis(self) -> None:
        """Navigate to the main analysis page, passing current username and store."""
        self._swap(
            AnalysisPage(
                self._root,
                store=self._store,
                username=self._username_var.get(),
                on_back=self.show_landing,
                on_exit=self._root.quit,
            )
        )

    def run(self) -> None:
        """Show the landing page and enter the Tkinter main event loop."""
        self.show_landing()
        self._root.mainloop()
