from mock_service import (
    extract_section,
    extract_value,
    generate_mock_response,
    improve_mock_bullet,
)


def test_extract_section_returns_text_after_heading() -> None:
    """Text after a prompt heading should be extracted correctly."""

    prompt = """
Rewrite the résumé bullet.

Original bullet:
Built data pipelines using Python and SQL.
""".strip()

    result = extract_section(prompt, "Original bullet:")

    assert result == "Built data pipelines using Python and SQL."


def test_extract_section_returns_empty_string_when_heading_is_missing() -> None:
    """A missing heading should return an empty string."""

    result = extract_section("Some unrelated text", "Original bullet:")

    assert result == ""


def test_extract_value_returns_labelled_value() -> None:
    """Single-line labelled values should be extracted correctly."""

    prompt = """
Target role: Senior Data Engineer
Years of experience: 5
Major skills: Python, SQL and AWS
""".strip()

    assert extract_value(prompt, "Target role:") == "Senior Data Engineer"
    assert extract_value(prompt, "Years of experience:") == "5"
    assert extract_value(prompt, "Major skills:") == "Python, SQL and AWS"


def test_improve_mock_bullet_handles_pipeline_content() -> None:
    """Pipeline-related input should produce a stronger pipeline bullet."""

    result = improve_mock_bullet(
        "Built data pipelines using Python and SQL."
    )

    assert "Engineered" in result
    assert "data pipelines" in result
    assert "Python" in result
    assert "SQL" in result


def test_improve_mock_bullet_handles_database_content() -> None:
    """Database input should produce a query-optimisation response."""

    result = improve_mock_bullet(
        "Improved database queries and made reports faster."
    )

    assert "Optimised" in result
    assert "database queries" in result


def test_generate_mock_response_rewrites_bullet() -> None:
    """The mock generator should recognise a rewrite prompt."""

    prompt = """
Rewrite the résumé bullet below.

Original bullet:
Built data pipelines using Python and SQL.
""".strip()

    result = generate_mock_response(prompt)

    assert "Engineered" in result
    assert "Python" in result
    assert "SQL" in result


def test_generate_mock_response_evaluates_bullet() -> None:
    """The mock generator should return the evaluation headings."""

    prompt = """
Evaluate the résumé bullet below.

Résumé bullet:
Maintained ETL pipelines.
""".strip()

    result = generate_mock_response(prompt)

    assert "Score:" in result
    assert "Strengths:" in result
    assert "Weaknesses:" in result
    assert "Improved version:" in result


def test_generate_mock_response_creates_professional_summary() -> None:
    """The mock generator should preserve professional-summary details."""

    prompt = """
Write a professional résumé summary using the information below.

Target role: Senior Data Engineer
Years of experience: 5
Major skills: Python, SQL, AWS and Spark
""".strip()

    result = generate_mock_response(prompt)

    assert "Senior Data Engineer" in result
    assert "5 years of experience" in result
    assert "Python, SQL, AWS and Spark" in result


def test_generate_mock_response_has_default_fallback() -> None:
    """Unknown prompts should receive a safe fallback response."""

    result = generate_mock_response("Explain career development.")

    assert "Mock response generated locally" in result