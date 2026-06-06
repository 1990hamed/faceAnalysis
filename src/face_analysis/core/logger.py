"""Session-scoped logging and output directory management.

Every analysis run gets its own timestamped directory under Output/sessions/:

    Output/sessions/YYYY-MM-DD_HH-MM-SS_<username>/
        session.log          ← human-readable log for this run
        original/            ← copied original image
        landmarked/          ← MediaPipe-annotated image
        pdf/                 ← generated PDF report

Call `init_session(username)` once at the start of each analysis, then use
`get_session()` to obtain the active SessionContext from anywhere in the app.
"""

import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

_OUTPUT_ROOT = Path("./Output")
_SESSIONS_ROOT = _OUTPUT_ROOT / "sessions"

_active: "SessionContext | None" = None


def _sanitize(name: str) -> str:
    return re.sub(r"[^\w\-]", "_", name.strip()) or "guest"


class SessionContext:
    """Holds paths and the logger for one analysis session."""

    def __init__(self, username: str) -> None:
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        slug = _sanitize(username)
        self.session_dir = _SESSIONS_ROOT / f"{stamp}_{slug}"

        self.original_dir = self.session_dir / "original"
        self.landmarked_dir = self.session_dir / "landmarked"
        self.pdf_dir = self.session_dir / "pdf"

        for d in (self.original_dir, self.landmarked_dir, self.pdf_dir):
            d.mkdir(parents=True, exist_ok=True)

        self.username = username
        self.logger = self._make_logger()
        self.logger.info("Session started for user '%s'", username)
        self.logger.info("Session directory: %s", self.session_dir)

    def _make_logger(self) -> logging.Logger:
        log_path = self.session_dir / "session.log"
        logger = logging.getLogger(f"face_analysis.session.{id(self)}")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s  %(levelname)-8s  %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter("%(levelname)s  %(message)s"))
        logger.addHandler(ch)

        return logger

    def save_original(self, source: str | Path) -> Path:
        """Copy *source* into this session's original/ directory."""
        src = Path(source)
        dest = self.original_dir / src.name
        shutil.copy2(src, dest)
        self.logger.info("Original image saved: %s", dest)
        return dest

    def save_landmarked(self, source: str | Path) -> Path:
        """Copy *source* into this session's landmarked/ directory."""
        src = Path(source)
        dest = self.landmarked_dir / src.name
        shutil.copy2(src, dest)
        self.logger.info("Landmarked image saved: %s", dest)
        return dest

    def save_pdf(self, source: str | Path) -> Path:
        """Copy *source* into this session's pdf/ directory."""
        src = Path(source)
        dest = self.pdf_dir / src.name
        shutil.copy2(src, dest)
        self.logger.info("PDF report saved: %s", dest)
        return dest

    def log(self, level: str, msg: str, *args: object) -> None:
        getattr(self.logger, level)(msg, *args)


def init_session(username: str) -> SessionContext:
    """Create a new SessionContext and make it the active session."""
    global _active
    _active = SessionContext(username)
    return _active


def get_session() -> "SessionContext | None":
    """Return the currently active SessionContext, or None if not initialised."""
    return _active
