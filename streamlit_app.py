"""
Streamlit web interface for the Amazon Bedrock AI Résumé Assistant.

This application provides:
- PDF résumé analysis
- ATS scoring
- Technical skills detection
- Impact analysis
- Job-description matching
- Missing skills and keyword analysis
- AI recruiter feedback
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import streamlit as st

from ai_review_service import (
    generate_full_resume_review,
    generate_job_match_review,
)
from config import MOCK_MODE
from job_matcher import match_resume_to_job
from pdf_service import (
    PDFProcessingError,
    extract_text_from_pdf,
    get_pdf_summary,
)
from resume_analyzer import analyze_resume


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Amazon Bedrock AI Résumé Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

BANNER_PATH = (
    BASE_DIR
    / "docs"
    / "images"
    / "banner.png"
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================


def save_uploaded_pdf(uploaded_file) -> str:
    """
    Save an uploaded Streamlit PDF to a temporary file.

    Args:
        uploaded_file:
            File uploaded through Streamlit.

    Returns:
        Path to the temporary PDF file.
    """

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp_file:
        temp_file.write(
            uploaded_file.getbuffer()
        )

        return temp_file.name


def score_label(score: int) -> str:
    """
    Convert a numeric score into a qualitative label.
    """

    if score >= 85:
        return "Strong"

    if score >= 70:
        return "Good"

    if score >= 50:
        return "Moderate"

    return "Needs Improvement"


def render_score(
    title: str,
    score: int,
) -> None:
    """
    Render a résumé score and qualitative interpretation.
    """

    st.metric(
        label=title,
        value=f"{score}/100",
    )

    st.caption(
        score_label(score)
    )


def render_skills(
    skills: list[str],
    empty_message: str = "No technical skills detected.",
) -> None:
    """
    Render skills as compact inline badges.
    """

    if not skills:
        st.info(
            empty_message
        )
        return

    formatted_skills = " ".join(
        f"`{skill}`"
        for skill in skills
    )

    st.markdown(
        formatted_skills
    )


def build_analysis_recommendations(
    analysis,
) -> list[str]:
    """
    Generate deterministic recommendations
    from résumé analysis results.
    """

    recommendations: list[str] = []

    missing_sections = [
        section.title()
        for section, detected
        in analysis.detected_sections.items()
        if not detected
    ]

    if missing_sections:
        recommendations.append(
            "Consider adding these missing sections: "
            + ", ".join(missing_sections)
            + "."
        )

    if analysis.metric_count < 5:
        recommendations.append(
            "Add more measurable achievements using percentages, "
            "time savings, revenue, scale, cost reduction, "
            "or performance improvements."
        )

    if analysis.weak_phrases:
        recommendations.append(
            "Replace passive or weak phrases with stronger "
            "action-oriented résumé language."
        )

    if len(
        analysis.strong_action_verbs
    ) < 5:
        recommendations.append(
            "Use a wider range of strong action verbs "
            "throughout your experience bullets."
        )

    if analysis.skills_score < 70:
        recommendations.append(
            "Strengthen your technical-skills coverage with "
            "tools genuinely relevant to your target role."
        )

    if not recommendations:
        recommendations.append(
            "The résumé has a strong baseline. Focus on tailoring "
            "keywords, achievements, and terminology to each "
            "specific job description."
        )

    return recommendations


def remove_temp_file(
    file_path: str | None,
) -> None:
    """
    Safely remove a temporary PDF.
    """

    if (
        file_path
        and os.path.exists(file_path)
    ):
        os.remove(
            file_path
        )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header(
        "⚙️ Résumé Assistant"
    )

    st.caption(
        "AI-powered résumé intelligence for ATS optimization "
        "and job-description matching."
    )

    st.divider()

    # -----------------------------------------------------
    # APPLICATION MODE
    # -----------------------------------------------------

    st.subheader(
        "Application Mode"
    )

    if MOCK_MODE:

        st.warning(
            "🧪 Mock Mode"
        )

        st.caption(
            "Deterministic résumé analysis is fully active. "
            "Generative AI feedback is currently using the "
            "local fallback service instead of live Amazon Bedrock."
        )

    else:

        st.success(
            "☁️ Amazon Bedrock Mode"
        )

        st.caption(
            "Generative AI recruiter feedback is being "
            "generated through Amazon Bedrock."
        )

    st.divider()

    # -----------------------------------------------------
    # NAVIGATION
    # -----------------------------------------------------

    page = st.radio(
        "Choose a tool",
        [
            "Résumé Analysis",
            "Job Match Analysis",
        ],
    )

    st.divider()

    # -----------------------------------------------------
    # CAPABILITIES
    # -----------------------------------------------------

    st.subheader(
        "Core Capabilities"
    )

    st.markdown(
        """
- ATS résumé scoring
- PDF résumé processing
- Section detection
- Technical skill extraction
- Impact and metrics analysis
- Job-description matching
- Missing skill detection
- ATS keyword analysis
- Recruiter-style AI feedback
"""
    )

    st.divider()

    st.caption(
        "Amazon Bedrock AI Résumé Assistant"
    )


# =========================================================
# HERO / BRANDING
# =========================================================

if BANNER_PATH.exists():

    st.image(
        str(BANNER_PATH),
        use_container_width=True,
    )

else:

    st.warning(
        "Project banner could not be found at "
        "`docs/images/banner.png`."
    )


st.title(
    "Amazon Bedrock AI Résumé Assistant"
)

st.markdown(
    """
Analyze résumé quality, measure ATS readiness, compare your résumé
with target job descriptions, and receive recruiter-style feedback
powered by deterministic analysis and Amazon Bedrock.
"""
)

st.caption(
    "Built with Python · Streamlit · Amazon Bedrock · Boto3 · "
    "pytest · PDF Processing · ATS Scoring · Job Matching"
)

st.divider()


# =========================================================
# PAGE 1 — FULL RÉSUMÉ ANALYSIS
# =========================================================

if page == "Résumé Analysis":

    st.header(
        "Full Résumé Analysis"
    )

    st.write(
        "Upload a PDF résumé to evaluate its ATS readiness, "
        "structure, technical skills, quantified impact, "
        "and recruiter appeal."
    )

    uploaded_resume = st.file_uploader(
        "Upload résumé PDF",
        type=["pdf"],
        key="analysis_resume",
    )

    if uploaded_resume is not None:

        st.success(
            f"Uploaded: {uploaded_resume.name}"
        )

        analyze_button = st.button(
            "Analyze Résumé",
            type="primary",
            use_container_width=True,
        )

        if analyze_button:

            temp_path: str | None = None

            try:

                with st.spinner(
                    "Analyzing résumé..."
                ):

                    temp_path = save_uploaded_pdf(
                        uploaded_resume
                    )

                    document_summary = get_pdf_summary(
                        temp_path
                    )

                    resume_text = extract_text_from_pdf(
                        temp_path
                    )

                    analysis = analyze_resume(
                        resume_text
                    )

                st.success(
                    "Résumé analysis completed successfully."
                )

                # =========================================
                # RESULT TABS
                # =========================================

                (
                    overview_tab,
                    skills_tab,
                    review_tab,
                    text_tab,
                ) = st.tabs(
                    [
                        "Overview",
                        "Skills & Impact",
                        "AI Review",
                        "Résumé Text",
                    ]
                )

                # =========================================
                # OVERVIEW TAB
                # =========================================

                with overview_tab:

                    st.subheader(
                        "Document Information"
                    )

                    doc_col1, doc_col2, doc_col3 = st.columns(
                        3
                    )

                    doc_col1.metric(
                        "Pages",
                        document_summary["page_count"],
                    )

                    doc_col2.metric(
                        "Words",
                        document_summary["word_count"],
                    )

                    doc_col3.metric(
                        "Characters",
                        document_summary["character_count"],
                    )

                    st.divider()

                    # -------------------------------------
                    # SCORES
                    # -------------------------------------

                    st.subheader(
                        "ATS & Résumé Scores"
                    )

                    score_columns = st.columns(
                        5
                    )

                    score_data = [
                        (
                            "Overall",
                            analysis.overall_score,
                        ),
                        (
                            "ATS Readiness",
                            analysis.ats_score,
                        ),
                        (
                            "Sections",
                            analysis.section_score,
                        ),
                        (
                            "Impact",
                            analysis.impact_score,
                        ),
                        (
                            "Skills",
                            analysis.skills_score,
                        ),
                    ]

                    for column, (
                        label,
                        score,
                    ) in zip(
                        score_columns,
                        score_data,
                    ):

                        with column:

                            render_score(
                                label,
                                score,
                            )

                    st.divider()

                    # -------------------------------------
                    # OVERALL INTERPRETATION
                    # -------------------------------------

                    st.subheader(
                        "Overall Résumé Assessment"
                    )

                    if analysis.overall_score >= 85:

                        st.success(
                            "Strong résumé — the document demonstrates "
                            "good ATS readiness, technical relevance, "
                            "and measurable professional impact."
                        )

                    elif analysis.overall_score >= 70:

                        st.info(
                            "Good résumé — targeted improvements could "
                            "increase recruiter and ATS performance."
                        )

                    elif analysis.overall_score >= 50:

                        st.warning(
                            "Moderate résumé — several areas should be "
                            "strengthened before applying."
                        )

                    else:

                        st.error(
                            "The résumé needs significant improvement "
                            "before being used for competitive applications."
                        )

                    # -------------------------------------
                    # SECTIONS
                    # -------------------------------------

                    st.subheader(
                        "Résumé Sections"
                    )

                    section_columns = st.columns(
                        3
                    )

                    for index, (
                        section,
                        detected,
                    ) in enumerate(
                        analysis.detected_sections.items()
                    ):

                        column = section_columns[
                            index % 3
                        ]

                        if detected:

                            column.success(
                                f"✓ {section.title()}"
                            )

                        else:

                            column.error(
                                f"✗ {section.title()}"
                            )

                # =========================================
                # SKILLS & IMPACT TAB
                # =========================================

                with skills_tab:

                    st.subheader(
                        "Technical Skills Detected"
                    )

                    render_skills(
                        analysis.technical_skills
                    )

                    st.divider()

                    # -------------------------------------
                    # IMPACT ANALYSIS
                    # -------------------------------------

                    st.subheader(
                        "Impact Analysis"
                    )

                    impact_col1, impact_col2 = st.columns(
                        2
                    )

                    with impact_col1:

                        st.metric(
                            "Quantified Achievements",
                            analysis.metric_count,
                        )

                    with impact_col2:

                        st.metric(
                            "Impact Score",
                            f"{analysis.impact_score}/100",
                        )

                    st.write(
                        "**Strong action verbs detected**"
                    )

                    if analysis.strong_action_verbs:

                        render_skills(
                            analysis.strong_action_verbs,
                            empty_message=(
                                "No strong action verbs detected."
                            ),
                        )

                    else:

                        st.info(
                            "No strong action verbs detected."
                        )

                    st.write(
                        "**Weak résumé phrases**"
                    )

                    if analysis.weak_phrases:

                        for phrase in analysis.weak_phrases:

                            st.warning(
                                phrase
                            )

                    else:

                        st.success(
                            "No weak résumé phrases detected."
                        )

                    st.divider()

                    # -------------------------------------
                    # RECOMMENDATIONS
                    # -------------------------------------

                    st.subheader(
                        "Recommendations"
                    )

                    recommendations = (
                        build_analysis_recommendations(
                            analysis
                        )
                    )

                    for number, recommendation in enumerate(
                        recommendations,
                        start=1,
                    ):

                        st.markdown(
                            f"**{number}.** {recommendation}"
                        )

                # =========================================
                # AI REVIEW TAB
                # =========================================

                with review_tab:

                    st.subheader(
                        "AI Recruiter Review"
                    )

                    if MOCK_MODE:

                        st.info(
                            "The application is currently running "
                            "in Mock Mode. Live Amazon Bedrock "
                            "feedback is not active."
                        )

                    try:

                        with st.spinner(
                            "Generating recruiter review..."
                        ):

                            ai_review = (
                                generate_full_resume_review(
                                    resume_text,
                                    analysis,
                                )
                            )

                        st.markdown(
                            ai_review
                        )

                    except Exception as error:

                        st.warning(
                            "AI recruiter review is currently "
                            "unavailable."
                        )

                        st.caption(
                            f"Reason: {error}"
                        )

                # =========================================
                # RÉSUMÉ TEXT TAB
                # =========================================

                with text_tab:

                    st.subheader(
                        "Extracted Résumé Text"
                    )

                    st.caption(
                        "This is the text extracted from your PDF "
                        "and used by the analysis engine."
                    )

                    st.text_area(
                        "Extracted résumé content",
                        value=resume_text,
                        height=500,
                        disabled=True,
                    )

            except PDFProcessingError as error:

                st.error(
                    f"PDF processing error: {error}"
                )

            except ValueError as error:

                st.error(
                    f"Résumé analysis error: {error}"
                )

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )

            finally:

                remove_temp_file(
                    temp_path
                )

    else:

        st.info(
            "Upload a PDF résumé above to begin the analysis."
        )


# =========================================================
# PAGE 2 — JOB DESCRIPTION MATCHING
# =========================================================

elif page == "Job Match Analysis":

    st.header(
        "Résumé ↔ Job Description Match"
    )

    st.write(
        "Upload your résumé and paste a target job description "
        "to measure ATS alignment, identify missing skills, "
        "and receive tailoring recommendations."
    )

    uploaded_resume = st.file_uploader(
        "Upload résumé PDF",
        type=["pdf"],
        key="job_match_resume",
    )

    job_description = st.text_area(
        "Paste the job description",
        height=300,
        placeholder=(
            "Paste the complete target job description here..."
        ),
    )

    compare_button = st.button(
        "Compare Résumé with Job",
        type="primary",
        use_container_width=True,
    )

    if compare_button:

        if uploaded_resume is None:

            st.error(
                "Please upload a résumé PDF."
            )

        elif not job_description.strip():

            st.error(
                "Please paste a job description."
            )

        else:

            temp_path: str | None = None

            try:

                with st.spinner(
                    "Comparing résumé with job description..."
                ):

                    temp_path = save_uploaded_pdf(
                        uploaded_resume
                    )

                    resume_text = extract_text_from_pdf(
                        temp_path
                    )

                    result = match_resume_to_job(
                        resume_text,
                        job_description,
                    )

                st.success(
                    "Job match analysis completed."
                )

                # =========================================
                # RESULT TABS
                # =========================================

                (
                    overview_tab,
                    skills_tab,
                    keywords_tab,
                    review_tab,
                ) = st.tabs(
                    [
                        "Overview",
                        "Skills",
                        "ATS Keywords",
                        "AI Review",
                    ]
                )

                # =========================================
                # OVERVIEW TAB
                # =========================================

                with overview_tab:

                    st.subheader(
                        "Match Scores"
                    )

                    match_col1, match_col2, match_col3 = (
                        st.columns(
                            3
                        )
                    )

                    with match_col1:

                        render_score(
                            "Overall Match",
                            result.match_score,
                        )

                    with match_col2:

                        render_score(
                            "Skill Match",
                            result.skill_match_score,
                        )

                    with match_col3:

                        render_score(
                            "Keyword Match",
                            result.keyword_match_score,
                        )

                    st.divider()

                    # -------------------------------------
                    # MATCH STATUS
                    # -------------------------------------

                    st.subheader(
                        "Application Match"
                    )

                    if result.match_score >= 85:

                        st.success(
                            "Strong Match — your résumé is highly "
                            "aligned with this role."
                        )

                    elif result.match_score >= 70:

                        st.info(
                            "Good Match — targeted improvements "
                            "could increase alignment."
                        )

                    elif result.match_score >= 50:

                        st.warning(
                            "Moderate Match — additional tailoring "
                            "is recommended before applying."
                        )

                    else:

                        st.error(
                            "Low Match — significant résumé "
                            "tailoring is recommended."
                        )

                    st.divider()

                    # -------------------------------------
                    # QUICK SUMMARY
                    # -------------------------------------

                    summary_col1, summary_col2 = st.columns(
                        2
                    )

                    summary_col1.metric(
                        "Matched Skills",
                        len(
                            result.matched_skills
                        ),
                    )

                    summary_col2.metric(
                        "Missing Skills",
                        len(
                            result.missing_skills
                        ),
                    )

                # =========================================
                # SKILLS TAB
                # =========================================

                with skills_tab:

                    matched_col, missing_col = st.columns(
                        2
                    )

                    with matched_col:

                        st.subheader(
                            "Matched Skills"
                        )

                        if result.matched_skills:

                            render_skills(
                                result.matched_skills
                            )

                        else:

                            st.info(
                                "No matching technical "
                                "skills detected."
                            )

                    with missing_col:

                        st.subheader(
                            "Missing Job Skills"
                        )

                        if result.missing_skills:

                            render_skills(
                                result.missing_skills,
                                empty_message=(
                                    "No missing skills detected."
                                ),
                            )

                            st.warning(
                                "Only add missing skills to your résumé "
                                "if you genuinely have experience "
                                "using them."
                            )

                        else:

                            st.success(
                                "No major technical skill gaps detected."
                            )

                    st.divider()

                    st.subheader(
                        "Tailoring Recommendations"
                    )

                    if result.recommendations:

                        for number, recommendation in enumerate(
                            result.recommendations,
                            start=1,
                        ):

                            st.markdown(
                                f"**{number}.** {recommendation}"
                            )

                    else:

                        st.success(
                            "No major tailoring recommendations."
                        )

                # =========================================
                # ATS KEYWORDS TAB
                # =========================================

                with keywords_tab:

                    keyword_col1, keyword_col2 = st.columns(
                        2
                    )

                    with keyword_col1:

                        st.subheader(
                            "Matched Keywords"
                        )

                        if result.matched_keywords:

                            render_skills(
                                result.matched_keywords
                            )

                        else:

                            st.info(
                                "No ATS keywords matched."
                            )

                    with keyword_col2:

                        st.subheader(
                            "Missing Keywords"
                        )

                        if result.missing_keywords:

                            render_skills(
                                result.missing_keywords
                            )

                        else:

                            st.success(
                                "No significant ATS keywords "
                                "are missing."
                            )

                    st.divider()

                    st.caption(
                        "Keyword matching is intended to help with "
                        "résumé tailoring. Keywords should be added "
                        "naturally and only when they accurately "
                        "reflect your experience."
                    )

                # =========================================
                # AI REVIEW TAB
                # =========================================

                with review_tab:

                    st.subheader(
                        "AI Application Review"
                    )

                    if MOCK_MODE:

                        st.info(
                            "The application is currently running "
                            "in Mock Mode. Live Amazon Bedrock "
                            "feedback is not active."
                        )

                    try:

                        with st.spinner(
                            "Generating AI application review..."
                        ):

                            ai_review = (
                                generate_job_match_review(
                                    resume_text,
                                    job_description,
                                    result,
                                )
                            )

                        st.markdown(
                            ai_review
                        )

                    except Exception as error:

                        st.warning(
                            "AI application review is currently "
                            "unavailable."
                        )

                        st.caption(
                            f"Reason: {error}"
                        )

            except PDFProcessingError as error:

                st.error(
                    f"PDF processing error: {error}"
                )

            except ValueError as error:

                st.error(
                    f"Matching error: {error}"
                )

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )

            finally:

                remove_temp_file(
                    temp_path
                )


# =========================================================
# HOW IT WORKS
# =========================================================

st.divider()

with st.expander(
    "How this application works"
):

    st.markdown(
        """
### 1. PDF Processing
The uploaded résumé is parsed and converted into text that can
be evaluated by the analysis engine.

### 2. Deterministic Résumé Analysis
The application evaluates résumé sections, technical skills,
action verbs, quantified achievements, and ATS-oriented features.

### 3. Job Description Matching
The résumé can be compared with a target job description to
measure skill alignment and ATS keyword coverage.

### 4. AI Recruiter Review
Amazon Bedrock provides qualitative recruiter-style feedback.
When Bedrock inference is unavailable, the application can run
using its local Mock Mode fallback.

### 5. Actionable Recommendations
The system identifies missing sections, missing skills,
keyword gaps, and areas where résumé impact can be improved.
"""
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Amazon Bedrock AI Résumé Assistant · "
    "Python · Streamlit · Amazon Bedrock · Boto3 · pytest"
)