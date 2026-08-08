def build_rewrite_bullet_prompt(bullet: str) -> str:
    """Build the prompt used to rewrite a résumé bullet."""

    return f"""
Rewrite the résumé bullet below to demonstrate stronger ownership,
technical depth and business impact.

Requirements:
- Return one polished bullet only.
- Start with a strong action verb.
- Keep the statement truthful.
- Do not invent percentages or numerical results.
- Keep it between 20 and 35 words.

Original bullet:
{bullet}
""".strip()


def build_evaluate_bullet_prompt(bullet: str) -> str:
    """Build the prompt used to evaluate a résumé bullet."""

    return f"""
Evaluate the résumé bullet below.

Return the answer using exactly these headings:

Score:
Strengths:
Weaknesses:
Improved version:

Score the bullet out of 10.
Do not invent achievements or numerical metrics.

Résumé bullet:
{bullet}
""".strip()


def build_role_skills_prompt(role: str) -> str:
    """Build the prompt used to recommend skills for a target role."""

    return f"""
Identify the 10 most important skills for this target role:

Target role:
{role}

Group the answer under:

Core technical skills:
Cloud and platform skills:
Engineering and operational skills:

Keep the recommendations specific, relevant and ATS-friendly.
""".strip()


def build_professional_summary_prompt(
    role: str,
    experience: str,
    skills: str,
) -> str:
    """Build the prompt used to create a professional summary."""

    return f"""
Write a professional résumé summary using the information below.

Target role: {role}
Years of experience: {experience}
Major skills: {skills}

Requirements:
- Write three concise sentences.
- Use implied first-person language without personal pronouns.
- Make it ATS-friendly.
- Do not invent employers, certifications, projects or metrics.
""".strip()

def build_full_resume_review_prompt(
    resume_text: str,
    analysis_summary: str,
) -> str:
    """
    Build a prompt for a qualitative recruiter-style résumé review.
    """

    return f"""
You are an expert technical recruiter and professional résumé writer
specializing in data engineering, cloud engineering, and AI roles.

Review the résumé below using the deterministic analysis provided.

Do not invent experience, skills, metrics, employers, certifications,
or achievements that are not present in the résumé.

Provide your response using exactly these sections:

STRENGTHS
- Identify the strongest parts of the résumé.

WEAKNESSES
- Identify specific weaknesses that may reduce recruiter or ATS performance.

PRIORITY IMPROVEMENTS
- Give the 3 to 5 most important improvements in priority order.

RECRUITER VERDICT
- Give a concise recruiter-style assessment of the résumé.

DETERMINISTIC ANALYSIS:
{analysis_summary}

RÉSUMÉ:
{resume_text}
""".strip()

def build_job_match_review_prompt(
    resume_text: str,
    job_description: str,
    match_summary: str,
) -> str:
    """
    Build a prompt for recruiter-style résumé-to-job analysis.
    """

    return f"""
You are an expert technical recruiter reviewing a candidate
for a specific job opening.

Compare the résumé with the job description using the supplied
deterministic match results.

Important rules:

1. Do not claim the candidate has a skill unless it appears in the résumé.
2. Do not recommend falsely adding missing skills.
3. Missing skills should only be added if the candidate genuinely has
   relevant experience with them.
4. Focus on ATS alignment, recruiter appeal, demonstrated impact,
   technical relevance, and role fit.

Return exactly these sections:

MATCH STRENGTHS
- Explain where the candidate aligns well.

MATCH GAPS
- Explain the most important gaps.

TAILORING PRIORITIES
- Give the most important résumé changes for this application.

APPLICATION VERDICT
- Rate the fit as Strong, Good, Moderate, or Low and briefly explain why.

MATCH ANALYSIS:
{match_summary}

JOB DESCRIPTION:
{job_description}

RÉSUMÉ:
{resume_text}
""".strip()