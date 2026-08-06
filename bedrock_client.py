from typing import Any

import boto3

from config import AWS_REGION, MODEL_ID, SYSTEM_PROMPT


def create_bedrock_client() -> Any:
    """Create an Amazon Bedrock Runtime client."""

    return boto3.client(
        service_name="bedrock-runtime",
        region_name=AWS_REGION,
    )


def invoke_bedrock(prompt: str) -> str:
    """Send a request to Amazon Nova Lite through Bedrock."""

    client = create_bedrock_client()

    response = client.converse(
        modelId=MODEL_ID,
        system=[
            {
                "text": SYSTEM_PROMPT,
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt,
                    }
                ],
            }
        ],
        inferenceConfig={
            "maxTokens": 300,
            "temperature": 0.2,
            "topP": 0.9,
        },
    )

    content_blocks = response["output"]["message"]["content"]

    generated_text = "".join(
        block["text"]
        for block in content_blocks
        if "text" in block
    )

    return generated_text.strip()