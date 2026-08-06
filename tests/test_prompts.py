from prompts import (
    build_evaluate_bullet_prompt,
    build_professional_summary_prompt,
    build_rewrite_bullet_prompt,
    build_role_skills_prompt,
)


def test_rewrite_bullet_prompt_contains_original_bullet() -> None:
    """The rewrite prompt should contain the user's original bullet."""

    bullet = "Built data pipelines using Python and SQL."

    result = build_rewrite_bullet_prompt(bullet)

    assert bullet in result
    assert "Original bullet:" in result
    assert "strong action verb" in result


def test_evaluate_bullet_prompt_contains_required_headings() -> None:
    """The evaluation prompt should request predictable headings."""

    bullet = "Maintained ETL pipelines."

    result = build_evaluate_bullet_prompt(bullet)

    assert bullet in result
    assert "Score:" in result
    assert "Strengths:" in result
    assert "Weaknesses:" in result
    assert "Improved version:" in result


def test_role_skills_prompt_contains_target_role() -> None:
    """The skills prompt should include the target role."""

    role = "Senior Data Engineer at AWS"

    result = build_role_skills_prompt(role)

    assert role in result
    assert "Core technical skills:" in result
    assert "Cloud and platform skills:" in result
    assert "Engineering and operational skills:" in result


def test_professional_summary_prompt_contains_user_details() -> None:
    """The summary prompt should preserve all information supplied."""

    result = build_professional_summary_prompt(
        role="Senior Data Engineer",
        experience="5",
        skills="Python, SQL, AWS and Spark",
    )

    assert "Senior Data Engineer" in result
    assert "5" in result
    assert "Python, SQL, AWS and Spark" in result
    assert "three concise sentences" in result