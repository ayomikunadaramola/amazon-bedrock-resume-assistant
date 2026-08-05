from __future__ import annotations

import sys
from typing import Callable, Final

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
)


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

AWS_REGION: Final[str] = "us-east-1"
MODEL_ID: Final[str] = "amazon.nova-lite-v1:0"

# Keep this as True while your AWS Bedrock inference quota is zero.
# Change it to False after AWS enables your Bedrock inference quota.
MOCK_MODE: Final[bool] = True


SYSTEM_PROMPT: Final[str] = """
You are an expert résumé writer and technical recruiter specialising in
data engineering, cloud engineering and artificial intelligence roles.

Follow these rules:

1. Answer only the task requested.
2. Do not provide tutorials unless the user asks for one.
3. Use strong action verbs.
4. Preserve all facts supplied by the user.
5. Never invent metrics, employers, projects, tools or achievements.
6. When metrics are missing, improve the wording without creating numbers.
7. Use concise, professional and ATS-friendly language.
8. Use British English spelling where appropriate.
""".strip()


# =========================================================
# MOCK MODE
# =========================================================

def generate_mock_response(prompt: str) -> str:
    """
    Return a temporary local response without calling Amazon Bedrock.

    This allows the application interface to be developed and tested while
    the AWS account has no available Bedrock inference quota.
    """

    prompt_lower = prompt.lower()

    if "rewrite the résumé bullet" in prompt_lower:
        original_bullet = extract_section(prompt, "Original bullet:")

        if original_bullet:
            return (
                "Engineered Python- and SQL-based data pipelines to automate "
                "data ingestion, transformation and delivery, improving the "
                "reliability and accessibility of analytics-ready datasets."
            )

        return (
            "Engineered scalable data pipelines using Python and SQL to "
            "automate data processing and improve the delivery of "
            "analytics-ready datasets."
        )

    if "evaluate the résumé bullet" in prompt_lower:
        bullet = extract_section(prompt, "Résumé bullet:")

        return (
            "Score:\n"
            "6/10\n\n"
            "Strengths:\n"
            "- Communicates relevant data engineering responsibility.\n"
            "- Includes a recognisable technical area.\n\n"
            "Weaknesses:\n"
            "- Uses passive or generic wording.\n"
            "- Does not explain ownership, technical depth or business value.\n"
            "- Does not identify the tools used or the result achieved.\n\n"
            "Improved version:\n"
            f"{create_mock_bullet_improvement(bullet)}"
        )

    if "identify the 10 most important skills" in prompt_lower:
        role = extract_section(prompt, "target role:")

        return (
            f"Recommended skills for {role or 'the target role'}:\n\n"
            "Core technical skills:\n"
            "1. Python\n"
            "2. Advanced SQL\n"
            "3. Data modelling\n"
            "4. ETL and ELT pipeline development\n"
            "5. Apache Spark\n\n"
            "Cloud and platform skills:\n"
            "6. Amazon S3\n"
            "7. AWS Glue\n"
            "8. Amazon Redshift\n\n"
            "Engineering and operational skills:\n"
            "9. Apache Airflow and workflow orchestration\n"
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
        "data quality, automation and analytics enablement. Experienced "
        "in translating business requirements into maintainable, "
        "production-ready data solutions."
    )

    if "cover letter" in prompt_lower:
        return (
            "Dear Hiring Manager,\n\n"
            "I am writing to express my interest in the advertised role. "
            "My background in data engineering, cloud platforms and scalable "
            "pipeline development has equipped me to design reliable data "
            "solutions that support informed business decisions.\n\n"
            "I would welcome the opportunity to contribute my technical "
            "experience, problem-solving ability and commitment to data "
            "quality to your team.\n\n"
            "Kind regards,\n"
            "Ayomikun Adaramola"
        )

    return (
        "Mock response generated locally because Amazon Bedrock inference "
        "is currently unavailable for this AWS account. The application "
        "interface is working correctly and can be switched to live Bedrock "
        "mode when AWS enables the required quota."
    )


def extract_section(prompt: str, heading: str) -> str:
    """Extract the text appearing after a heading in a generated prompt."""

    if heading not in prompt:
        return ""

    return prompt.split(heading, maxsplit=1)[1].strip()


def extract_value(prompt: str, label: str) -> str:
    """Extract a single-line value from a labelled prompt field."""

    for line in prompt.splitlines():
        if line.strip().startswith(label):
            return line.split(label, maxsplit=1)[1].strip()

    return ""


def create_mock_bullet_improvement(bullet: str) -> str:
    """Create a safe mock improvement without inventing numerical metrics."""

    if not bullet:
        return (
            "Optimised data workflows and reporting processes to improve "
            "query performance and increase access to reliable insights."
        )

    bullet_lower = bullet.lower()

    if "etl" in bullet_lower:
        return (
            "Maintained and enhanced ETL pipelines and database workflows to "
            "support reliable data processing and consistent downstream reporting."
        )

    if "query" in bullet_lower or "database" in bullet_lower:
        return (
            "Optimised database queries and reporting workflows to improve "
            "performance and accelerate access to business insights."
        )

    if "pipeline" in bullet_lower:
        return (
            "Engineered and maintained data pipelines to automate ingestion, "
            "transformation and delivery of analytics-ready datasets."
        )

    return (
        "Strengthened the original achievement using clearer ownership, "
        "technical detail and business-focused language."
    )


# =========================================================
# AMAZON BEDROCK CONNECTION
# =========================================================

def create_bedrock_client():
    """Create and return an Amazon Bedrock Runtime client."""

    return boto3.client(
        service_name="bedrock-runtime",
        region_name=AWS_REGION,
    )


def invoke_model(prompt: str) -> str:
    """
    Generate a response using mock mode or Amazon Bedrock.

    When MOCK_MODE is True, no AWS API call is made.
    When MOCK_MODE is False, Amazon Nova Lite is invoked through Bedrock.
    """

    if MOCK_MODE:
        return generate_mock_response(prompt)

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

    return "".join(
        block["text"]
        for block in content_blocks
        if "text" in block
    ).strip()


# =========================================================
# RÉSUMÉ ASSISTANT FEATURES
# =========================================================

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
- Keep the statement truthful.
- Do not invent percentages or numerical results.
- Keep it between 20 and 35 words.

Original bullet:
{bullet}
""".strip()

    return invoke_model(prompt)


def evaluate_bullet() -> str:
    """Evaluate one résumé bullet and suggest an improved version."""

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

Score the bullet out of 10.
Do not invent achievements or numerical metrics.

Résumé bullet:
{bullet}
""".strip()

    return invoke_model(prompt)


def generate_role_skills() -> str:
    """Generate important ATS-friendly skills for a target role."""

    role = input("\nEnter the target role:\n> ").strip()

    if not role:
        return "No target role was provided."

    prompt = f"""
Identify the 10 most important skills for this target role:

target role:
{role}

Group the answer under:

Core technical skills:
Cloud and platform skills:
Engineering and operational skills:

Keep the recommendations specific, relevant and ATS-friendly.
""".strip()

    return invoke_model(prompt)


def create_professional_summary() -> str:
    """Generate a professional résumé summary from user information."""

    role = input("\nEnter your current or target role:\n> ").strip()
    experience = input("Enter your years of experience:\n> ").strip()
    skills = input(
        "Enter your major skills, separated by commas:\n> "
    ).strip()

    if not role or not experience or not skills:
        return (
            "Role, years of experience and major skills are all required."
        )

    prompt = f"""
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

    return invoke_model(prompt)


def ask_general_question() -> str:
    """Answer a general résumé or career-related question."""

    question = input("\nEnter your question:\n> ").strip()

    if not question:
        return "No question was provided."

    return invoke_model(question)


# =========================================================
# USER INTERFACE
# =========================================================

def display_menu() -> None:
    """Display the available application options."""

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
    """Display a clear message for Amazon Bedrock API errors."""

    error_details = error.response.get("Error", {})
    error_code = error_details.get("Code", "UnknownError")
    error_message = error_details.get("Message", str(error))

    if (
        error_code == "ThrottlingException"
        and "tokens per day" in error_message.lower()
    ):
        print(
            "\nAmazon Bedrock inference is currently unavailable because "
            "this AWS account has no remaining or assigned daily token "
            "allocation.\n\n"
            "This is an AWS quota issue, not an application error.\n"
            "Set MOCK_MODE to True to continue testing locally.\n",
            file=sys.stderr,
        )
        return

    if error_code == "AccessDeniedException":
        print(
            "\nAmazon Bedrock denied the request. Check the IAM user's "
            "Bedrock permissions and model access.\n",
            file=sys.stderr,
        )
        return

    if error_code == "ValidationException":
        print(
            f"\nAmazon Bedrock rejected the request configuration:\n"
            f"{error_message}\n",
            file=sys.stderr,
        )
        return

    print(
        f"\nAWS error [{error_code}]: {error_message}\n",
        file=sys.stderr,
    )


def run_action(action: Callable[[], str]) -> None:
    """Run one selected application function safely."""

    try:
        result = action()
        print(f"\nAssistant:\n{result}\n")

    except NoCredentialsError:
        print(
            "\nAWS credentials were not found.\n"
            "Run 'aws configure' and try again.\n",
            file=sys.stderr,
        )

    except ClientError as error:
        handle_aws_error(error)

    except BotoCoreError as error:
        print(
            f"\nAWS SDK error:\n{error}\n",
            file=sys.stderr,
        )

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by the user.")


def main() -> None:
    """Run the Amazon Bedrock AI Résumé Assistant."""

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
            print(
                "\nInvalid selection. Enter a number between 1 and 6."
            )
            continue

        run_action(action)


if __name__ == "__main__":
    main()