def extract_section(prompt: str, heading: str) -> str:
    """Extract all text appearing after a prompt heading."""

    if heading not in prompt:
        return ""

    return prompt.split(heading, maxsplit=1)[1].strip()


def extract_value(prompt: str, label: str) -> str:
    """Extract a single-line value from a labelled prompt field."""

    for line in prompt.splitlines():
        stripped_line = line.strip()

        if stripped_line.startswith(label):
            return stripped_line.split(label, maxsplit=1)[1].strip()

    return ""


def improve_mock_bullet(bullet: str) -> str:
    """Create a truthful mock improvement without inventing metrics."""

    bullet_lower = bullet.lower()

    if "pipeline" in bullet_lower:
        return (
            "Engineered Python- and SQL-based data pipelines to automate "
            "data ingestion, transformation and delivery, improving the "
            "reliability and accessibility of analytics-ready datasets."
        )

    if "query" in bullet_lower or "database" in bullet_lower:
        return (
            "Optimised database queries and reporting workflows to improve "
            "performance and accelerate access to business insights."
        )

    if "etl" in bullet_lower:
        return (
            "Maintained and enhanced ETL pipelines and database workflows "
            "to support reliable data processing and consistent reporting."
        )

    return (
        "Strengthened the achievement using clearer ownership, technical "
        "detail and business-focused language."
    )


def generate_mock_response(prompt: str) -> str:
    """Generate a local response without calling Amazon Bedrock."""

    prompt_lower = prompt.lower()

    if "rewrite the résumé bullet" in prompt_lower:
        bullet = extract_section(prompt, "Original bullet:")
        return improve_mock_bullet(bullet)

    if "evaluate the résumé bullet" in prompt_lower:
        bullet = extract_section(prompt, "Résumé bullet:")

        return (
            "Score:\n"
            "6/10\n\n"
            "Strengths:\n"
            "- Communicates a relevant engineering responsibility.\n"
            "- Contains useful technical context.\n\n"
            "Weaknesses:\n"
            "- Does not clearly demonstrate ownership.\n"
            "- Does not explain the value or outcome of the work.\n"
            "- Uses wording that could be more specific.\n\n"
            "Improved version:\n"
            f"{improve_mock_bullet(bullet)}"
        )

    if "identify the 10 most important skills" in prompt_lower:
        role = extract_section(prompt, "Target role:")

        return (
            f"Recommended skills for {role or 'the target role'}:\n\n"
            "Core technical skills:\n"
            "1. Python\n"
            "2. Advanced SQL\n"
            "3. Data modelling\n"
            "4. ETL and ELT development\n"
            "5. Apache Spark\n\n"
            "Cloud and platform skills:\n"
            "6. Amazon S3\n"
            "7. AWS Glue\n"
            "8. Amazon Redshift\n\n"
            "Engineering and operational skills:\n"
            "9. Apache Airflow\n"
            "10. Data quality, monitoring and governance"
        )

    if "write a professional résumé summary" in prompt_lower:
        role = extract_value(prompt, "Target role:")
        experience = extract_value(prompt, "Years of experience:")
        skills = extract_value(prompt, "Major skills:")

        safe_role = role or "Data Engineer"
        safe_experience = experience or "several"
        safe_skills = skills or "Python, SQL and cloud technologies"

        return (
            f"{safe_role} with {safe_experience} years of experience "
            "designing reliable data pipelines and scalable cloud data "
            f"platforms. Skilled in {safe_skills}, with a strong focus on "
            "automation, data quality and analytics enablement. Experienced "
            "in translating business requirements into maintainable, "
            "production-ready data solutions."
        )

    return (
        "Mock response generated locally because live Amazon Bedrock "
        "inference is currently unavailable."
    )