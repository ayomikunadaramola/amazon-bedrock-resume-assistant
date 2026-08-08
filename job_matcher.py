from __future__ import annotations

import re
from dataclasses import dataclass, field

from resume_analyzer import (
    TECHNICAL_SKILLS,
    extract_technical_skills,
)


# =========================================================
# DATA MODEL
# =========================================================


@dataclass
class JobMatchResult:
    """Structured result of résumé-to-job-description matching."""

    match_score: int = 0

    skill_match_score: int = 0

    keyword_match_score: int = 0

    matched_skills: list[str] = field(default_factory=list)

    missing_skills: list[str] = field(default_factory=list)

    resume_skills: list[str] = field(default_factory=list)

    job_skills: list[str] = field(default_factory=list)

    matched_keywords: list[str] = field(default_factory=list)

    missing_keywords: list[str] = field(default_factory=list)

    recommendations: list[str] = field(default_factory=list)


# =========================================================
# TEXT NORMALIZATION
# =========================================================


def normalize_text(text: str) -> str:
    """
    Normalize text for keyword comparison.

    Converts text to lowercase and removes unnecessary
    punctuation while keeping technology-related characters.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9+#.\-/\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# =========================================================
# JOB DESCRIPTION SKILLS
# =========================================================


def extract_job_skills(
    job_description: str,
) -> list[str]:
    """
    Extract known technical skills from a job description.
    """

    if not job_description.strip():
        return []

    return extract_technical_skills(
        job_description
    )


# =========================================================
# SKILL COMPARISON
# =========================================================


def compare_skills(
    resume_skills: list[str],
    job_skills: list[str],
) -> tuple[list[str], list[str]]:
    """
    Compare résumé skills against required job skills.

    Returns:
        matched skills
        missing skills
    """

    resume_set = {
        skill.lower()
        for skill in resume_skills
    }

    job_set = {
        skill.lower()
        for skill in job_skills
    }

    matched = sorted(
        resume_set.intersection(job_set)
    )

    missing = sorted(
        job_set.difference(resume_set)
    )

    return matched, missing


# =========================================================
# SKILL MATCH SCORE
# =========================================================


def calculate_skill_match_score(
    matched_skills: list[str],
    job_skills: list[str],
) -> int:
    """
    Calculate percentage of required technical skills
    found in the résumé.
    """

    if not job_skills:
        return 100

    score = (
        len(matched_skills)
        / len(job_skills)
    ) * 100

    return round(score)


# =========================================================
# KEYWORD EXTRACTION
# =========================================================


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "their",
    "this",
    "to",
    "we",
    "will",
    "with",
    "you",
    "your",
}


IMPORTANT_JOB_TERMS = {
    "analytics",
    "architecture",
    "automation",
    "batch",
    "cloud",
    "compliance",
    "data",
    "database",
    "deployment",
    "distributed",
    "engineering",
    "etl",
    "governance",
    "ingestion",
    "integration",
    "modeling",
    "monitoring",
    "optimization",
    "orchestration",
    "pipeline",
    "pipelines",
    "quality",
    "reliability",
    "scalability",
    "security",
    "streaming",
    "transformation",
    "warehouse",
}


def extract_job_keywords(
    job_description: str,
) -> list[str]:
    """
    Extract useful ATS-style keywords from a job description.

    The function intentionally focuses on meaningful
    professional and data-engineering terminology.
    """

    normalized = normalize_text(
        job_description
    )

    words = re.findall(
        r"\b[a-z][a-z0-9+#.\-/]*\b",
        normalized,
    )

    keywords = {
        word
        for word in words
        if (
            word not in STOP_WORDS
            and (
                word in IMPORTANT_JOB_TERMS
                or word in TECHNICAL_SKILLS
            )
        )
    }

    return sorted(keywords)


# =========================================================
# KEYWORD COMPARISON
# =========================================================


def compare_keywords(
    resume_text: str,
    job_keywords: list[str],
) -> tuple[list[str], list[str]]:
    """
    Compare important JD keywords against résumé content.
    """

    normalized_resume = normalize_text(
        resume_text
    )

    matched: list[str] = []
    missing: list[str] = []

    for keyword in job_keywords:
        pattern = (
            r"(?<!\w)"
            + re.escape(keyword)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            normalized_resume,
            flags=re.IGNORECASE,
        ):
            matched.append(keyword)
        else:
            missing.append(keyword)

    return sorted(matched), sorted(missing)


# =========================================================
# KEYWORD MATCH SCORE
# =========================================================


def calculate_keyword_match_score(
    matched_keywords: list[str],
    job_keywords: list[str],
) -> int:
    """
    Calculate ATS-style keyword coverage percentage.
    """

    if not job_keywords:
        return 100

    score = (
        len(matched_keywords)
        / len(job_keywords)
    ) * 100

    return round(score)


# =========================================================
# RECOMMENDATIONS
# =========================================================


def build_match_recommendations(
    skill_score: int,
    keyword_score: int,
    missing_skills: list[str],
    missing_keywords: list[str],
) -> list[str]:
    """
    Generate deterministic résumé-tailoring recommendations.
    """

    recommendations: list[str] = []

    if missing_skills:
        recommendations.append(
            "Consider highlighting relevant experience with these "
            "job-specific skills where genuinely applicable: "
            + ", ".join(missing_skills)
            + "."
        )

    if keyword_score < 70 and missing_keywords:
        recommendations.append(
            "Improve ATS keyword alignment by naturally incorporating "
            "relevant terminology such as: "
            + ", ".join(missing_keywords[:8])
            + "."
        )

    if skill_score < 60:
        recommendations.append(
            "The résumé currently has a relatively low technical-skill "
            "match for this role. Prioritize demonstrated experience "
            "that directly maps to the job requirements."
        )

    if skill_score >= 80 and keyword_score >= 80:
        recommendations.append(
            "The résumé has strong alignment with this job description. "
            "Focus on strengthening quantified achievements and using "
            "the employer's terminology naturally."
        )

    if not recommendations:
        recommendations.append(
            "The résumé shows reasonable alignment. Tailor experience "
            "bullets to demonstrate how the matched skills produced "
            "measurable business or technical outcomes."
        )

    return recommendations


# =========================================================
# COMPLETE JOB MATCH
# =========================================================


def match_resume_to_job(
    resume_text: str,
    job_description: str,
) -> JobMatchResult:
    """
    Compare an extracted résumé against a target job description.
    """

    if not resume_text.strip():
        raise ValueError(
            "Résumé text cannot be empty."
        )

    if not job_description.strip():
        raise ValueError(
            "Job description cannot be empty."
        )

    resume_skills = extract_technical_skills(
        resume_text
    )

    job_skills = extract_job_skills(
        job_description
    )

    matched_skills, missing_skills = compare_skills(
        resume_skills,
        job_skills,
    )

    skill_match_score = calculate_skill_match_score(
        matched_skills,
        job_skills,
    )

    job_keywords = extract_job_keywords(
        job_description
    )

    matched_keywords, missing_keywords = compare_keywords(
        resume_text,
        job_keywords,
    )

    keyword_match_score = calculate_keyword_match_score(
        matched_keywords,
        job_keywords,
    )

    # Technical skill alignment receives slightly greater weight
    # than general ATS keyword coverage.
    match_score = round(
        (
            skill_match_score * 0.60
            + keyword_match_score * 0.40
        )
    )

    recommendations = build_match_recommendations(
        skill_match_score,
        keyword_match_score,
        missing_skills,
        missing_keywords,
    )

    return JobMatchResult(
        match_score=match_score,
        skill_match_score=skill_match_score,
        keyword_match_score=keyword_match_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        resume_skills=resume_skills,
        job_skills=job_skills,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        recommendations=recommendations,
    )