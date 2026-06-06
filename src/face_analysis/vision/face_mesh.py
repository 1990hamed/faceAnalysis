"""MediaPipe-based face landmark detection and annotation.

Provides :func:`draw_face_mesh` which:

1. Ensures the ``face_landmarker.task`` model file is present (downloads it on
   first use).
2. Runs :class:`mediapipe.tasks.vision.FaceLandmarker` in IMAGE mode on the
   supplied file.
3. Draws tessellation and contour overlays onto a copy of the image.
4. Saves the annotated image into the active session's ``landmarked/`` directory
   (or a ``SavedImages/LandMarked_Images`` fallback) and returns the path plus a
   resized :class:`~PIL.ImageTk.PhotoImage` ready for the GUI canvas.
"""

import urllib.request
from pathlib import Path
from tkinter import messagebox

import cv2
import mediapipe as mp
from PIL import Image, ImageTk

from face_analysis.core.logger import get_session

_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
_MODEL_PATH = Path(__file__).parents[3] / "models" / "face_landmarker.task"

_drawing = mp.tasks.vision.drawing_utils
_styles = mp.tasks.vision.drawing_styles
_FaceLandmarker = mp.tasks.vision.FaceLandmarker
_FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
_FaceLandmarksConnections = mp.tasks.vision.FaceLandmarksConnections
_BaseOptions = mp.tasks.BaseOptions
_VisionRunningMode = mp.tasks.vision.RunningMode


def _ensure_model() -> bool:
    """Download the face landmarker model if not present. Returns True on success."""
    if _MODEL_PATH.exists():
        return True
    _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    session = get_session()
    try:
        if session:
            session.log("info", "Downloading face landmarker model from %s", _MODEL_URL)
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
        if session:
            session.log("info", "Model downloaded to %s", _MODEL_PATH)
        return True
    except Exception as exc:
        if session:
            session.log("error", "Model download failed: %s", exc)
        messagebox.showerror("خطا", f"دانلود مدل ناموفق بود:\n{exc}")
        return False


def draw_face_mesh(
    image_path: str | Path,
    max_faces: int = 1,
    min_detection_confidence: float = 0.5,
    min_tracking_confidence: float = 0.5,
) -> tuple[str, "ImageTk.PhotoImage"] | None:
    """Run MediaPipe FaceLandmarker on *image_path*, save the annotated image into
    the active session's landmarked/ directory (or a fallback dir), and return
    (output_path, resized_tk_image) or None if no face is detected."""
    session = get_session()

    if not _ensure_model():
        return None

    image_path = Path(image_path)
    if session is not None:
        out_dir = session.landmarked_dir
    else:
        out_dir = Path("./Output/SavedImages/LandMarked_Images")
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{image_path.stem}WithLandMark.jpg"

    if session:
        session.log("info", "Running face mesh detection on %s", image_path)

    image_bgr = cv2.imread(str(image_path))
    if image_bgr is None:
        if session:
            session.log("error", "Could not read image: %s", image_path)
        messagebox.showerror("خطا", f"تصویر یافت نشد: {image_path}")
        return None

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    options = _FaceLandmarkerOptions(
        base_options=_BaseOptions(model_asset_path=str(_MODEL_PATH)),
        running_mode=_VisionRunningMode.IMAGE,
        num_faces=max_faces,
        min_face_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )

    with _FaceLandmarker.create_from_options(options) as landmarker:
        result = landmarker.detect(mp_image)

    if not result.face_landmarks:
        if session:
            session.log("warning", "No face detected in %s", image_path)
        messagebox.showwarning(
            "هیچ چهره‌ای شناسایی نشد", "هشدار: هیچ چهره‌ای در تصویر شناسایی نشد."
        )
        return None

    annotated = image_rgb.copy()
    tesselation_spec = _drawing.DrawingSpec(
        color=(0, 255, 0), thickness=1, circle_radius=1
    )

    for face_landmarks in result.face_landmarks:
        _drawing.draw_landmarks(
            image=annotated,
            landmark_list=face_landmarks,
            connections=_FaceLandmarksConnections.FACE_LANDMARKS_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=tesselation_spec,
        )
        _drawing.draw_landmarks(
            image=annotated,
            landmark_list=face_landmarks,
            connections=_FaceLandmarksConnections.FACE_LANDMARKS_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=_styles.get_default_face_mesh_contours_style(),
        )

    pil_image = Image.fromarray(annotated)
    pil_image.save(str(output_path))

    if session:
        session.log(
            "info",
            "Face mesh saved: %s  (faces detected: %d)",
            output_path,
            len(result.face_landmarks),
        )

    tk_image = ImageTk.PhotoImage(pil_image.resize((300, 200)))
    return str(output_path), tk_image
