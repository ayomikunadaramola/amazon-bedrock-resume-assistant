import app


def test_rewrite_bullet_returns_validation_message_for_empty_input(
    monkeypatch,
) -> None:
    """An empty résumé bullet should be rejected."""

    monkeypatch.setattr("builtins.input", lambda _: "")

    result = app.rewrite_bullet()

    assert result == "No résumé bullet was provided."


def test_rewrite_bullet_sends_prompt_to_response_service(
    monkeypatch,
) -> None:
    """A valid bullet should be passed through the response service."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "Built data pipelines using Python and SQL.",
    )

    monkeypatch.setattr(
        app,
        "generate_response",
        lambda prompt: f"Processed: {prompt}",
    )

    result = app.rewrite_bullet()

    assert result.startswith("Processed:")
    assert "Built data pipelines using Python and SQL." in result


def test_generate_role_skills_rejects_empty_role(
    monkeypatch,
) -> None:
    """An empty target role should be rejected."""

    monkeypatch.setattr("builtins.input", lambda _: "")

    result = app.generate_role_skills()

    assert result == "No target role was provided."


def test_generate_role_skills_processes_valid_role(
    monkeypatch,
) -> None:
    """A valid role should be included in the generated prompt."""

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "Senior Data Engineer at AWS",
    )

    monkeypatch.setattr(
        app,
        "generate_response",
        lambda prompt: prompt,
    )

    result = app.generate_role_skills()

    assert "Senior Data Engineer at AWS" in result


def test_professional_summary_requires_all_fields(
    monkeypatch,
) -> None:
    """The summary feature should reject missing information."""

    responses = iter(
        [
            "Senior Data Engineer",
            "",
            "Python, SQL and AWS",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    result = app.create_professional_summary()

    assert (
        result
        == "Role, years of experience and major skills are all required."
    )


def test_professional_summary_processes_valid_information(
    monkeypatch,
) -> None:
    """Valid summary information should be placed in the prompt."""

    responses = iter(
        [
            "Senior Data Engineer",
            "5",
            "Python, SQL, AWS and Spark",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    monkeypatch.setattr(
        app,
        "generate_response",
        lambda prompt: prompt,
    )

    result = app.create_professional_summary()

    assert "Senior Data Engineer" in result
    assert "5" in result
    assert "Python, SQL, AWS and Spark" in result


def test_general_question_rejects_empty_input(
    monkeypatch,
) -> None:
    """An empty career question should be rejected."""

    monkeypatch.setattr("builtins.input", lambda _: "")

    result = app.ask_general_question()

    assert result == "No question was provided."