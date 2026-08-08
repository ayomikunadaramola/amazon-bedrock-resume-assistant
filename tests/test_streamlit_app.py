"""Smoke tests for the Streamlit web application."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STREAMLIT_APP = (
    PROJECT_ROOT
    / "streamlit_app.py"
)


def test_streamlit_app_starts_without_errors() -> None:
    """
    The Streamlit application should start
    without raising an exception.
    """

    app = AppTest.from_file(
        str(STREAMLIT_APP),
        default_timeout=15,
    )

    app.run()

    assert not app.exception


def test_streamlit_app_displays_main_title() -> None:
    """
    The application should display its main title.
    """

    app = AppTest.from_file(
        str(STREAMLIT_APP),
        default_timeout=15,
    )

    app.run()

    titles = [
        title.value
        for title in app.title
    ]

    assert (
        "Amazon Bedrock AI Résumé Assistant"
        in titles
    )


def test_streamlit_sidebar_contains_navigation() -> None:
    """
    The sidebar should expose the two main tools.
    """

    app = AppTest.from_file(
        str(STREAMLIT_APP),
        default_timeout=15,
    )

    app.run()

    assert len(
        app.radio
    ) >= 1

    options = list(
        app.radio[0].options
    )

    assert "Résumé Analysis" in options
    assert "Job Match Analysis" in options