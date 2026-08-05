from __future__ import annotations

import sys
from typing import Final

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
)


AWS_REGION: Final[str] = "us-east-1"
MODEL_ID = "us.amazon.nova-lite-v1:0"

SYSTEM_PROMPT: Final[str] = """
You are an expert résumé writer and technical recruiter specialising in
data engineering, cloud engineering and artificial intelligence roles.

Follow these rules:

1. Answer only the task requested.
2. Do not provide tutorials unless the user asks for one.
3. Use strong action verbs.
4. Preserve facts supplied by the user.
5. Never invent metrics, tools, employers or achievements.
6. When metrics are missing, improve the wording without fabricating numbers.
7. Write in concise, professional, ATS-friendly language.
""".strip()


def create_bedrock_client():
    """Create an Amazon Bedrock Runtime client."""

    return boto3.client(
        service_name="bedrock-runtime",
        region_name=AWS_REGION,
    )


def invoke_model(prompt: str) -> str:
    """Send a prompt to Amazon Nova Lite and return its response."""

    client = create_bedrock_client()

    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "maxTokens": 120,
            "temperature": 0.2,
            "topP": 0.9,
        },
    )

    content_blocks = response["output"]["message"]["content"]

    return "".join(
        block["text"]
        for block in content_blocks
        if "text" in block
    ).strip()


def rewrite_bullet() -> str:
    """Collect and rewrite one résumé bullet."""

    bullet = input("\nEnter the résumé bullet:\n> ").strip()

    if not bullet:
        return "No résumé bullet was provided."

    prompt = f"""
Rewrite the résumé bullet below to demonstrate stronger ownership,
technical depth and business impact.

Requirements:
- Return one polished bullet only.
- Start with a strong action verb.
- Keep it truthful.
- Do not invent a percentage or numerical result.
- Keep it between 20 and 35 words.

Original bullet:
{bullet}
""".strip()

    return invoke_model(prompt)


def evaluate_bullet() -> str:
    """Evaluate one résumé bullet and suggest improvements."""

    bullet = input("\nEnter the résumé bullet to evaluate:\n> ").strip()

    if not bullet:
        return "No résumé bullet was provided."

    prompt = f"""
Evaluate the résumé bullet below.

Return the answer using exactly these headings:

Score:
Strengths:
Weaknesses:
Improved version:

Score the bullet out of 10. Do not invent achievements or metrics.

Résumé bullet:
{bullet}
""".strip()

    return invoke_model(prompt)


def generate_role_skills() -> str:
    """Generate important skills for a target role."""

    role = input("\nEnter the target role:\n> ").strip()

    if not role:
        return "No target role was provided."

    prompt = f"""
Identify the 10 most important skills for this target role:

{role}

Group them under:
- Core technical skills
- Cloud and platform skills
- Engineering and operational skills

Keep the recommendations specific and ATS-friendly.
""".strip()

    return invoke_model(prompt)


def create_professional_summary() -> str:
    """Generate a professional résumé summary from user information."""

    role = input("\nEnter your current or target role:\n> ").strip()
    experience = input("Enter your years of experience:\n> ").strip()
    skills = input("Enter your major skills, separated by commas:\n> ").strip()

    if not role or not experience or not skills:
        return "Role, experience and skills are all required."

    prompt = f"""
Write a professional résumé summary using the information below.

Target role: {role}
Years of experience: {experience}
Major skills: {skills}

Requirements:
- Write 3 concise sentences.
- Use first-person implied language without pronouns.
- Make it ATS-friendly.
- Do not invent employers, certifications, metrics or projects.
""".strip()

    return invoke_model(prompt)


def answer_general_question() -> str:
    """Answer a general résumé or career question."""

    question = input("\nEnter your question:\n> ").strip()

    if not question:
        return "No question was provided."

    return invoke_model(question)


def display_menu() -> None:
    """Display available application actions."""

    print(
        """
Choose an action:

1. Rewrite a résumé bullet
2. Evaluate a résumé bullet
3. Generate skills for a target role
4. Create a professional summary
5. Ask a general career question
6. Exit
"""
    )


def main() -> None:
    """Run the command-line résumé assistant."""

    actions = {
        "1": rewrite_bullet,
        "2": evaluate_bullet,
        "3": generate_role_skills,
        "4": create_professional_summary,
        "5": answer_general_question,
    }

    print("\nAmazon Bedrock Résumé Assistant")
    print("Powered by Amazon Nova Lite")

    while True:
        display_menu()
        choice = input("Select an option: ").strip()

        if choice == "6":
            print("\nGoodbye.")
            return

        action = actions.get(choice)

        if action is None:
            print("\nInvalid selection. Choose a number from 1 to 6.")
            continue

        try:
            result = action()
            print(f"\nAssistant:\n{result}\n")

        except NoCredentialsError:
            print(
                "\nAWS credentials were not found. Run 'aws configure'.\n",
                file=sys.stderr,
            )

        except ClientError as error:
            error_details = error.response.get("Error", {})
            error_code = error_details.get("Code", "UnknownError")
            error_message = error_details.get("Message", str(error))

            print(
                f"\nAWS error [{error_code}]: {error_message}\n",
                file=sys.stderr,
            )

        except BotoCoreError as error:
            print(
                f"\nAWS SDK error: {error}\n",
                file=sys.stderr,
            )

        except KeyboardInterrupt:
            print("\n\nApplication stopped.")
            return


if __name__ == "__main__":
    main()