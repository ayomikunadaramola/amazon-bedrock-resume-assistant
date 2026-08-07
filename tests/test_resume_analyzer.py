import pytest

from resume_analyzer import (
    analyze_resume,
    calculate_impact_score,
    calculate_section_score,
    calculate_skills_score,
    count_metrics,
    detect_sections,
    extract_technical_skills,
    find_action_verbs,
    find_weak_phrases,
)


SAMPLE_RESUME = """
PROFESSIONAL SUMMARY

Senior Data Engineer experienced in cloud data platforms.

TECHNICAL SKILLS

Python, SQL, AWS, Apache Spark, Airflow, PostgreSQL,
Snowflake and Docker.

PROFESSIONAL EXPERIENCE

Senior Data Engineer

Built scalable Python and SQL data pipelines processing
500,000+ transactions daily.

Optimized PostgreSQL queries and reduced reporting time
by 65%.

Automated ingestion processes and saved 30+ engineering
hours per week.

EDUCATION

Bachelor's Degree

CERTIFICATIONS

AWS Cloud Certification

PROJECTS

Cloud Data Engineering Project
"""


def test_detect_sections_identifies_resume_sections():
    sections = detect_sections(SAMPLE_RESUME)

    assert sections["summary"] is True
    assert sections["experience"] is True
    assert sections["skills"] is True
    assert sections["education"] is True
    assert sections["certifications"] is True
    assert sections["projects"] is True


def test_count_metrics_detects_quantified_achievements():
    metrics = count_metrics(SAMPLE_RESUME)

    assert metrics >= 3


def test_find_action_verbs_detects_strong_verbs():
    verbs = find_action_verbs(SAMPLE_RESUME)

    assert "built" in verbs
    assert "optimized" in verbs
    assert "automated" in verbs


def test_find_weak_phrases_detects_passive_language():
    text = """
    Responsible for data pipelines.
    Worked on reporting systems.
    """

    weak_phrases = find_weak_phrases(text)

    assert "responsible for" in weak_phrases
    assert "worked on" in weak_phrases


def test_extract_technical_skills_detects_skills():
    skills = extract_technical_skills(
        SAMPLE_RESUME
    )

    assert "python" in skills
    assert "sql" in skills
    assert "aws" in skills
    assert "airflow" in skills


def test_calculate_section_score_returns_percentage():
    sections = {
        "summary": True,
        "experience": True,
        "skills": True,
        "education": False,
    }

    score = calculate_section_score(sections)

    assert score == 75


def test_calculate_impact_score_stays_within_range():
    score = calculate_impact_score(
        metric_count=4,
        action_verbs=[
            "built",
            "optimized",
            "automated",
        ],
        weak_phrases=[],
    )

    assert 0 <= score <= 100


def test_calculate_skills_score_returns_high_score_for_many_skills():
    skills = [
        "python",
        "sql",
        "aws",
        "spark",
        "airflow",
        "docker",
        "postgresql",
        "snowflake",
        "git",
        "terraform",
    ]

    score = calculate_skills_score(skills)

    assert score >= 80


def test_analyze_resume_returns_complete_analysis():
    analysis = analyze_resume(
        SAMPLE_RESUME
    )

    assert analysis.word_count > 0

    assert analysis.overall_score > 0

    assert analysis.ats_score > 0

    assert len(
        analysis.technical_skills
    ) > 0


def test_analyze_resume_rejects_empty_text():
    with pytest.raises(
        ValueError,
        match="Résumé text cannot be empty",
    ):
        analyze_resume("")