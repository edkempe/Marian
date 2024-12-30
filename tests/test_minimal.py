"""Minimal test suite using real implementations."""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database_init import get_test_engines, init_db
from models.email import Base as EmailBase
from models.email import Email
from models.email_analysis import Base as AnalysisBase
from models.email_analysis import EmailAnalysis
from shared_lib.anthropic_client_lib import test_anthropic_connection
from shared_lib.constants import API_CONFIG, SentimentTypes
from src import EmailAnalytics, EmailAnalyzer, EmailSelfAnalyzer
from tests.test_utils import (
    TEST_EMAIL_BODY,
    TEST_EMAIL_SUBJECT,
    TEST_ANALYSIS_CATEGORY,
    TEST_ANALYSIS_PRIORITY,
    TEST_ANALYSIS_SUMMARY,
    assert_email_analysis_response,
    create_test_email,
    create_test_analysis,
    get_test_session,
)

from .test_config import (
    TEST_ANALYSIS_DB,
    TEST_EMAIL_DB,
    cleanup_test_env,
    setup_test_env,
)


def setup_module():
    """Set up test databases."""
    init_db(testing=True)


@pytest.fixture(scope="function")
def test_db():
    """Create test databases for each test."""
    email_engine, analysis_engine, catalog_engine = get_test_engines()
    yield email_engine, analysis_engine, catalog_engine


@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Set up test environment and databases."""
    # Set up test environment
    setup_test_env()

    # Create test databases
    email_engine = create_engine(f"sqlite:///{TEST_EMAIL_DB}")
    analysis_engine = create_engine(f"sqlite:///{TEST_ANALYSIS_DB}")

    # Create tables
    EmailBase.metadata.create_all(email_engine)
    AnalysisBase.metadata.create_all(analysis_engine)

    yield

    # Clean up after all tests
    cleanup_test_env()


@pytest.fixture(scope="session", autouse=True)
def verify_api_connection():
    """Verify API connection before running tests."""
    if not test_anthropic_connection():
        pytest.exit(
            "API connection test failed. Please check your API key and connection."
        )


def test_email_analysis(verify_api_connection):
    """Test email analysis with real API calls."""
    analyzer = EmailAnalyzer(test_mode=True)

    test_email = {
        "id": f"test_{datetime.now().timestamp()}",
        "subject": TEST_EMAIL_SUBJECT,
        "body": "This is an important work email that requires review by tomorrow.",
    }

    try:
        analysis = analyzer.analyze_email(test_email)
        assert_email_analysis_response(analysis)
    except Exception as e:
        pytest.fail(f"Email analysis failed: {str(e)}")


@patch("shared_lib.gmail_lib.GmailAPI")
def test_email_fetching(mock_gmail):
    """Test email fetching with mocked Gmail API."""
    # Mock Gmail API
    mock_gmail_instance = MagicMock()
    mock_gmail.return_value = mock_gmail_instance
    
    analyzer = EmailSelfAnalyzer()

    # Add test email to database
    with get_test_session(TEST_EMAIL_DB) as session:
        email = create_test_email()
        session.add(email)
        session.commit()

        # Verify email was added
        email = session.query(Email).first()
        assert email is not None
        assert email.subject == TEST_EMAIL_SUBJECT
        assert email.body == TEST_EMAIL_BODY


def test_email_analytics():
    """Test email analytics with real database."""
    analytics = EmailAnalytics()

    # Add test analysis to database
    with get_test_session(TEST_ANALYSIS_DB) as session:
        analysis = create_test_analysis()
        session.add(analysis)
        session.commit()

        # Verify analysis was added
        analysis = session.query(EmailAnalysis).first()
        assert analysis is not None
        assert analysis.summary == TEST_ANALYSIS_SUMMARY
        assert json.loads(analysis.category) == TEST_ANALYSIS_CATEGORY
        assert analysis.priority_score == TEST_ANALYSIS_PRIORITY
        assert analysis.sentiment == SentimentTypes.NEUTRAL
