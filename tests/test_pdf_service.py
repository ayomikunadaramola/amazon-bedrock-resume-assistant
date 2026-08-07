from pathlib import Path

import fitz
import pytest

from pdf_service import (
    PDFProcessingError,
    extract_text_from_pdf,
    get_pdf_summary,
    validate_pdf_path,
)


def create_test_pdf(
    file_path: Path,
    text: str = "Ayomikun Adaramola\nSenior Data Engineer",
) -> None:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    document.save(file_path)
    document.close()


def test_validate_pdf_path_accepts_existing_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "resume.pdf"
    create_test_pdf(pdf_path)

    result = validate_pdf_path(pdf_path)

    assert result == pdf_path.resolve()


def test_validate_pdf_path_rejects_missing_file(tmp_path: Path) -> None:
    missing_pdf = tmp_path / "missing.pdf"

    with pytest.raises(PDFProcessingError, match="PDF file not found"):
        validate_pdf_path(missing_pdf)


def test_validate_pdf_path_rejects_non_pdf_file(tmp_path: Path) -> None:
    text_file = tmp_path / "resume.txt"
    text_file.write_text("Resume content", encoding="utf-8")

    with pytest.raises(PDFProcessingError, match="Only PDF files"):
        validate_pdf_path(text_file)


def test_extract_text_from_pdf_returns_resume_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "resume.pdf"
    create_test_pdf(pdf_path)

    extracted_text = extract_text_from_pdf(pdf_path)

    assert "Ayomikun Adaramola" in extracted_text
    assert "Senior Data Engineer" in extracted_text


def test_extract_text_from_empty_pdf_raises_error(tmp_path: Path) -> None:
    pdf_path = tmp_path / "empty.pdf"

    document = fitz.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    with pytest.raises(PDFProcessingError, match="No readable text"):
        extract_text_from_pdf(pdf_path)


def test_get_pdf_summary_returns_document_statistics(
    tmp_path: Path,
) -> None:
    pdf_path = tmp_path / "resume.pdf"
    create_test_pdf(
        pdf_path,
        "Python SQL AWS Amazon Bedrock Data Engineering",
    )

    summary = get_pdf_summary(pdf_path)

    assert summary["file_name"] == "resume.pdf"
    assert summary["page_count"] == 1
    assert summary["word_count"] == 7
    assert summary["character_count"] > 0