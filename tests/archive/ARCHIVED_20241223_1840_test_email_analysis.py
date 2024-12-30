"""Tests for email analysis functionality."""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from constants import API_CONFIG

from app_email_analyzer import EmailAnalyzer, analyze_email
from models.email import Email
from models.email_analysis import EmailAnalysis

TEST_ANALYSES = {
    "meeting": {
        "summary": "Meeting scheduled for tomorrow",
        "category": "calendar",
        "sentiment": "neutral",
        "action_items": ["Attend meeting tomorrow"],
        "key_points": ["Meeting scheduled"],
    },
    "review": {
        "summary": "Document review request",
        "category": "review",
        "sentiment": "neutral",
        "action_items": ["Review document"],
        "key_points": ["Review needed"],
    },
}


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic API for testing."""
    with patch("anthropic.Anthropic") as mock:
        client = MagicMock()
        mock.return_value = client

        def create_message(messages, **kwargs):
            content = messages[0].content
            if "meeting" in content.lower():
                analysis = TEST_ANALYSES["meeting"]
            else:
                analysis = TEST_ANALYSES["review"]

            response = MagicMock()
            response.content = [{"text": json.dumps(analysis)}]
            return response

        client.messages.create.side_effect = create_message
        yield client


@pytest.fixture
def test_emails():
    """Create test emails for analysis."""
    return [
        Email(
            id="test1",
            thread_id="thread1",
            subject="Team Meeting",
            content="Meeting scheduled for tomorrow at 2 PM.",
            from_address="manager@example.com",
            to_address="team@example.com",
            received_date=datetime.utcnow(),
        ),
        Email(
            id="test2",
            thread_id="thread2",
            subject="Document Review",
            content="Please review this document by EOD.",
            from_address="colleague@example.com",
            to_address="me@example.com",
            received_date=datetime.utcnow(),
        ),
    ]


def test_analyze_email(mock_anthropic, test_emails, test_db_session):
    """Test analyzing a single email."""
    analyzer = EmailAnalyzer()
    analysis = analyzer.analyze_single(test_emails[0])
    assert analysis.category == "calendar"
    assert "meeting" in analysis.summary.lower()


def test_analyze_batch(mock_anthropic, test_emails, test_db_session):
    """Test analyzing multiple emails in batch."""
    analyzer = EmailAnalyzer()
    analyses = analyzer.analyze_batch(test_emails)
    assert len(analyses) == 2
    assert any(a.category == "calendar" for a in analyses)
    assert any(a.category == "review" for a in analyses)


def test_analysis_storage(mock_anthropic, test_emails, test_db_session):
    """Test storing analysis results in database."""
    analyzer = EmailAnalyzer()
    analysis = analyzer.analyze_single(test_emails[0])
    test_db_session.add(analysis)
    test_db_session.commit()

    stored = (
        test_db_session.query(EmailAnalysis)
        .filter_by(email_id=test_emails[0].id)
        .first()
    )
    assert stored is not None
    assert stored.category == "calendar"
    assert "meeting" in stored.summary.lower()


def test_analysis_error(mock_anthropic, test_emails):
    """Test handling of API errors in analysis."""
    mock_anthropic.messages.create.side_effect = Exception("API Error")
    analyzer = EmailAnalyzer()
    with pytest.raises(Exception):
        analyzer.analyze_single(test_emails[0])
