from __future__ import annotations

import sys
from typing import Callable

from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
)

from config import MOCK_MODE
from prompts import (
    build_evaluate_bullet_prompt,
    build_professional_summary_prompt,
    build_rewrite_bullet_prompt,
    build_role_skills_prompt,
)
from resume_service import generate_response


def rewrite_bullet() -> str:
    """Collect and rewrite one résumé bullet."""

    bullet = input("\nEnter the résumé bullet:\n> ").strip()

    if not bullet:
        return "No résumé bullet was provided."

    prompt = build_rewrite_bullet_prompt(bullet)
    return generate_response(prompt)


def evaluate_bullet() -> str:
    """Evaluate one résumé bullet."""

    bullet = input("\nEnter the résumé bullet to evaluate:\n> ").strip()

    if not bullet:
        return "No résumé bullet was provided."

    prompt = build_evaluate_bullet_prompt(bullet)
    return generate_response(prompt)


def generate_role_skills() -> str:
    """Generate skills for a target role."""

    role = input("\nEnter the target role:\n> ").strip()

    if not role:
        return "No target role was provided."

    prompt = build_role_skills_prompt(role)
    return generate_response(prompt)


def create_professional_summary() -> str:
    """Create a professional résumé summary."""

    role = input("\nEnter your current or target role:\n> ").strip()
    experience = input("Enter your years of experience:\n> ").strip()
    skills = input(
        "Enter your major skills, separated by commas:\n> "
    ).strip()

    if not role or not experience or not skills:
        return (
            "Role, years of experience and major skills are all required."
        )

    prompt = build_professional_summary_prompt(
        role=role,
        experience=experience,
        skills=skills,
    )

    return generate_response(prompt)


def ask_general_question() -> str:
    """Answer a general résumé or career question."""

    question = input("\nEnter your question:\n> ").strip()

    if not question:
        return "No question was provided."

    return generate_response(question)


def display_menu() -> None:
    """Display the application menu."""

    mode_name = "Mock Mode" if MOCK_MODE else "Live Amazon Bedrock Mode"

    print("\n" + "=" * 55)
    print(" AMAZON BEDROCK AI RÉSUMÉ ASSISTANT")
    print(f" Current mode: {mode_name}")
    print("=" * 55)

    print(
        """
1. Rewrite a résumé bullet
2. Evaluate a résumé bullet
3. Generate skills for a target role
4. Create a professional summary
5. Ask a general career question
6. Exit
"""
    )


def handle_aws_error(error: ClientError) -> None:
    """Display user-friendly Amazon Bedrock errors."""

    error_details = error.response.get("Error", {})
    error_code = error_details.get("Code", "UnknownError")
    error_message = error_details.get("Message", str(error))

    if error_code == "ThrottlingException":
        print(
            "\nAmazon Bedrock is currently unavailable because the "
            "account has reached or has not received its inference quota.\n"
            "Change MOCK_MODE to True in config.py to continue locally.\n",
            file=sys.stderr,
        )
        return

    if error_code == "AccessDeniedException":
        print(
            "\nAmazon Bedrock denied the request. Check the IAM permissions "
            "and model access configuration.\n",
            file=sys.stderr,
        )
        return

    print(
        f"\nAWS error [{error_code}]: {error_message}\n",
        file=sys.stderr,
    )


def run_action(action: Callable[[], str]) -> None:
    """Execute one application feature safely."""

    try:
        result = action()
        print(f"\nAssistant:\n{result}\n")

    except NoCredentialsError:
        print(
            "\nAWS credentials were not found. Run 'aws configure'.\n",
            file=sys.stderr,
        )

    except ClientError as error:
        handle_aws_error(error)

    except BotoCoreError as error:
        print(
            f"\nAWS SDK error: {error}\n",
            file=sys.stderr,
        )

    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")


def main() -> None:
    """Run the résumé assistant."""

    actions: dict[str, Callable[[], str]] = {
        "1": rewrite_bullet,
        "2": evaluate_bullet,
        "3": generate_role_skills,
        "4": create_professional_summary,
        "5": ask_general_question,
    }

    while True:
        display_menu()
        choice = input("Select an option: ").strip()

        if choice == "6":
            print("\nGoodbye.")
            break

        action = actions.get(choice)

        if action is None:
            print("\nInvalid selection. Enter a number between 1 and 6.")
            continue

        run_action(action)


if __name__ == "__main__":
    main()