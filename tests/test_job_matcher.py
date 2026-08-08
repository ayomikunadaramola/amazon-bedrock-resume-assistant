import pytest

from job_matcher import (
    build_match_recommendations,
    calculate_keyword_match_score,
    calculate_skill_match_score,
    compare_keywords,
    compare_skills,
    extract_job_keywords,
    extract_job_skills,
    match_resume_to_job,
    normalize_text,
)


RESUME_TEXT = """
SENIOR DATA ENGINEER

Professional Summary

Senior Data Engineer experienced in building scalable
cloud data platforms.

Technical Skills

Python, SQL, AWS, Apache Spark, Airflow,
PostgreSQL, Docker and Git.

Professional Experience

Built Python and SQL pipelines on AWS.

Orchestrated batch pipelines using Apache Airflow.

Optimized PostgreSQL queries and improved reporting
performance by 65%.

Implemented data quality monitoring and automated
ETL workflows.
"""


JOB_DESCRIPTION = """
We are hiring a Senior Data Engineer.

The successful candidate will build scalable data pipelines
and cloud-based data platforms.

Required skills include Python, SQL, AWS, Apache Spark,
Airflow, Docker, Terraform and Snowflake.

The engineer will be responsible for ETL, data ingestion,
pipeline orchestration, data quality, monitoring,
automation, scalability and warehouse optimization.
"""


def test_normalize_text_returns_lowercase_clean_text():
    result = normalize_text(
        "Python, SQL & AWS!"
    )

    assert "python" in result
    assert "sql" in result
    assert "aws" in result


def test_extract_job_skills_detects_required_skills():
    skills = extract_job_skills(
        JOB_DESCRIPTION
    )

    assert "python" in skills
    assert "sql" in skills
    assert "aws" in skills
    assert "terraform" in skills
    assert "snowflake" in skills


def test_compare_skills_returns_matched_and_missing():
    resume_skills = [
        "python",
        "sql",
        "aws",
    ]

    job_skills = [
        "python",
        "sql",
        "aws",
        "terraform",
    ]

    matched, missing = compare_skills(
        resume_skills,
        job_skills,
    )

    assert "python" in matched
    assert "sql" in matched
    assert "aws" in matched

    assert "terraform" in missing


def test_skill_match_score_calculates_percentage():
    matched = [
        "python",
        "sql",
        "aws",
    ]

    required = [
        "python",
        "sql",
        "aws",
        "terraform",
    ]

    score = calculate_skill_match_score(
        matched,
        required,
    )

    assert score == 75


def test_extract_job_keywords_detects_ats_terms():
    keywords = extract_job_keywords(
        JOB_DESCRIPTION
    )

    assert "pipeline" in keywords or "pipelines" in keywords
    assert "etl" in keywords
    assert "automation" in keywords
    assert "monitoring" in keywords


def test_compare_keywords_detects_missing_terms():
    keywords = [
        "python",
        "sql",
        "terraform",
    ]

    matched, missing = compare_keywords(
        RESUME_TEXT,
        keywords,
    )

    assert "python" in matched
    assert "sql" in matched
    assert "terraform" in missing


def test_keyword_match_score_calculates_percentage():
    score = calculate_keyword_match_score(
        matched_keywords=[
            "python",
            "sql",
        ],
        job_keywords=[
            "python",
            "sql",
            "terraform",
            "snowflake",
        ],
    )

    assert score == 50


def test_build_match_recommendations_flags_missing_skills():
    recommendations = build_match_recommendations(
        skill_score=50,
        keyword_score=60,
        missing_skills=[
            "terraform",
            "snowflake",
        ],
        missing_keywords=[
            "warehouse",
        ],
    )

    combined = " ".join(
        recommendations
    ).lower()

    assert "terraform" in combined
    assert "snowflake" in combined


def test_match_resume_to_job_returns_complete_result():
    result = match_resume_to_job(
        RESUME_TEXT,
        JOB_DESCRIPTION,
    )

    assert 0 <= result.match_score <= 100
    assert 0 <= result.skill_match_score <= 100
    assert 0 <= result.keyword_match_score <= 100

    assert "python" in result.matched_skills
    assert "sql" in result.matched_skills

    assert "terraform" in result.missing_skills
    assert "snowflake" in result.missing_skills

    assert len(result.recommendations) > 0


def test_match_resume_to_job_rejects_empty_resume():
    with pytest.raises(
        ValueError,
        match="Résumé text cannot be empty",
    ):
        match_resume_to_job(
            "",
            JOB_DESCRIPTION,
        )


def test_match_resume_to_job_rejects_empty_job_description():
    with pytest.raises(
        ValueError,
        match="Job description cannot be empty",
    ):
        match_resume_to_job(
            RESUME_TEXT,
            "",
        )