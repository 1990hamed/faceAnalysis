"""PDF report generation with RTL (right-to-left) Farsi text support.

Uses ReportLab to render analysis results on an A4 page.  Farsi text is reshaped
with *arabic_reshaper* and passed through the BiDi algorithm before drawing so
that characters and words appear in the correct visual order.

The bundled Vazirmatn-Bold font is registered at import time if the file exists;
otherwise the generator falls back to Helvetica so the module always works in
test environments that lack the font asset.

Call :func:`generate_pdf` once per analysis run.  When a
:class:`~face_analysis.core.logger.SessionContext` is active the PDF is saved
directly into the session's ``pdf/`` subdirectory.
"""

from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from face_analysis.core.logger import get_session

_FONT_PATH = Path(__file__).parents[3] / "Font" / "Vazirmatn-Bold.ttf"
_FONT_NAME = "Vazirmatn-Bold"

if _FONT_PATH.exists():
    pdfmetrics.registerFont(TTFont(_FONT_NAME, str(_FONT_PATH)))
else:
    _FONT_NAME = "Helvetica"


def _rtl(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))


def generate_pdf(
    texts: dict[str, str],
    username: str,
    original_image_path: str | None,
    landmarked_image_path: str | None,
    output_dir: Path | str | None = None,
) -> Path:
    """Render the analysis result to a PDF and return its path.

    When a SessionContext is active, *output_dir* defaults to the session's pdf/
    directory so the report lands alongside the session's images and log file.
    """
    session = get_session()

    if output_dir is None:
        out_dir = session.pdf_dir if session is not None else Path("./Output")
    else:
        out_dir = Path(output_dir)

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"analysis_{username}.pdf"

    if session:
        session.log("info", "Generating PDF report: %s", pdf_path)

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    c.setFont(_FONT_NAME, 10)

    rtl_texts = {k: _rtl(v) for k, v in texts.items()}

    y = 800
    line_gap = 60

    for key in (
        "common_text",
        "missing_text",
        "man_feature_text",
        "woman_feature_text",
        "method_text",
    ):
        value = rtl_texts.get(key, "")
        if key in ("common_text", "missing_text", "method_text"):
            c.drawCentredString(A4[0] / 2, y, value)
            y -= line_gap
        else:
            for part in value.split(",")[::-1]:
                c.drawCentredString(A4[0] / 2, y, part.strip())
                y -= 50
            y -= line_gap

    c.showPage()

    if original_image_path and Path(original_image_path).exists():
        c.drawImage(
            original_image_path,
            x=100,
            y=500,
            width=400,
            height=300,
            preserveAspectRatio=True,
            anchor="c",
        )
    if landmarked_image_path and Path(landmarked_image_path).exists():
        c.drawImage(
            landmarked_image_path,
            x=100,
            y=100,
            width=400,
            height=300,
            preserveAspectRatio=True,
            anchor="c",
        )

    c.save()

    if session:
        session.log("info", "PDF saved successfully: %s", pdf_path)

    return pdf_path
