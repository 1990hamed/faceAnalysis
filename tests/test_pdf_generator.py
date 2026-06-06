"""Tests for core/pdf_generator.py: file creation, naming, path handling, and edge cases."""

from face_analysis.core.pdf_generator import generate_pdf

SAMPLE_TEXTS = {
    "common_text": "آرکتایپ‌های مشترک: آتنا و آپولو",
    "missing_text": "آرکتایپ‌های اضافه شده: هرا و زئوس",
    "method_text": "روش: وجودی شناختی رفتاری",
    "man_feature_text": "برنامه ریز, آینده نگر",
    "woman_feature_text": "عاقل, همکار",
}


def test_generate_pdf_creates_file(tmp_path):
    pdf = generate_pdf(SAMPLE_TEXTS, "test_user", None, None, output_dir=tmp_path)
    assert pdf.exists()
    assert pdf.suffix == ".pdf"
    assert pdf.stat().st_size > 0


def test_generate_pdf_filename_contains_username(tmp_path):
    pdf = generate_pdf(SAMPLE_TEXTS, "ali", None, None, output_dir=tmp_path)
    assert "ali" in pdf.name


def test_generate_pdf_creates_output_dir(tmp_path):
    nested = tmp_path / "a" / "b" / "c"
    pdf = generate_pdf(SAMPLE_TEXTS, "u", None, None, output_dir=nested)
    assert nested.exists()
    assert pdf.exists()


def test_generate_pdf_nonexistent_image_paths_do_not_raise(tmp_path):
    pdf = generate_pdf(
        SAMPLE_TEXTS,
        "u",
        original_image_path="/no/such/file.jpg",
        landmarked_image_path="/no/such/landmark.jpg",
        output_dir=tmp_path,
    )
    assert pdf.exists()


def test_generate_pdf_accepts_string_output_dir(tmp_path):
    pdf = generate_pdf(SAMPLE_TEXTS, "u", None, None, output_dir=str(tmp_path))
    assert pdf.exists()


def test_generate_pdf_overwrites_existing(tmp_path):
    pdf1 = generate_pdf(SAMPLE_TEXTS, "u", None, None, output_dir=tmp_path)
    pdf2 = generate_pdf(SAMPLE_TEXTS, "u", None, None, output_dir=tmp_path)
    assert pdf1 == pdf2
    assert pdf2.stat().st_size > 0


def test_generate_pdf_empty_texts(tmp_path):
    pdf = generate_pdf({}, "empty_user", None, None, output_dir=tmp_path)
    assert pdf.exists()
