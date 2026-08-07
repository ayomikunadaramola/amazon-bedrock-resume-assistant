"""
Resume Assistant
"""

from __future__ import annotations

import os

from resume_analyzer import analyze_resume

from config import MOCK_MODE

from pdf_service import (
    PDFProcessingError,
    extract_text_from_pdf,
    get_pdf_summary,
)

from prompts import (
    build_evaluate_bullet_prompt,
    build_professional_summary_prompt,
    build_rewrite_bullet_prompt,
    build_role_skills_prompt,
)

from resume_service import generate_response


# =========================================================
# DISPLAY HELPERS
# =========================================================


def print_header() -> None:
    """Display the application header."""

    mode = "Mock Mode" if MOCK_MODE else "Amazon Bedrock Mode"

    print("\n" + "=" * 57)
    print(" AMAZON BEDROCK AI RÉSUMÉ ASSISTANT")
    print(f" Current mode: {mode}")
    print("=" * 57)


def display_menu() -> None:
    """Display the main application menu."""

    print_header()

    print(
        """
1. Rewrite a résumé bullet
2. Evaluate a résumé bullet
3. Generate skills for a target role
4. Create a professional summary
5. Ask a general career question
6. Analyze a résumé PDF
7. Exit
"""
    )


# =========================================================
# INPUT HELPERS
# =========================================================


def get_non_empty_input(prompt_text: str) -> str:
    """
    Request user input and remove surrounding whitespace.

    Args:
        prompt_text: Message displayed to the user.

    Returns:
        Cleaned user input.
    """

    return input(prompt_text).strip()


# =========================================================
# OPTION 1
# REWRITE RÉSUMÉ BULLET
# =========================================================


def rewrite_bullet() -> None:
    """Rewrite a résumé bullet point using AI or mock mode."""

    bullet = get_non_empty_input(
        "\nEnter the résumé bullet:\n> "
    )

    if not bullet:
        print("\nPlease enter a résumé bullet.")
        return

    prompt = build_rewrite_bullet_prompt(bullet)

    try:
        response = generate_response(prompt)
    except Exception as error:
        print(f"\nUnable to generate response: {error}")
        return

    print("\nAssistant:\n")
    print(response)


# =========================================================
# OPTION 2
# EVALUATE RÉSUMÉ BULLET
# =========================================================


def evaluate_bullet() -> None:
    """Evaluate the quality of a résumé bullet point."""

    bullet = get_non_empty_input(
        "\nEnter the résumé bullet you want evaluated:\n> "
    )

    if not bullet:
        print("\nPlease enter a résumé bullet.")
        return

    prompt = build_evaluate_bullet_prompt(bullet)

    try:
        response = generate_response(prompt)
    except Exception as error:
        print(f"\nUnable to generate response: {error}")
        return

    print("\nAssistant:\n")
    print(response)


# =========================================================
# OPTION 3
# GENERATE SKILLS
# =========================================================


def generate_role_skills() -> None:
    """Generate important skills for a target role."""

    role = get_non_empty_input(
        "\nEnter the target job role:\n> "
    )

    if not role:
        print("\nPlease enter a target role.")
        return

    prompt = build_role_skills_prompt(role)

    try:
        response = generate_response(prompt)
    except Exception as error:
        print(f"\nUnable to generate response: {error}")
        return

    print("\nAssistant:\n")
    print(response)


# =========================================================
# OPTION 4
# PROFESSIONAL SUMMARY
# =========================================================


def create_professional_summary() -> None:
    """Generate a professional résumé summary."""

    print(
        "\nProvide a few details so the assistant can create "
        "your professional summary."
    )

    role = get_non_empty_input(
        "\nCurrent or target role:\n> "
    )

    years_experience = get_non_empty_input(
        "\nYears of experience:\n> "
    )

    skills = get_non_empty_input(
        "\nKey skills, separated by commas:\n> "
    )

    achievements = get_non_empty_input(
        "\nOne or two major achievements:\n> "
    )

    if not all(
        [
            role,
            years_experience,
            skills,
            achievements,
        ]
    ):
        print(
            "\nPlease provide all required information "
            "to generate a professional summary."
        )
        return
    
    prompt = build_professional_summary_prompt(
    role,
    years_experience,
    skills,
)

    prompt += (
    "\n\nMajor achievements:\n"
    f"{achievements}"
)
    
    try:
        response = generate_response(prompt)
    except Exception as error:
        print(f"\nUnable to generate response: {error}")
        return

    print("\nAssistant:\n")
    print(response)


# =========================================================
# OPTION 5
# GENERAL CAREER QUESTION
# =========================================================


def ask_general_question() -> None:
    """Answer a general résumé or career-related question."""

    question = get_non_empty_input(
        "\nEnter your career or résumé question:\n> "
    )

    if not question:
        print("\nPlease enter a question.")
        return

    prompt = f"""
You are an expert résumé writer, technical recruiter,
and career advisor.

Answer the following career question clearly,
professionally, and practically.

Question:
{question}
""".strip()

    try:
        response = generate_response(prompt)
    except Exception as error:
        print(f"\nUnable to generate response: {error}")
        return

    print("\nAssistant:\n")
    print(response)


# =========================================================
# OPTION 6
# ANALYZE RÉSUMÉ PDF
# =========================================================


def analyze_resume_pdf() -> None:
    """
    Validate a résumé PDF, extract its text,
    analyze résumé quality, and display a structured report.
    """

    print("\n" + "=" * 57)
    print(" FULL RÉSUMÉ ANALYSIS")
    print("=" * 57)

    file_path = get_non_empty_input(
        "\nEnter the path to the résumé PDF:\n> "
    )

    if not file_path:
        print("\nPlease provide a PDF file path.")
        return

    try:
        summary = get_pdf_summary(file_path)
        resume_text = extract_text_from_pdf(file_path)
        analysis = analyze_resume(resume_text)

    except PDFProcessingError as error:
        print(f"\nPDF processing error: {error}")
        return

    except ValueError as error:
        print(f"\nRésumé analysis error: {error}")
        return

    except Exception as error:
        print(f"\nUnexpected error: {error}")
        return

    print("\nRésumé PDF processed successfully.")

    print("\n" + "-" * 57)
    print(" DOCUMENT INFORMATION")
    print("-" * 57)

    print(f"File name   : {summary['file_name']}")
    print(f"Pages       : {summary['page_count']}")
    print(f"Words       : {summary['word_count']}")
    print(f"Characters  : {summary['character_count']}")

    print("\n" + "-" * 57)
    print(" ATS / RÉSUMÉ SCORES")
    print("-" * 57)

    print(f"Overall Score       : {analysis.overall_score}/100")
    print(f"ATS Readiness       : {analysis.ats_score}/100")
    print(f"Section Completeness: {analysis.section_score}/100")
    print(f"Impact & Metrics    : {analysis.impact_score}/100")
    print(f"Technical Skills    : {analysis.skills_score}/100")

    print("\n" + "-" * 57)
    print(" SECTIONS DETECTED")
    print("-" * 57)

    for section, detected in analysis.detected_sections.items():
        symbol = "✓" if detected else "✗"
        print(f"{symbol} {section.title()}")

    print("\n" + "-" * 57)
    print(" TECHNICAL SKILLS DETECTED")
    print("-" * 57)

    if analysis.technical_skills:
        for skill in analysis.technical_skills:
            print(f"• {skill}")
    else:
        print("No known technical skills detected.")

    print("\n" + "-" * 57)
    print(" IMPACT ANALYSIS")
    print("-" * 57)

    print(
        f"Quantified achievements detected: "
        f"{analysis.metric_count}"
    )

    if analysis.strong_action_verbs:
        print(
            "\nStrong action verbs:\n"
            + ", ".join(analysis.strong_action_verbs)
        )
    else:
        print("\nNo strong action verbs detected.")

    if analysis.weak_phrases:
        print(
            "\nWeak phrases detected:\n"
            + ", ".join(analysis.weak_phrases)
        )
    else:
        print("\nNo weak résumé phrases detected.")

    print("\n" + "-" * 57)
    print(" PRELIMINARY RECOMMENDATIONS")
    print("-" * 57)

    recommendations: list[str] = []

    missing_sections = [
        section.title()
        for section, detected
        in analysis.detected_sections.items()
        if not detected
    ]

    if missing_sections:
        recommendations.append(
            "Consider adding these missing sections: "
            + ", ".join(missing_sections)
            + "."
        )

    if analysis.metric_count < 5:
        recommendations.append(
            "Add more measurable achievements using percentages, "
            "time savings, revenue, scale, cost reduction, "
            "or performance improvements."
        )

    if analysis.weak_phrases:
        recommendations.append(
            "Replace passive phrases with stronger action-oriented language."
        )

    if len(analysis.strong_action_verbs) < 5:
        recommendations.append(
            "Use a wider range of strong action verbs in experience bullets."
        )

    if analysis.skills_score < 70:
        recommendations.append(
            "Strengthen the technical skills section with relevant tools "
            "and technologies for the target role."
        )

    if not recommendations:
        recommendations.append(
            "The résumé has a strong baseline. Focus next on tailoring "
            "keywords and achievements to each target job description."
        )

    for number, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        print(f"{number}. {recommendation}")

    print("\n" + "-" * 57)
    print(" EXTRACTED RÉSUMÉ PREVIEW")
    print("-" * 57 + "\n")

    preview_length = 1200
    print(resume_text[:preview_length])

    if len(resume_text) > preview_length:
        print("\n[Preview truncated]")

    print("\n" + "=" * 57)
    print(" Analysis completed successfully.")
    print("=" * 57)

# =========================================================
# MAIN APPLICATION LOOP
# =========================================================


def main() -> None:
    """Run the Amazon Bedrock AI Résumé Assistant."""

    while True:

        display_menu()

        choice = input("Select an option: ").strip()

        if choice == "1":
            rewrite_bullet()

        elif choice == "2":
            evaluate_bullet()

        elif choice == "3":
            generate_role_skills()

        elif choice == "4":
            create_professional_summary()

        elif choice == "5":
            ask_general_question()

        elif choice == "6":
            analyze_resume_pdf()

        elif choice == "7":
            print("\nThank you for using the Amazon Bedrock AI Résumé Assistant.")
            print("Goodbye.\n")
            break

        else:
            print(
                "\nInvalid selection. "
                "Please choose an option between 1 and 7."
            )


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================


if __name__ == "__main__":
    main()