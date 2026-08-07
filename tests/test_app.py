from __future__ import annotations

import app
from pdf_service import PDFProcessingError


# =========================================================
# OPTION 1 — REWRITE RÉSUMÉ BULLET
# =========================================================


def test_rewrite_bullet_rejects_empty_input(
    monkeypatch,
    capsys,
) -> None:
    """An empty résumé bullet should display a validation message."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "",
    )

    app.rewrite_bullet()

    captured = capsys.readouterr()

    assert "Please enter a résumé bullet." in captured.out


def test_rewrite_bullet_sends_prompt_to_response_service(
    monkeypatch,
    capsys,
) -> None:
    """A valid bullet should be sent to the response service."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "Built data pipelines using Python and SQL.",
    )

    captured_prompt: dict[str, str] = {}

    def fake_generate_response(prompt: str) -> str:
        captured_prompt["prompt"] = prompt
        return "Improved résumé bullet."

    monkeypatch.setattr(
        app,
        "generate_response",
        fake_generate_response,
    )

    app.rewrite_bullet()

    captured = capsys.readouterr()

    assert "Built data pipelines using Python and SQL." in (
        captured_prompt["prompt"]
    )

    assert "Improved résumé bullet." in captured.out


def test_rewrite_bullet_handles_response_error(
    monkeypatch,
    capsys,
) -> None:
    """Response-service failures should be handled cleanly."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "Built data pipelines using Python.",
    )

    def raise_error(_: str) -> str:
        raise RuntimeError("Model unavailable")

    monkeypatch.setattr(
        app,
        "generate_response",
        raise_error,
    )

    app.rewrite_bullet()

    captured = capsys.readouterr()

    assert "Unable to generate response" in captured.out
    assert "Model unavailable" in captured.out


# =========================================================
# OPTION 2 — EVALUATE RÉSUMÉ BULLET
# =========================================================


def test_evaluate_bullet_rejects_empty_input(
    monkeypatch,
    capsys,
) -> None:
    """An empty bullet should not be evaluated."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "",
    )

    app.evaluate_bullet()

    captured = capsys.readouterr()

    assert "Please enter a résumé bullet." in captured.out


def test_evaluate_bullet_processes_valid_input(
    monkeypatch,
    capsys,
) -> None:
    """A valid résumé bullet should be evaluated."""

    bullet = (
        "Optimized PostgreSQL queries and improved "
        "reporting performance."
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: bullet,
    )

    captured_prompt: dict[str, str] = {}

    def fake_generate_response(prompt: str) -> str:
        captured_prompt["prompt"] = prompt
        return "Bullet evaluation completed."

    monkeypatch.setattr(
        app,
        "generate_response",
        fake_generate_response,
    )

    app.evaluate_bullet()

    captured = capsys.readouterr()

    assert bullet in captured_prompt["prompt"]
    assert "Bullet evaluation completed." in captured.out


# =========================================================
# OPTION 3 — GENERATE ROLE SKILLS
# =========================================================


def test_generate_role_skills_rejects_empty_role(
    monkeypatch,
    capsys,
) -> None:
    """An empty target role should display a validation message."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "",
    )

    app.generate_role_skills()

    captured = capsys.readouterr()

    assert "Please enter a target role." in captured.out


def test_generate_role_skills_processes_valid_role(
    monkeypatch,
    capsys,
) -> None:
    """A valid target role should be passed into the generated prompt."""

    role = "Senior Data Engineer at AWS"

    monkeypatch.setattr(
        "builtins.input",
        lambda _: role,
    )

    captured_prompt: dict[str, str] = {}

    def fake_generate_response(prompt: str) -> str:
        captured_prompt["prompt"] = prompt
        return "Python, SQL, AWS, Spark and Airflow"

    monkeypatch.setattr(
        app,
        "generate_response",
        fake_generate_response,
    )

    app.generate_role_skills()

    captured = capsys.readouterr()

    assert role in captured_prompt["prompt"]
    assert "Python, SQL, AWS" in captured.out


# =========================================================
# OPTION 4 — PROFESSIONAL SUMMARY
# =========================================================


def test_professional_summary_requires_all_fields(
    monkeypatch,
    capsys,
) -> None:
    """Missing summary information should be rejected."""

    responses = iter(
        [
            "Senior Data Engineer",
            "",
            "Python, SQL and AWS",
            "Built scalable data pipelines.",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    app.create_professional_summary()

    captured = capsys.readouterr()

    assert (
        "Please provide all required information"
        in captured.out
    )


def test_professional_summary_processes_valid_information(
    monkeypatch,
    capsys,
) -> None:
    """Valid professional information should be placed in the prompt."""

    responses = iter(
        [
            "Senior Data Engineer",
            "5",
            "Python, SQL, AWS and Spark",
            (
                "Built scalable pipelines and improved "
                "data processing performance."
            ),
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    captured_prompt: dict[str, str] = {}

    def fake_generate_response(prompt: str) -> str:
        captured_prompt["prompt"] = prompt
        return "Generated professional summary."

    monkeypatch.setattr(
        app,
        "generate_response",
        fake_generate_response,
    )

    app.create_professional_summary()

    captured = capsys.readouterr()

    prompt = captured_prompt["prompt"]

    assert "Senior Data Engineer" in prompt
    assert "5" in prompt
    assert "Python, SQL, AWS and Spark" in prompt
    assert "Built scalable pipelines" in prompt
    assert "Generated professional summary." in captured.out


# =========================================================
# OPTION 5 — GENERAL CAREER QUESTION
# =========================================================


def test_general_question_rejects_empty_input(
    monkeypatch,
    capsys,
) -> None:
    """An empty career question should be rejected."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "",
    )

    app.ask_general_question()

    captured = capsys.readouterr()

    assert "Please enter a question." in captured.out


def test_general_question_processes_valid_input(
    monkeypatch,
    capsys,
) -> None:
    """A valid career question should be sent for processing."""

    question = (
        "What AWS skills should a senior data engineer highlight?"
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: question,
    )

    captured_prompt: dict[str, str] = {}

    def fake_generate_response(prompt: str) -> str:
        captured_prompt["prompt"] = prompt
        return "Highlight AWS Glue, S3, Redshift and EMR."

    monkeypatch.setattr(
        app,
        "generate_response",
        fake_generate_response,
    )

    app.ask_general_question()

    captured = capsys.readouterr()

    assert question in captured_prompt["prompt"]
    assert "AWS Glue" in captured.out


# =========================================================
# OPTION 6 — PDF RÉSUMÉ ANALYSIS
# =========================================================


def test_analyze_resume_pdf_rejects_empty_path(
    monkeypatch,
    capsys,
) -> None:
    """An empty PDF path should display a validation message."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "",
    )

    app.analyze_resume_pdf()

    captured = capsys.readouterr()

    assert "Please provide a PDF file path." in captured.out


def test_analyze_resume_pdf_processes_valid_pdf(
    monkeypatch,
    capsys,
) -> None:
    """A valid résumé PDF should display metadata and extracted text."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "sample_resume.pdf",
    )

    fake_summary = {
        "file_name": "sample_resume.pdf",
        "page_count": 3,
        "word_count": 846,
        "character_count": 6697,
    }

    fake_resume_text = (
        "SAMPLE RESUME\n"
        "Senior Data Engineer\n"
        "Python SQL AWS Spark Airflow"
    )

    monkeypatch.setattr(
        app,
        "get_pdf_summary",
        lambda _: fake_summary,
    )

    monkeypatch.setattr(
        app,
        "extract_text_from_pdf",
        lambda _: fake_resume_text,
    )

    app.analyze_resume_pdf()

    captured = capsys.readouterr()

    assert "Résumé PDF processed successfully." in captured.out
    assert "sample_resume.pdf" in captured.out
    assert "3" in captured.out
    assert "846" in captured.out
    assert "6697" in captured.out
    assert "Senior Data Engineer" in captured.out


def test_analyze_resume_pdf_handles_processing_error(
    monkeypatch,
    capsys,
) -> None:
    """PDF-processing errors should be shown without crashing."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "missing_resume.pdf",
    )

    def raise_pdf_error(_: str):
        raise PDFProcessingError(
            "PDF file not found: missing_resume.pdf"
        )

    monkeypatch.setattr(
        app,
        "get_pdf_summary",
        raise_pdf_error,
    )

    app.analyze_resume_pdf()

    captured = capsys.readouterr()

    assert "PDF processing error" in captured.out
    assert "PDF file not found" in captured.out


def test_analyze_resume_pdf_truncates_long_preview(
    monkeypatch,
    capsys,
) -> None:
    """Long extracted résumé text should display a truncation message."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "sample_resume.pdf",
    )

    fake_summary = {
        "file_name": "sample_resume.pdf",
        "page_count": 3,
        "word_count": 1000,
        "character_count": 3000,
    }

    long_resume_text = "A" * 2000

    monkeypatch.setattr(
        app,
        "get_pdf_summary",
        lambda _: fake_summary,
    )

    monkeypatch.setattr(
        app,
        "extract_text_from_pdf",
        lambda _: long_resume_text,
    )

    app.analyze_resume_pdf()

    captured = capsys.readouterr()

    assert "Preview truncated" in captured.out


# =========================================================
# MENU / APPLICATION SHELL
# =========================================================


def test_display_menu_contains_pdf_option(
    capsys,
) -> None:
    """The application menu should expose the PDF-analysis feature."""

    app.display_menu()

    captured = capsys.readouterr()

    assert "6. Analyze a résumé PDF" in captured.out
    assert "7. Exit" in captured.out