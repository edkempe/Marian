"""Test data fixtures for pytest.

This module provides shared test data fixtures that can be reused across
different test modules. This helps maintain consistency in test data and
reduces duplication.

Key fixtures:
- sample_emails: Common email test data
- sample_catalog_items: Common catalog items for testing
- sample_tags: Common tags for testing
- sample_analysis: Common email analysis results
"""

import json
from datetime import datetime, timezone

import pytest

from models.email import EmailMessage
from models.catalog import CatalogEntry, CatalogTag, Tag
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel


@pytest.fixture
def sample_emails():
    """Create a set of test emails."""
    return [
        EmailMessage(
            id="msg1",
            threadId="thread1",
            subject="Test Email 1",
            body="This is a test email about Python programming.",
            from_="sender1@example.com",
            to="recipient1@example.com",
            received_date=datetime.now(timezone.utc),
            cc="cc1@example.com",
            bcc="bcc1@example.com",
            full_api_response=json.dumps(
                {
                    "id": "msg1",
                    "threadId": "thread1",
                    "labelIds": ["INBOX", "UNREAD"],
                    "snippet": "This is a test email...",
                }
            ),
        ),
        EmailMessage(
            id="msg2",
            threadId="thread2",
            subject="Test Email 2",
            body="Another test email about JavaScript development.",
            from_="sender2@example.com",
            to="recipient2@example.com",
            received_date=datetime.now(timezone.utc),
            cc="cc2@example.com",
            bcc="bcc2@example.com",
            full_api_response=json.dumps(
                {
                    "id": "msg2",
                    "threadId": "thread2",
                    "labelIds": ["INBOX", "IMPORTANT"],
                    "snippet": "Another test email...",
                }
            ),
        ),
    ]


@pytest.fixture
def sample_gmail_labels():
    """Create a set of test Gmail labels."""
    now = datetime.now(timezone.utc)
    return [
        GmailLabel(
            id="INBOX",
            name="Inbox",
            type="system",
            is_active=True,
            first_seen_at=now,
            last_seen_at=now,
        ),
        GmailLabel(
            id="SENT",
            name="Sent",
            type="system",
            is_active=True,
            first_seen_at=now,
            last_seen_at=now,
        ),
        GmailLabel(
            id="Label_123",
            name="Custom Label",
            type="user",
            is_active=False,
            first_seen_at=now,
            last_seen_at=now,
            deleted_at=now,
        ),
    ]


@pytest.fixture
def sample_catalog_items():
    """Create a set of test catalog items."""
    return [
        CatalogEntry(
            title="Python Tutorial",
            description="A beginner's guide to Python programming",
            content_type="tutorial",
            source_url="https://example.com/python",
            created_at=datetime.now(timezone.utc),
        ),
        CatalogEntry(
            title="JavaScript Guide",
            description="Advanced JavaScript development techniques",
            content_type="guide",
            source_url="https://example.com/javascript",
            created_at=datetime.now(timezone.utc),
        ),
        CatalogEntry(
            title="Machine Learning Basics",
            description="Introduction to machine learning concepts",
            content_type="course",
            source_url="https://example.com/ml",
            created_at=datetime.now(timezone.utc),
        ),
    ]


@pytest.fixture
def sample_tags():
    """Create a set of test tags."""
    return [
        Tag(name="python", description="Python programming language"),
        Tag(name="javascript", description="JavaScript programming language"),
        Tag(name="beginner", description="Content suitable for beginners"),
        Tag(name="advanced", description="Advanced level content"),
        Tag(name="machine-learning", description="Machine learning topics"),
    ]


@pytest.fixture
def sample_analysis():
    """Create sample email analysis results."""
    return [
        EmailAnalysis(
            email_id="msg1",
            sentiment_score=0.8,
            priority_score=0.6,
            topic="Programming",
            summary="Discussion about Python programming",
            created_at=datetime.now(timezone.utc),
        ),
        EmailAnalysis(
            email_id="msg2",
            sentiment_score=0.7,
            priority_score=0.4,
            topic="Development",
            summary="Discussion about JavaScript development",
            created_at=datetime.now(timezone.utc),
        ),
    ]


@pytest.fixture
def sample_asset_catalog_items():
    """Create sample asset catalog items."""
    return [
        CatalogEntry(
            title="frontend-app",
            description="Frontend web application",
            content_type="application",
            source_url="https://example.com/frontend",
            created_at=datetime.now(timezone.utc),
        ),
        CatalogEntry(
            title="backend-api",
            description="Backend API service",
            content_type="service",
            source_url="https://example.com/backend",
            created_at=datetime.now(timezone.utc),
        ),
    ]


@pytest.fixture
def sample_asset_dependencies(sample_asset_catalog_items):
    """Create sample asset dependencies."""
    return [
        CatalogEntry(
            title="dependency",
            description="Dependency between frontend and backend",
            content_type="dependency",
            source_url="https://example.com/dependency",
            created_at=datetime.now(timezone.utc),
        )
    ]
