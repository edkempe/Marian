"""Tests for the email analyzer module."""

import json
from datetime import datetime, timedelta
from typing import Any, Dict

import pytest

from models.email import Email
from models.email_analysis import EmailAnalysis, EmailAnalysisResponse
from shared_lib.constants import API_CONFIG
from shared_lib.database_session_util import get_analysis_session, get_email_session
from src.app_email_analyzer import EmailAnalyzer


@pytest.fixture(scope="session")
def email_analyzer():
    """Create EmailAnalyzer instance for testing."""
    analyzer = EmailAnalyzer(metrics_port=0)  # Disable metrics for tests
    return analyzer


@pytest.fixture
def valid_email_data():
    """Valid email data for testing."""
    return {
        "id": f"test_{datetime.now().timestamp()}",
        "threadId": "thread1",
        "subject": "Test Email",
        "body": "This is an important work email that requires review by tomorrow.",
        "received_date": datetime.now().isoformat(),
        "labels": '["INBOX"]',
        "from_": "test@example.com",
        "to": "recipient@example.com",
    }


def test_email_analysis_response_validation():
    """Test EmailAnalysisResponse validation with real API response."""
    analyzer = EmailAnalyzer(metrics_port=0)

    test_email = {
        "id": f"test_{datetime.now().timestamp()}",
        "threadId": "thread1",
        "subject": "Test Email",
        "body": "This is an important work email that requires review by tomorrow.",
        "received_date": datetime.now().isoformat(),
        "labels": '["INBOX"]',
        "from_": "test@example.com",
        "to": "recipient@example.com",
    }

    # Get real API response
    response = analyzer.analyze_email(test_email)
    assert response is not None
    assert isinstance(response, EmailAnalysis)
    assert response.email_id == test_email["id"]
    assert response.summary is not None
    assert response.priority_score > 0
    assert response.priority_reason is not None


def test_analyze_email_success(email_analyzer, valid_email_data):
    """Test successful email analysis with real API."""
    result = email_analyzer.analyze_email(valid_email_data)

    assert result is not None
    assert result.email_id == valid_email_data["id"]
    assert result.summary is not None
    assert result.priority_score > 0
    assert result.priority_reason is not None
    assert isinstance(result.category, list)
    assert isinstance(result.action_type, list)
    assert isinstance(result.confidence_score, float)


def test_analyze_email_with_empty_fields(email_analyzer):
    """Test email analysis with minimal content."""
    minimal_email = {
        "id": f"test_{datetime.now().timestamp()}",
        "threadId": "thread1",
        "subject": "",
        "body": "Short test.",
        "received_date": datetime.now().isoformat(),
        "labels": '["INBOX"]',
        "from_": "test@example.com",
        "to": "recipient@example.com",
    }

    result = email_analyzer.analyze_email(minimal_email)
    assert result is not None
    assert result.email_id == minimal_email["id"]
    assert result.summary is not None


def test_analyze_email_api_error(email_analyzer):
    """Test handling of API errors with invalid content."""
    invalid_email = {
        "id": f"test_{datetime.now().timestamp()}",
        "threadId": "thread1",
        "subject": "Test Email",
        "body": "\x00\x01\x02\x03",  # Invalid binary content
        "received_date": datetime.now().isoformat(),
        "labels": '["INBOX"]',
        "from_": "test@example.com",
        "to": "recipient@example.com",
    }

    result = email_analyzer.analyze_email(invalid_email)
    assert result is None


def test_process_emails_batch_handling(email_analyzer):
    """Test email batch processing with real emails."""
    # Add test emails to database
    with get_email_session() as session:
        for i in range(5):
            email = Email(
                id=f"test_{i}_{datetime.now().timestamp()}",
                threadId=f"thread_{i}",
                subject=f"Test Email {i}",
                from_="test@example.com",
                to="recipient@example.com",
                received_date=datetime.now(),
                body=f"This is test email {i} that needs to be reviewed.",
                labels='["INBOX"]',
            )
            session.add(email)
        session.commit()

    # Process emails
    email_analyzer.process_emails()

    # Verify results
    with get_analysis_session() as session:
        analyses = session.query(EmailAnalysis).all()
        assert len(analyses) > 0
        for analysis in analyses:
            assert analysis.summary is not None
            assert analysis.priority_score > 0
            assert analysis.priority_reason is not None


def test_process_emails_error_handling(email_analyzer):
    """Test error handling during batch processing."""
    # Add test emails with some invalid content
    with get_email_session() as session:
        # Valid email
        email1 = Email(
            id="test_valid_1",
            threadId="thread_1",
            subject="Test Email 1",
            from_="test@example.com",
            to="recipient@example.com",
            received_date=datetime.now(),
            body="This is a valid test email.",
            labels='["INBOX"]',
        )
        # Invalid email
        email2 = Email(
            id="test_invalid_1",
            threadId="thread_2",
            subject="Test Email 2",
            from_="test@example.com",
            to="recipient@example.com",
            received_date=datetime.now(),
            body="\x00\x01\x02\x03",  # Invalid binary content
            labels='["INBOX"]',
        )
        session.add(email1)
        session.add(email2)
        session.commit()

    # Process emails
    email_analyzer.process_emails()

    # Verify results
    with get_analysis_session() as session:
        # Should have analysis for valid email
        analysis = (
            session.query(EmailAnalysis)
            .filter(EmailAnalysis.email_id.like("test_valid%"))
            .first()
        )
        assert analysis is not None
        assert analysis.summary is not None

        # Should not have analysis for invalid email
        invalid_analysis = (
            session.query(EmailAnalysis)
            .filter(EmailAnalysis.email_id.like("test_invalid%"))
            .first()
        )
        assert invalid_analysis is None
