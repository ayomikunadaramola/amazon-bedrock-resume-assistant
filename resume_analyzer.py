from __future__ import annotations

import re
from dataclasses import dataclass, field


# =========================================================
# CONFIGURATION
# =========================================================


SECTION_PATTERNS = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "career summary",
        "about me",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "career experience",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "technologies",
        "technical competencies",
    ],
    "education": [
        "education",
        "academic background",
        "academic qualifications",
        "qualifications",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "professional certifications",
        "licenses and certifications",
    ],
    "projects": [
        "projects",
        "technical projects",
        "selected projects",
        "portfolio projects",
        "key projects",
    ],
}


STRONG_ACTION_VERBS = {
    "achieved",
    "automated",
    "built",
    "created",
    "delivered",
    "deployed",
    "designed",
    "developed",
    "engineered",
    "implemented",
    "improved",
    "increased",
    "integrated",
    "led",
    "managed",
    "migrated",
    "optimized",
    "orchestrated",
    "reduced",
    "scaled",
    "streamlined",
    "transformed",
}


WEAK_PHRASES = {
    "responsible for",
    "worked on",
    "helped with",
    "assisted with",
    "involved in",
    "participated in",
    "tasked with",
}


TECHNICAL_SKILLS = {
    "python",
    "sql",
    "scala",
    "java",
    "spark",
    "apache spark",
    "airflow",
    "apache airflow",
    "kafka",
    "docker",
    "kubernetes",
    "terraform",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "amazon s3",
    "s3",
    "redshift",
    "aws glue",
    "glue",
    "athena",
    "lambda",
    "emr",
    "bigquery",
    "snowflake",
    "databricks",
    "postgresql",
    "mysql",
    "mongodb",
    "dbt",
    "power bi",
    "looker",
    "github",
    "git",
    "boto3",
    "amazon bedrock",
}


# =========================================================
# DATA MODEL
# =========================================================


@dataclass
class ResumeAnalysis:
    detected_sections: dict[str, bool] = field(default_factory=dict)

    technical_skills: list[str] = field(default_factory=list)

    strong_action_verbs: list[str] = field(default_factory=list)

    weak_phrases: list[str] = field(default_factory=list)

    metric_count: int = 0

    word_count: int = 0

    ats_score: int = 0

    section_score: int = 0

    impact_score: int = 0

    skills_score: int = 0

    overall_score: int = 0


# =========================================================
# SECTION ANALYSIS
# =========================================================


def detect_sections(resume_text: str) -> dict[str, bool]:
    """
    Detect common résumé sections.

    Args:
        resume_text: Extracted résumé text.

    Returns:
        Mapping of section names to detection status.
    """

    normalized_text = resume_text.lower()

    results: dict[str, bool] = {}

    for section, headings in SECTION_PATTERNS.items():
        results[section] = any(
            heading in normalized_text
            for heading in headings
        )

    return results


# =========================================================
# METRIC ANALYSIS
# =========================================================


def count_metrics(resume_text: str) -> int:
    """
    Count measurable achievements such as percentages,
    currency values and numeric quantities.
    """

    patterns = [
        r"\b\d+(?:\.\d+)?%",
        r"\$\s?\d+(?:,\d{3})*(?:\.\d+)?",
        r"₦\s?\d+(?:,\d{3})*(?:\.\d+)?",
        r"\b\d+\+",
        r"\b\d{1,3}(?:,\d{3})+\b",
    ]

    matches: list[str] = []

    for pattern in patterns:
        matches.extend(
            re.findall(
                pattern,
                resume_text,
                flags=re.IGNORECASE,
            )
        )

    return len(matches)


# =========================================================
# ACTION VERB ANALYSIS
# =========================================================


def find_action_verbs(resume_text: str) -> list[str]:
    """
    Find strong résumé action verbs.
    """

    words = set(
        re.findall(
            r"\b[a-zA-Z]+\b",
            resume_text.lower(),
        )
    )

    return sorted(
        word
        for word in STRONG_ACTION_VERBS
        if word in words
    )


def find_weak_phrases(resume_text: str) -> list[str]:
    """
    Detect weak or passive résumé language.
    """

    normalized_text = resume_text.lower()

    return sorted(
        phrase
        for phrase in WEAK_PHRASES
        if phrase in normalized_text
    )


# =========================================================
# SKILLS ANALYSIS
# =========================================================


def extract_technical_skills(
    resume_text: str,
) -> list[str]:
    """
    Detect common technical skills from résumé text.
    """

    normalized_text = resume_text.lower()

    detected = [
        skill
        for skill in TECHNICAL_SKILLS
        if skill in normalized_text
    ]

    return sorted(detected)


# =========================================================
# SCORING
# =========================================================


def calculate_section_score(
    sections: dict[str, bool],
) -> int:
    """
    Score résumé completeness based on expected sections.
    """

    if not sections:
        return 0

    detected = sum(sections.values())

    return round(
        detected / len(sections) * 100
    )


def calculate_impact_score(
    metric_count: int,
    action_verbs: list[str],
    weak_phrases: list[str],
) -> int:
    """
    Score how strongly the résumé communicates impact.
    """

    score = 40

    score += min(metric_count * 6, 30)

    score += min(len(action_verbs) * 3, 25)

    score -= min(len(weak_phrases) * 5, 20)

    return max(
        0,
        min(score, 100),
    )


def calculate_skills_score(
    skills: list[str],
) -> int:
    """
    Estimate technical-skill richness.

    This is not a role-match score. Role matching will
    be added in a later milestone.
    """

    skill_count = len(skills)

    if skill_count >= 15:
        return 100

    if skill_count >= 10:
        return 90

    if skill_count >= 7:
        return 80

    if skill_count >= 5:
        return 70

    if skill_count >= 3:
        return 55

    if skill_count >= 1:
        return 35

    return 0


def calculate_ats_score(
    section_score: int,
    impact_score: int,
    skills_score: int,
    word_count: int,
) -> int:
    """
    Calculate an explainable ATS-readiness score.
    """

    length_score = 100

    if word_count < 250:
        length_score = 50

    elif word_count < 400:
        length_score = 70

    elif word_count > 1500:
        length_score = 65

    elif word_count > 1200:
        length_score = 80

    score = (
        section_score * 0.35
        + impact_score * 0.25
        + skills_score * 0.25
        + length_score * 0.15
    )

    return round(score)


# =========================================================
# COMPLETE ANALYSIS
# =========================================================


def analyze_resume(
    resume_text: str,
) -> ResumeAnalysis:
    """
    Run the complete deterministic résumé analysis.
    """

    if not resume_text.strip():
        raise ValueError(
            "Résumé text cannot be empty."
        )

    sections = detect_sections(resume_text)

    technical_skills = extract_technical_skills(
        resume_text
    )

    action_verbs = find_action_verbs(
        resume_text
    )

    weak_phrases = find_weak_phrases(
        resume_text
    )

    metrics = count_metrics(
        resume_text
    )

    word_count = len(
        resume_text.split()
    )

    section_score = calculate_section_score(
        sections
    )

    impact_score = calculate_impact_score(
        metrics,
        action_verbs,
        weak_phrases,
    )

    skills_score = calculate_skills_score(
        technical_skills
    )

    ats_score = calculate_ats_score(
        section_score,
        impact_score,
        skills_score,
        word_count,
    )

    overall_score = round(
        (
            ats_score
            + section_score
            + impact_score
            + skills_score
        )
        / 4
    )

    return ResumeAnalysis(
        detected_sections=sections,
        technical_skills=technical_skills,
        strong_action_verbs=action_verbs,
        weak_phrases=weak_phrases,
        metric_count=metrics,
        word_count=word_count,
        ats_score=ats_score,
        section_score=section_score,
        impact_score=impact_score,
        skills_score=skills_score,
        overall_score=overall_score,
    )