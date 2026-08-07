from __future__ import annotations

from pathlib import Path

import fitz


class PDFProcessingError(Exception):
    """Raised when a PDF résumé cannot be processed."""


def validate_pdf_path(file_path: str | Path) -> Path:
    """
    Validate that the supplied path points to an existing PDF file.

    Args:
        file_path: Path to the résumé PDF.

    Returns:
        A resolved Path object.

    Raises:
        PDFProcessingError: If the file does not exist, is not a file,
        or does not have a .pdf extension.
    """
    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        raise PDFProcessingError(f"PDF file not found: {path}")

    if not path.is_file():
        raise PDFProcessingError(f"The supplied path is not a file: {path}")

    if path.suffix.lower() != ".pdf":
        raise PDFProcessingError("Only PDF files are supported.")

    return path


def extract_text_from_pdf(file_path: str | Path) -> str:
    """
    Extract readable text from a résumé PDF.

    Args:
        file_path: Path to the résumé PDF.

    Returns:
        Extracted text from all pages.

    Raises:
        PDFProcessingError: If the PDF is encrypted, damaged, empty,
        or contains no extractable text.
    """
    path = validate_pdf_path(file_path)

    try:
        document = fitz.open(path)
    except Exception as error:
        raise PDFProcessingError(
            f"Unable to open the PDF: {error}"
        ) from error

    try:
        if document.is_encrypted and not document.authenticate(""):
            raise PDFProcessingError(
                "The PDF is password-protected. Remove the password and try again."
            )

        if document.page_count == 0:
            raise PDFProcessingError("The PDF contains no pages.")

        pages: list[str] = []

        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text").strip()

            if page_text:
                pages.append(page_text)

        extracted_text = "\n\n".join(pages).strip()

        if not extracted_text:
            raise PDFProcessingError(
                "No readable text was found. The PDF may be scanned or image-based."
            )

        return extracted_text

    finally:
        document.close()


def get_pdf_summary(file_path: str | Path) -> dict[str, int | str]:
    """
    Return basic information about a résumé PDF.

    Args:
        file_path: Path to the résumé PDF.

    Returns:
        Dictionary containing the file name, page count,
        character count, and word count.
    """
    path = validate_pdf_path(file_path)
    extracted_text = extract_text_from_pdf(path)

    try:
        document = fitz.open(path)
        page_count = document.page_count
    finally:
        document.close()

    return {
        "file_name": path.name,
        "page_count": page_count,
        "character_count": len(extracted_text),
        "word_count": len(extracted_text.split()),
    }