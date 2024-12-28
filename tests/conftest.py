"""Shared pytest fixtures."""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.base import Base
from config import EMAIL_CONFIG, CATALOG_CONFIG
from shared_lib.gmail_lib import GmailAPI
from src.app_catalog import CatalogChat
from models.email import Email
from models.gmail_label import GmailLabel
from datetime import datetime
import json
from typing import Generator
import pytz

@pytest.fixture(scope="session", autouse=True)
def validate_config():
    """Validate all configuration values before any tests run."""
    # Validate email config
    required_email_config = {
        'BATCH_SIZE', 'COUNT', 'LABELS', 'EXCLUDED_LABELS'
    }
    for key in required_email_config:
        assert key in EMAIL_CONFIG, f"Missing required email config: {key}"

    # Validate catalog config
    required_catalog_config = {
        'ENABLE_SEMANTIC', 'DB_PATH', 'CHAT_LOG'
    }
    for key in required_catalog_config:
        assert key in CATALOG_CONFIG, f"Missing required catalog config: {key}"

@pytest.fixture(scope="session")
def gmail_api():
    """Create Gmail API client for tests."""
    return GmailAPI()

@pytest.fixture(scope="session")
def catalog_chat():
    """Create CatalogChat client for tests."""
    return CatalogChat()

@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for tests."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="session")
def db_session_factory(db_engine):
    """Create a session factory."""
    return sessionmaker(bind=db_engine)

@pytest.fixture
def db_session(db_session_factory):
    """Create a new database session for a test."""
    session = db_session_factory()
    yield session
    session.execute(text('DELETE FROM emails'))
    session.execute(text('DELETE FROM gmail_labels'))
    session.commit()
    session.rollback()
    session.close()

@pytest.fixture
def sample_emails():
    """Create a set of test emails."""
    return [
        Email(
            id="msg1",
            thread_id="thread1",
            subject="Test Email 1",
            body="This is a test email about Python programming.",
            sender="sender1@example.com",
            to_address="recipient1@example.com",
            received_date=datetime.now(pytz.utc),
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
            body="Another test email about JavaScript development.",
            sender="sender2@example.com",
            to_address="recipient2@example.com",
            received_date=datetime.now(pytz.utc),
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
    now = datetime.now(pytz.utc)
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
