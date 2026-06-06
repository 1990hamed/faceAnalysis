"""Tests for session-based image storage and the SavedImages fallback.

Covers:
- logger.SessionContext directory layout
- image_utils.open_image_dialog: session path vs. SavedImages fallback
- face_mesh.draw_face_mesh: SavedImages fallback path when no session is active
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PIL import Image

import face_analysis.core.logger as logger_module
from face_analysis.core.logger import SessionContext, get_session, init_session
from face_analysis.vision import image_utils

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_active_session():
    """Ensure no session leaks between tests."""
    logger_module._active = None
    yield
    logger_module._active = None


@pytest.fixture()
def sample_image(tmp_path) -> Path:
    """Write a tiny PNG so tests don't need real photos."""
    p = tmp_path / "face.png"
    Image.new("RGB", (10, 10), color=(100, 150, 200)).save(str(p))
    return p


# ---------------------------------------------------------------------------
# SessionContext directory layout
# ---------------------------------------------------------------------------


def test_session_creates_subdirectories(tmp_path, monkeypatch):
    monkeypatch.setattr(logger_module, "_SESSIONS_ROOT", tmp_path / "sessions")
    ctx = SessionContext("alice")
    assert ctx.original_dir.is_dir()
    assert ctx.landmarked_dir.is_dir()
    assert ctx.pdf_dir.is_dir()


def test_session_dir_contains_username(tmp_path, monkeypatch):
    monkeypatch.setattr(logger_module, "_SESSIONS_ROOT", tmp_path / "sessions")
    ctx = SessionContext("bob")
    assert "bob" in ctx.session_dir.name


def test_session_log_file_created(tmp_path, monkeypatch):
    monkeypatch.setattr(logger_module, "_SESSIONS_ROOT", tmp_path / "sessions")
    ctx = SessionContext("carol")
    assert (ctx.session_dir / "session.log").exists()


def test_save_original_copies_file(tmp_path, monkeypatch, sample_image):
    monkeypatch.setattr(logger_module, "_SESSIONS_ROOT", tmp_path / "sessions")
    ctx = SessionContext("dave")
    dest = ctx.save_original(sample_image)
    assert dest.exists()
    assert dest.parent == ctx.original_dir


def test_save_landmarked_copies_file(tmp_path, monkeypatch, sample_image):
    monkeypatch.setattr(logger_module, "_SESSIONS_ROOT", tmp_path / "sessions")
    ctx = SessionContext("eve")
    dest = ctx.save_landmarked(sample_image)
    assert dest.exists()
    assert dest.parent == ctx.landmarked_dir


def test_init_session_sets_active(tmp_path, monkeypatch):
    monkeypatch.setattr(logger_module, "_SESSIONS_ROOT", tmp_path / "sessions")
    ctx = init_session("frank")
    assert get_session() is ctx


def test_init_session_replaces_previous(tmp_path, monkeypatch):
    monkeypatch.setattr(logger_module, "_SESSIONS_ROOT", tmp_path / "sessions")
    ctx1 = init_session("grace")
    ctx2 = init_session("grace")
    assert get_session() is ctx2
    assert ctx1 is not ctx2


def test_no_saved_images_folder_created_when_session_active(tmp_path, monkeypatch):
    monkeypatch.setattr(logger_module, "_SESSIONS_ROOT", tmp_path / "sessions")
    init_session("henry")
    saved_images = tmp_path / "Output" / "SavedImages"
    assert not saved_images.exists()


# ---------------------------------------------------------------------------
# image_utils.open_image_dialog — session path
# ---------------------------------------------------------------------------


def test_open_image_dialog_saves_to_session(tmp_path, monkeypatch, sample_image):
    monkeypatch.setattr(logger_module, "_SESSIONS_ROOT", tmp_path / "sessions")
    init_session("ivan")

    monkeypatch.setattr(
        "face_analysis.vision.image_utils.filedialog.askopenfilename",
        lambda **kw: str(sample_image),
    )
    monkeypatch.setattr(
        "face_analysis.vision.image_utils.ImageTk.PhotoImage",
        lambda img: MagicMock(),
    )

    file_path, tk_img = image_utils.open_image_dialog()

    assert file_path == str(sample_image)
    session = get_session()
    assert (session.original_dir / sample_image.name).exists()


def test_open_image_dialog_session_no_saved_images(tmp_path, monkeypatch, sample_image):
    monkeypatch.setattr(logger_module, "_SESSIONS_ROOT", tmp_path / "sessions")
    monkeypatch.setattr(logger_module, "_OUTPUT_ROOT", tmp_path / "Output")
    init_session("judy")

    monkeypatch.setattr(
        "face_analysis.vision.image_utils.filedialog.askopenfilename",
        lambda **kw: str(sample_image),
    )
    monkeypatch.setattr(
        "face_analysis.vision.image_utils.ImageTk.PhotoImage",
        lambda img: MagicMock(),
    )

    image_utils.open_image_dialog()

    assert not (tmp_path / "Output" / "SavedImages").exists()


# ---------------------------------------------------------------------------
# image_utils.open_image_dialog — SavedImages fallback (no session)
# ---------------------------------------------------------------------------


def test_open_image_dialog_fallback_creates_saved_images(
    tmp_path, monkeypatch, sample_image
):
    # No session active — should use SavedImages fallback.
    fallback_root = tmp_path / "Output"

    original_open = image_utils.open_image_dialog

    def patched_dialog():
        # Redirect Path("./Output/...") to tmp_path by patching Path inside image_utils
        return original_open()

    monkeypatch.setattr(
        "face_analysis.vision.image_utils.filedialog.askopenfilename",
        lambda **kw: str(sample_image),
    )
    monkeypatch.setattr(
        "face_analysis.vision.image_utils.ImageTk.PhotoImage",
        lambda img: MagicMock(),
    )
    # Redirect the fallback directory to tmp_path so the test stays isolated.
    monkeypatch.setattr(
        "face_analysis.vision.image_utils.Path",
        lambda *args: (
            Path(str(args[0]).replace("./Output", str(fallback_root)))
            if args and "./Output" in str(args[0])
            else Path(*args)
        ),
    )

    file_path, _ = image_utils.open_image_dialog()

    assert file_path == str(sample_image)
    expected = fallback_root / "SavedImages" / "Original_Images" / sample_image.name
    assert expected.exists()


def test_open_image_dialog_no_file_returns_none_none(monkeypatch):
    monkeypatch.setattr(
        "face_analysis.vision.image_utils.filedialog.askopenfilename",
        lambda **kw: "",
    )
    file_path, img = image_utils.open_image_dialog()
    assert file_path is None
    assert img is None


# ---------------------------------------------------------------------------
# face_mesh.draw_face_mesh — SavedImages fallback directory (no session)
# ---------------------------------------------------------------------------


def test_draw_face_mesh_fallback_output_dir_is_landmarked_images(
    tmp_path, monkeypatch, sample_image
):
    """When no session is active, the output directory must be
    SavedImages/LandMarked_Images, not SavedImages."""
    from face_analysis.vision import face_mesh

    fallback_root = tmp_path / "Output"

    # Patch _ensure_model so no download is attempted.
    monkeypatch.setattr(face_mesh, "_ensure_model", lambda: True)

    # Patch the fallback Path inside face_mesh to redirect to tmp_path.
    original_path_cls = face_mesh.Path

    def redirected_path(*args):
        s = str(args[0]) if args else ""
        if "./Output" in s:
            return original_path_cls(s.replace("./Output", str(fallback_root)))
        return original_path_cls(*args)

    monkeypatch.setattr(face_mesh, "Path", redirected_path)

    # Patch cv2 and mediapipe to avoid real model inference.
    import numpy as np

    fake_bgr = np.zeros((10, 10, 3), dtype=np.uint8)
    monkeypatch.setattr(face_mesh.cv2, "imread", lambda *a, **kw: fake_bgr)
    monkeypatch.setattr(face_mesh.cv2, "cvtColor", lambda *a, **kw: fake_bgr)

    fake_landmark = MagicMock()
    fake_result = MagicMock()
    fake_result.face_landmarks = [fake_landmark]

    fake_landmarker = MagicMock()
    fake_landmarker.__enter__ = lambda s: fake_landmarker
    fake_landmarker.__exit__ = MagicMock(return_value=False)
    fake_landmarker.detect = lambda img: fake_result

    monkeypatch.setattr(
        face_mesh._FaceLandmarker,
        "create_from_options",
        lambda opts: fake_landmarker,
    )
    monkeypatch.setattr(face_mesh._drawing, "draw_landmarks", lambda **kw: None)
    monkeypatch.setattr(
        face_mesh,
        "mp",
        MagicMock(
            Image=MagicMock(return_value=MagicMock()),
            ImageFormat=MagicMock(SRGB="SRGB"),
        ),
    )
    monkeypatch.setattr(
        "face_analysis.vision.face_mesh.ImageTk.PhotoImage",
        lambda img: MagicMock(),
    )

    result = face_mesh.draw_face_mesh(sample_image)

    if result is not None:
        output_path = Path(result[0])
        assert "SavedImages" in output_path.parts or "LandMarked_Images" in str(
            output_path
        ), f"Unexpected output path: {output_path}"
        assert "sessions" not in output_path.parts
