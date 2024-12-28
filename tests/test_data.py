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

import pytest
from datetime import datetime, timezone
import json
from models.email import Email
from models.email_analysis import EmailAnalysis
from models.catalog import CatalogItem, Tag, CatalogTag
from models.asset_catalog import AssetCatalogItem, AssetDependency
from models.gmail_label import GmailLabel

@pytest.fixture
def sample_emails():
    """Create a set of test emails."""
    return [
        Email(
            id="msg1",
            thread_id="thread1",
            subject="Test Email 1",
            content="This is a test email about Python programming.",
            from_address="sender1@example.com",
            to_address="recipient1@example.com",
            received_date=datetime.now(timezone.utc),
            cc_address="cc1@example.com",
            bcc_address="bcc1@example.com",
            full_api_response=json.dumps({
                "id": "msg1",
                "threadId": "thread1",
                "labelIds": ["INBOX", "UNREAD"],
                "snippet": "This is a test email..."
            })
        ),
        Email(
            id="msg2",
            thread_id="thread2",
            subject="Test Email 2",
            content="Another test email about JavaScript development.",
            from_address="sender2@example.com",
            to_address="recipient2@example.com",
            received_date=datetime.now(timezone.utc),
            cc_address="cc2@example.com",
            bcc_address="bcc2@example.com",
            full_api_response=json.dumps({
                "id": "msg2",
                "threadId": "thread2",
                "labelIds": ["INBOX", "IMPORTANT"],
                "snippet": "Another test email..."
            })
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
            last_seen_at=now
        ),
        GmailLabel(
            id="SENT",
            name="Sent",
            type="system",
            is_active=True,
            first_seen_at=now,
            last_seen_at=now
        ),
        GmailLabel(
            id="Label_123",
            name="Custom Label",
            type="user",
            is_active=False,
            first_seen_at=now,
            last_seen_at=now,
            deleted_at=now
        )
    ]

@pytest.fixture
def sample_catalog_items():
    """Create a set of test catalog items."""
    return [
        CatalogItem(
            title="Python Tutorial",
            description="A beginner's guide to Python programming",
            content_type="tutorial",
            source_url="https://example.com/python",
            created_at=datetime.now(timezone.utc)
        ),
        CatalogItem(
            title="JavaScript Guide",
            description="Advanced JavaScript development techniques",
            content_type="guide",
            source_url="https://example.com/javascript",
            created_at=datetime.now(timezone.utc)
        ),
        CatalogItem(
            title="Machine Learning Basics",
            description="Introduction to machine learning concepts",
            content_type="course",
            source_url="https://example.com/ml",
            created_at=datetime.now(timezone.utc)
        )
    ]

@pytest.fixture
def sample_tags():
    """Create a set of test tags."""
    return [
        Tag(name="python", description="Python programming language"),
        Tag(name="javascript", description="JavaScript programming language"),
        Tag(name="beginner", description="Content suitable for beginners"),
        Tag(name="advanced", description="Advanced level content"),
        Tag(name="machine-learning", description="Machine learning topics")
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
            created_at=datetime.now(timezone.utc)
        ),
        EmailAnalysis(
            email_id="msg2",
            sentiment_score=0.7,
            priority_score=0.4,
            topic="Development",
            summary="Discussion about JavaScript development",
            created_at=datetime.now(timezone.utc)
        )
    ]

@pytest.fixture
def sample_asset_catalog_items():
    """Create sample asset catalog items."""
    return [
        AssetCatalogItem(
            name="frontend-app",
            version="1.0.0",
            asset_type="application",
            description="Frontend web application",
            created_at=datetime.now(timezone.utc)
        ),
        AssetCatalogItem(
            name="backend-api",
            version="1.0.0",
            asset_type="service",
            description="Backend API service",
            created_at=datetime.now(timezone.utc)
        )
    ]

@pytest.fixture
def sample_asset_dependencies(sample_asset_catalog_items):
    """Create sample asset dependencies."""
    return [
        AssetDependency(
            source_id=sample_asset_catalog_items[0].id,  # frontend-app
            target_id=sample_asset_catalog_items[1].id,  # backend-api
            dependency_type="runtime",
            created_at=datetime.now(timezone.utc)
        )
    ]
