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