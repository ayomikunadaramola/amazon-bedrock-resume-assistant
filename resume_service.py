from bedrock_client import invoke_bedrock
from config import MOCK_MODE
from mock_service import generate_mock_response


def generate_response(prompt: str) -> str:
    """Generate a response using mock mode or Amazon Bedrock."""

    if MOCK_MODE:
        return generate_mock_response(prompt)

    return invoke_bedrock(prompt)