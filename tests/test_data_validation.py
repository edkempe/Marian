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
            labelIds=["INBOX", "UNREAD"],
            snippet="This is a test email...",
            historyId="12345",
            internalDate=datetime.now(timezone.utc),
            sizeEstimate=1024,
            raw=None,
            payload={
                "mimeType": "text/plain",
                "headers": [
                    {"name": "From", "value": "sender1@example.com"},
                    {"name": "To", "value": "recipient1@example.com"},
                    {"name": "Subject", "value": "Test Email 1"},
                    {"name": "Date", "value": datetime.now(timezone.utc).isoformat()}
                ],
                "body": {
                    "data": "This is a test email about Python programming."
                }
            }
        ),
        EmailMessage(
            id="msg2",
            threadId="thread2",
            labelIds=["INBOX", "IMPORTANT"],
            snippet="Another test email...",
            historyId="12346",
            internalDate=datetime.now(timezone.utc),
            sizeEstimate=2048,
            raw=None,
            payload={
                "mimeType": "text/plain",
                "headers": [
                    {"name": "From", "value": "sender2@example.com"},
                    {"name": "To", "value": "recipient2@example.com"},
                    {"name": "Subject", "value": "Test Email 2"},
                    {"name": "Date", "value": datetime.now(timezone.utc).isoformat()}
                ],
                "body": {
                    "data": "This is another test email about data validation."
                }
            }
        )
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
            id="analysis_abc123",
            email_id="msg1",
            summary="Test email about Python programming",
            sentiment="positive",
            categories=["programming", "education"],
            key_points=["Discusses Python", "Related to programming"],
            action_items=[{
                "description": "Review Python code",
                "due_date": datetime.now(timezone.utc).isoformat(),
                "priority": "high"
            }],
            priority_score=4,
            confidence_score=0.95,
            analysis_metadata={
                "model": "claude-3-opus-20240229",
                "processing_time": 1.23
            },
            model_version="claude-3-opus-20240229"
        ),
        EmailAnalysis(
            id="analysis_def456",
            email_id="msg2",
            summary="Test email about data validation",
            sentiment="neutral",
            categories=["testing", "validation"],
            key_points=["Discusses testing", "Covers data validation"],
            action_items=[{
                "description": "Update test cases",
                "due_date": datetime.now(timezone.utc).isoformat(),
                "priority": "medium"
            }],
            priority_score=3,
            confidence_score=0.85,
            analysis_metadata={
                "model": "claude-3-opus-20240229",
                "processing_time": 0.95
            },
            model_version="claude-3-opus-20240229"
        )
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
