"""Entry point for the Face Analysis application.

Initialises the Tk root window, applies the design theme, and delegates control
to :class:`~face_analysis.gui.app.GUIApp` which manages all page transitions.
"""

import tkinter as tk
from pathlib import Path

from face_analysis.gui.app import GUIApp
from face_analysis.gui.theme import COLORS, apply_theme

_ICON = Path(__file__).parent / "assets" / "icon.ico"


def main() -> None:
    """Bootstrap the GUI: create the root window, apply the theme, and start the event loop."""
    root = tk.Tk()
    root.title("سیستم تحلیل چهره")
    root.geometry("1100x760")
    root.minsize(900, 640)

    if _ICON.exists():
        root.iconbitmap(str(_ICON))

    apply_theme(root)
    root.configure(bg=COLORS["bg"])

    GUIApp(root).run()


if __name__ == "__main__":
    main()
