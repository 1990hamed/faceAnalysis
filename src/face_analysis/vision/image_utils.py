"""Image I/O utilities: file-picker dialog and latest-image lookup.

:func:`open_image_dialog` opens a native file-picker, copies the chosen image
into the active session's ``original/`` directory (or a ``SavedImages`` fallback
when no session is active), and returns a resized
:class:`~PIL.ImageTk.PhotoImage` for immediate display.

:func:`get_latest_image` scans a directory and returns the most-recently
modified image file, useful for pre-populating the canvas after a session
restart.
"""

import os
from pathlib import Path
from tkinter import filedialog

from PIL import Image, ImageTk

from face_analysis.core.logger import get_session


def open_image_dialog() -> tuple[str, "ImageTk.PhotoImage"] | tuple[None, None]:
    """Open a file-picker dialog, copy the chosen image into the active session's
    original/ directory, and return (file_path, resized_tk_image) or (None, None)."""
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.png;*.jpeg")]
    )
    if not file_path:
        return None, None

    session = get_session()
    if session is not None:
        session.save_original(file_path)
        session.log("info", "Image selected by user: %s", file_path)
    else:
        # Fallback when no session is active (e.g. unit tests).
        out_dir = Path("./Output/SavedImages/Original_Images")
        out_dir.mkdir(parents=True, exist_ok=True)
        import shutil

        shutil.copy2(file_path, out_dir / Path(file_path).name)

    img = Image.open(file_path).resize((300, 200))
    return file_path, ImageTk.PhotoImage(img)


def get_latest_image(directory: str | Path) -> str | None:
    """Return the path of the most-recently modified image in *directory*, or None."""
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return None

    image_exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
    images = [p for p in dir_path.iterdir() if p.suffix.lower() in image_exts]
    if not images:
        return None

    return str(max(images, key=os.path.getmtime))
