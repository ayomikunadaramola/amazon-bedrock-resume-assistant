import resume_service


def test_generate_response_uses_mock_service_when_mock_mode_is_enabled(
    monkeypatch,
) -> None:
    """Mock mode should call the local mock-response generator."""

    monkeypatch.setattr(resume_service, "MOCK_MODE", True)

    def fake_mock_response(prompt: str) -> str:
        return f"Mock result: {prompt}"

    monkeypatch.setattr(
        resume_service,
        "generate_mock_response",
        fake_mock_response,
    )

    result = resume_service.generate_response("Test prompt")

    assert result == "Mock result: Test prompt"


def test_generate_response_uses_bedrock_when_mock_mode_is_disabled(
    monkeypatch,
) -> None:
    """Live mode should route the prompt to the Bedrock client."""

    monkeypatch.setattr(resume_service, "MOCK_MODE", False)

    def fake_bedrock_response(prompt: str) -> str:
        return f"Bedrock result: {prompt}"

    monkeypatch.setattr(
        resume_service,
        "invoke_bedrock",
        fake_bedrock_response,
    )

    result = resume_service.generate_response("Test prompt")

    assert result == "Bedrock result: Test prompt"