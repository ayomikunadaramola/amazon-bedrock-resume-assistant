from __future__ import annotations

from types import SimpleNamespace

import app
from pdf_service import PDFProcessingError


# =========================================================
# OPTION 1 — REWRITE RÉSUMÉ BULLET
# =========================================================


def test_rewrite_bullet_rejects_empty_input(
    monkeypatch,
    capsys,
) -> None:
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


# =========================================================
# OPTION 2 — EVALUATE BULLET
# =========================================================


def test_evaluate_bullet_rejects_empty_input(
    monkeypatch,
    capsys,
) -> None:
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
    bullet = "Optimized PostgreSQL queries."

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
# OPTION 3 — SKILLS
# =========================================================


def test_generate_role_skills_rejects_empty_role(
    monkeypatch,
    capsys,
) -> None:
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
    responses = iter(
        [
            "Senior Data Engineer",
            "",
            "Python, SQL and AWS",
            "Built scalable pipelines.",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    app.create_professional_summary()

    captured = capsys.readouterr()

    assert "Please provide all required information" in captured.out


def test_professional_summary_processes_valid_information(
    monkeypatch,
    capsys,
) -> None:
    responses = iter(
        [
            "Senior Data Engineer",
            "5",
            "Python, SQL, AWS and Spark",
            "Built scalable pipelines and improved performance.",
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
    assert "Python, SQL, AWS and Spark" in prompt
    assert "Built scalable pipelines" in prompt
    assert "Generated professional summary." in captured.out


# =========================================================
# OPTION 5 — GENERAL QUESTION
# =========================================================


def test_general_question_rejects_empty_input(
    monkeypatch,
    capsys,
) -> None:
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
    question = "What AWS skills should a data engineer highlight?"

    monkeypatch.setattr(
        "builtins.input",
        lambda _: question,
    )

    captured_prompt: dict[str, str] = {}

    def fake_generate_response(prompt: str) -> str:
        captured_prompt["prompt"] = prompt
        return "Highlight Glue, S3 and Redshift."

    monkeypatch.setattr(
        app,
        "generate_response",
        fake_generate_response,
    )

    app.ask_general_question()

    captured = capsys.readouterr()

    assert question in captured_prompt["prompt"]
    assert "Glue" in captured.out


# =========================================================
# OPTION 6 — FULL PDF RÉSUMÉ ANALYSIS
# =========================================================


def test_analyze_resume_pdf_rejects_empty_path(
    monkeypatch,
    capsys,
) -> None:
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
        "PROFESSIONAL SUMMARY\n"
        "Senior Data Engineer\n"
        "Python SQL AWS Spark Airflow"
    )

    fake_analysis = SimpleNamespace(
        overall_score=93,
        ats_score=93,
        section_score=83,
        impact_score=95,
        skills_score=100,
        detected_sections={
            "summary": True,
            "experience": True,
            "skills": True,
            "education": True,
            "certifications": True,
            "projects": False,
        },
        technical_skills=[
            "python",
            "sql",
            "aws",
        ],
        strong_action_verbs=[
            "built",
            "optimized",
        ],
        weak_phrases=[],
        metric_count=12,
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

    monkeypatch.setattr(
        app,
        "analyze_resume",
        lambda _: fake_analysis,
    )

    app.analyze_resume_pdf()

    captured = capsys.readouterr()

    assert "Résumé PDF processed successfully." in captured.out
    assert "sample_resume.pdf" in captured.out

    assert "Overall Score" in captured.out
    assert "93/100" in captured.out

    assert "ATS Readiness" in captured.out
    assert "Section Completeness" in captured.out
    assert "Impact & Metrics" in captured.out
    assert "Technical Skills" in captured.out

    assert "Projects" in captured.out
    assert "python" in captured.out
    assert "sql" in captured.out
    assert "aws" in captured.out

    assert "Quantified achievements detected: 12" in captured.out

    assert "Analysis completed successfully." in captured.out


def test_analyze_resume_pdf_handles_processing_error(
    monkeypatch,
    capsys,
) -> None:
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

    fake_analysis = SimpleNamespace(
        overall_score=80,
        ats_score=80,
        section_score=80,
        impact_score=80,
        skills_score=80,
        detected_sections={
            "summary": True,
            "experience": True,
            "skills": True,
            "education": True,
            "certifications": False,
            "projects": False,
        },
        technical_skills=[
            "python",
            "sql",
        ],
        strong_action_verbs=[
            "built",
        ],
        weak_phrases=[],
        metric_count=2,
    )

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

    monkeypatch.setattr(
        app,
        "analyze_resume",
        lambda _: fake_analysis,
    )

    app.analyze_resume_pdf()

    captured = capsys.readouterr()

    assert "Preview truncated" in captured.out


def test_analyze_resume_pdf_displays_missing_section_recommendation(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "sample_resume.pdf",
    )

    fake_summary = {
        "file_name": "sample_resume.pdf",
        "page_count": 2,
        "word_count": 600,
        "character_count": 4500,
    }

    fake_analysis = SimpleNamespace(
        overall_score=75,
        ats_score=75,
        section_score=67,
        impact_score=75,
        skills_score=80,
        detected_sections={
            "summary": True,
            "experience": True,
            "skills": True,
            "education": True,
            "certifications": False,
            "projects": False,
        },
        technical_skills=[
            "python",
            "sql",
            "aws",
        ],
        strong_action_verbs=[
            "built",
            "optimized",
            "implemented",
        ],
        weak_phrases=[],
        metric_count=3,
    )

    monkeypatch.setattr(
        app,
        "get_pdf_summary",
        lambda _: fake_summary,
    )

    monkeypatch.setattr(
        app,
        "extract_text_from_pdf",
        lambda _: "Sample résumé text",
    )

    monkeypatch.setattr(
        app,
        "analyze_resume",
        lambda _: fake_analysis,
    )

    app.analyze_resume_pdf()

    captured = capsys.readouterr()

    assert "Certifications" in captured.out
    assert "Projects" in captured.out
    assert "Consider adding these missing sections" in captured.out


# =========================================================
# MENU
# =========================================================

def test_display_menu_contains_pdf_option(
    capsys,
) -> None:
    app.display_menu()

    captured = capsys.readouterr()

    assert "6. Analyze a résumé PDF" in captured.out
    assert "7. Match résumé to a job description" in captured.out
    assert "8. Exit" in captured.out