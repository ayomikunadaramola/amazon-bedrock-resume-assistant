import pytest

import ai_review_service

from job_matcher import JobMatchResult
from resume_analyzer import ResumeAnalysis


def build_sample_analysis() -> ResumeAnalysis:
    return ResumeAnalysis(
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
        metric_count=5,
        word_count=750,
        ats_score=85,
        section_score=83,
        impact_score=88,
        skills_score=80,
        overall_score=84,
    )


def build_sample_match_result() -> JobMatchResult:
    return JobMatchResult(
        match_score=76,
        skill_match_score=75,
        keyword_match_score=77,
        matched_skills=[
            "python",
            "sql",
            "aws",
        ],
        missing_skills=[
            "terraform",
            "snowflake",
        ],
        resume_skills=[
            "python",
            "sql",
            "aws",
        ],
        job_skills=[
            "python",
            "sql",
            "aws",
            "terraform",
            "snowflake",
        ],
        matched_keywords=[
            "python",
            "sql",
            "aws",
        ],
        missing_keywords=[
            "terraform",
            "snowflake",
        ],
        recommendations=[],
    )


def test_build_resume_analysis_summary_contains_scores():
    analysis = build_sample_analysis()

    summary = ai_review_service.build_resume_analysis_summary(
        analysis
    )

    assert "84/100" in summary
    assert "85/100" in summary
    assert "Projects" in summary
    assert "python" in summary


def test_build_job_match_summary_contains_match_data():
    result = build_sample_match_result()

    summary = ai_review_service.build_job_match_summary(
        result
    )

    assert "76/100" in summary
    assert "terraform" in summary
    assert "snowflake" in summary


def test_generate_full_resume_review_calls_response_service(
    monkeypatch,
):
    analysis = build_sample_analysis()

    captured_prompt = {}

    def fake_generate_response(prompt: str) -> str:
        captured_prompt["prompt"] = prompt
        return "Recruiter review completed."

    monkeypatch.setattr(
        ai_review_service,
        "generate_response",
        fake_generate_response,
    )

    response = ai_review_service.generate_full_resume_review(
        "Senior Data Engineer with Python and AWS.",
        analysis,
    )

    assert response == "Recruiter review completed."
    assert "Senior Data Engineer" in captured_prompt["prompt"]
    assert "84/100" in captured_prompt["prompt"]


def test_generate_job_match_review_calls_response_service(
    monkeypatch,
):
    result = build_sample_match_result()

    captured_prompt = {}

    def fake_generate_response(prompt: str) -> str:
        captured_prompt["prompt"] = prompt
        return "Job match review completed."

    monkeypatch.setattr(
        ai_review_service,
        "generate_response",
        fake_generate_response,
    )

    response = ai_review_service.generate_job_match_review(
        "Python SQL AWS résumé.",
        "Requires Python SQL AWS Terraform.",
        result,
    )

    assert response == "Job match review completed."
    assert "Terraform" in captured_prompt["prompt"]
    assert "76/100" in captured_prompt["prompt"]


def test_generate_full_resume_review_rejects_empty_resume():
    analysis = build_sample_analysis()

    with pytest.raises(
        ValueError,
        match="Résumé text cannot be empty",
    ):
        ai_review_service.generate_full_resume_review(
            "",
            analysis,
        )


def test_generate_job_match_review_rejects_empty_job_description():
    result = build_sample_match_result()

    with pytest.raises(
        ValueError,
        match="Job description cannot be empty",
    ):
        ai_review_service.generate_job_match_review(
            "Python SQL AWS",
            "",
            result,
        )