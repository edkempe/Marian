"""Test utilities for Marian project."""

import json
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, Generator, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.email import Email
from models.email_analysis import EmailAnalysis
from shared_lib.constants import SentimentTypes
from tests.test_config import TEST_ANALYSIS_DB, TEST_EMAIL_DB

# Test data constants
TEST_EMAIL_SUBJECT = "Test Email"
TEST_EMAIL_BODY = "Test content"
TEST_EMAIL_FROM = "test@example.com"
TEST_EMAIL_TO = "recipient@example.com"
TEST_ANALYSIS_SUMMARY = "Test summary"
TEST_ANALYSIS_CATEGORY = ["work"]
TEST_ANALYSIS_PRIORITY = 3
TEST_ANALYSIS_REASON = "Important work email"
TEST_ANALYSIS_ACTION_TYPES = ["review"]
TEST_ANALYSIS_KEY_POINTS = ["Test point 1", "Test point 2"]


@contextmanager
def get_test_session(db_path: str) -> Generator[Session, None, None]:
    """Get a test database session.
    
    Args:
        db_path: Path to the test database
        
    Yields:
        SQLAlchemy session
    """
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def create_test_email(
    subject: str = TEST_EMAIL_SUBJECT,
    body: str = TEST_EMAIL_BODY,
    labels: Optional[List[str]] = None,
    from_email: str = TEST_EMAIL_FROM,
    to_email: str = TEST_EMAIL_TO,
) -> Email:
    """Create a test email object.
    
    Args:
        subject: Email subject
        body: Email body
        labels: Email labels
        from_email: Sender email
        to_email: Recipient email
        
    Returns:
        Email object for testing
    """
    return Email(
        id=f"test_{datetime.now().timestamp()}",
        threadId="thread1",
        subject=subject,
        body=body,
        date=datetime.now(),
        labelIds=json.dumps(labels or ["INBOX"]),
        from_=from_email,
        to=to_email,
    )


def create_test_analysis(
    email_id: Optional[str] = None,
    summary: str = TEST_ANALYSIS_SUMMARY,
    category: List[str] = None,
    priority_score: int = TEST_ANALYSIS_PRIORITY,
    priority_reason: str = TEST_ANALYSIS_REASON,
    action_needed: bool = True,
    action_type: List[str] = None,
    key_points: List[str] = None,
    people_mentioned: List[str] = None,
    sentiment: str = SentimentTypes.NEUTRAL,
    confidence_score: float = 0.8,
) -> EmailAnalysis:
    """Create a test email analysis object.
    
    Args:
        email_id: ID of the email being analyzed
        summary: Analysis summary
        category: Email categories
        priority_score: Priority score (1-5)
        priority_reason: Reason for priority
        action_needed: Whether action is needed
        action_type: Types of actions needed
        key_points: Key points from email
        people_mentioned: People mentioned in email
        sentiment: Email sentiment
        confidence_score: Confidence score (0-1)
        
    Returns:
        EmailAnalysis object for testing
    """
    if email_id is None:
        email_id = f"test_{datetime.now().timestamp()}"
        
    return EmailAnalysis(
        email_id=email_id,
        threadId="thread1",
        analyzed_date=datetime.now(),
        prompt_version="1.0",
        summary=summary,
        category=json.dumps(category or TEST_ANALYSIS_CATEGORY),
        priority_score=priority_score,
        priority_reason=priority_reason,
        action_needed=action_needed,
        action_type=json.dumps(action_type or TEST_ANALYSIS_ACTION_TYPES),
        key_points=json.dumps(key_points or TEST_ANALYSIS_KEY_POINTS),
        people_mentioned=json.dumps(people_mentioned or []),
        links_found=json.dumps([]),
        links_display=json.dumps([]),
        sentiment=sentiment,
        confidence_score=confidence_score,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def assert_email_analysis_response(analysis: Dict) -> None:
    """Assert that an email analysis response is valid.
    
    Args:
        analysis: Email analysis response to validate
    """
    assert analysis is not None
    assert analysis.summary is not None
    assert 1 <= analysis.priority_score <= 5
    assert analysis.priority_reason is not None
    assert isinstance(analysis.category, list)
    assert isinstance(analysis.action_type, list)
    assert isinstance(analysis.key_points, list)
    assert isinstance(analysis.people_mentioned, list)
    assert analysis.sentiment in SentimentTypes.values()
    assert 0.0 <= analysis.confidence_score <= 1.0
