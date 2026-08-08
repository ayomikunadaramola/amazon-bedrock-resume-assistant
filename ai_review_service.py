from __future__ import annotations

from job_matcher import JobMatchResult
from prompts import (
    build_full_resume_review_prompt,
    build_job_match_review_prompt,
)
from resume_analyzer import ResumeAnalysis
from resume_service import generate_response


def build_resume_analysis_summary(
    analysis: ResumeAnalysis,
) -> str:
    """
    Convert deterministic résumé analysis into
    a concise text summary for the AI reviewer.
    """

    detected_sections = [
        section.title()
        for section, detected in analysis.detected_sections.items()
        if detected
    ]

    missing_sections = [
        section.title()
        for section, detected in analysis.detected_sections.items()
        if not detected
    ]

    skills = (
        ", ".join(analysis.technical_skills)
        if analysis.technical_skills
        else "None detected"
    )

    strong_verbs = (
        ", ".join(analysis.strong_action_verbs)
        if analysis.strong_action_verbs
        else "None detected"
    )

    weak_phrases = (
        ", ".join(analysis.weak_phrases)
        if analysis.weak_phrases
        else "None detected"
    )

    return f"""
Overall Score: {analysis.overall_score}/100
ATS Readiness: {analysis.ats_score}/100
Section Completeness: {analysis.section_score}/100
Impact Score: {analysis.impact_score}/100
Technical Skills Score: {analysis.skills_score}/100
Word Count: {analysis.word_count}
Quantified Achievements: {analysis.metric_count}

Detected Sections:
{", ".join(detected_sections) if detected_sections else "None"}

Missing Sections:
{", ".join(missing_sections) if missing_sections else "None"}

Technical Skills:
{skills}

Strong Action Verbs:
{strong_verbs}

Weak Phrases:
{weak_phrases}
""".strip()


def build_job_match_summary(
    result: JobMatchResult,
) -> str:
    """
    Convert deterministic job-match results
    into a concise summary for the AI reviewer.
    """

    matched_skills = (
        ", ".join(result.matched_skills)
        if result.matched_skills
        else "None"
    )

    missing_skills = (
        ", ".join(result.missing_skills)
        if result.missing_skills
        else "None"
    )

    matched_keywords = (
        ", ".join(result.matched_keywords)
        if result.matched_keywords
        else "None"
    )

    missing_keywords = (
        ", ".join(result.missing_keywords)
        if result.missing_keywords
        else "None"
    )

    return f"""
Overall Match Score: {result.match_score}/100
Skill Match Score: {result.skill_match_score}/100
Keyword Match Score: {result.keyword_match_score}/100

Matched Skills:
{matched_skills}

Missing Skills:
{missing_skills}

Matched Keywords:
{matched_keywords}

Missing Keywords:
{missing_keywords}
""".strip()


def generate_full_resume_review(
    resume_text: str,
    analysis: ResumeAnalysis,
) -> str:
    """
    Generate recruiter-style qualitative feedback
    for a full résumé.
    """

    if not resume_text.strip():
        raise ValueError(
            "Résumé text cannot be empty."
        )

    analysis_summary = build_resume_analysis_summary(
        analysis
    )

    prompt = build_full_resume_review_prompt(
        resume_text,
        analysis_summary,
    )

    return generate_response(
        prompt
    )


def generate_job_match_review(
    resume_text: str,
    job_description: str,
    result: JobMatchResult,
) -> str:
    """
    Generate recruiter-style qualitative feedback
    for résumé-to-job alignment.
    """

    if not resume_text.strip():
        raise ValueError(
            "Résumé text cannot be empty."
        )

    if not job_description.strip():
        raise ValueError(
            "Job description cannot be empty."
        )

    match_summary = build_job_match_summary(
        result
    )

    prompt = build_job_match_review_prompt(
        resume_text,
        job_description,
        match_summary,
    )

    return generate_response(
        prompt
    )