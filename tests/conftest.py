"""Shared pytest fixtures."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
import pytz
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from config import CATALOG_CONFIG, EMAIL_CONFIG
from models.base import Base
from models.email import Email
from models.gmail_label import GmailLabel
from shared_lib.constants import DATABASE_CONFIG
from shared_lib.gmail_lib import GmailAPI
from src.app_catalog import CatalogChat


class TestDatabaseFactory:
    """Factory for creating and managing test databases."""

    def __init__(self, test_data_dir: Path):
        """Initialize test database factory.
        
        Args:
            test_data_dir: Directory to store test database files
        """
        self.test_data_dir = test_data_dir
        self.test_data_dir.mkdir(exist_ok=True)
        self._engines = {}
        self._session_factories = {}

    def get_engine(self, db_type: str):
        """Get or create SQLAlchemy engine for a database type."""
        if db_type not in self._engines:
            db_path = self.test_data_dir / f"test_{db_type}.db"
            self._engines[db_type] = create_engine(f"sqlite:///{db_path}")
            Base.metadata.create_all(self._engines[db_type])
        return self._engines[db_type]

    def get_session_factory(self, db_type: str) -> sessionmaker:
        """Get or create session factory for a database type."""
        if db_type not in self._session_factories:
            engine = self.get_engine(db_type)
            self._session_factories[db_type] = sessionmaker(
                bind=engine,
                expire_on_commit=False,
            )
        return self._session_factories[db_type]

    def cleanup(self):
        """Clean up all test databases."""
        # Close all connections
        for engine in self._engines.values():
            engine.dispose()
        
        # Remove database files
        for db_file in self.test_data_dir.glob("test_*.db"):
            db_file.unlink(missing_ok=True)


@pytest.fixture(scope="session")
def test_db_factory(tmp_path_factory) -> Generator[TestDatabaseFactory, None, None]:
    """Create test database factory.
    
    Uses pytest's tmp_path_factory to create a temporary directory that persists
    for the entire test session.
    """
    test_data_dir = tmp_path_factory.mktemp("test_data")
    factory = TestDatabaseFactory(test_data_dir)
    yield factory
    factory.cleanup()


@pytest.fixture(scope="function")
def email_session(test_db_factory) -> Generator[Session, None, None]:
    """Create a new email database session for each test."""
    session_factory = test_db_factory.get_session_factory("email")
    session = session_factory()
    
    # Start transaction
    session.begin_nested()
    
    yield session
    
    # Rollback transaction after test
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def analysis_session(test_db_factory) -> Generator[Session, None, None]:
    """Create a new analysis database session for each test."""
    session_factory = test_db_factory.get_session_factory("analysis")
    session = session_factory()
    
    # Start transaction
    session.begin_nested()
    
    yield session
    
    # Rollback transaction after test
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def catalog_session(test_db_factory) -> Generator[Session, None, None]:
    """Create a new catalog database session for each test."""
    session_factory = test_db_factory.get_session_factory("catalog")
    session = session_factory()
    
    # Start transaction
    session.begin_nested()
    
    yield session
    
    # Rollback transaction after test
    session.rollback()
    session.close()


@pytest.fixture(scope="session", autouse=True)
def validate_config():
    """Validate all configuration values before any tests run."""
    # Validate email config
    required_email_config = {"BATCH_SIZE", "COUNT", "LABELS", "EXCLUDED_LABELS"}
    for key in required_email_config:
        assert key in EMAIL_CONFIG, f"Missing required email config: {key}"

    # Validate catalog config
    required_catalog_config = {"ENABLE_SEMANTIC", "DB_PATH", "CHAT_LOG"}
    for key in required_catalog_config:
        assert key in CATALOG_CONFIG, f"Missing required catalog config: {key}"


@pytest.fixture(scope="session", autouse=True)
def verify_api_connection():
    """Verify API connection before running tests."""
    from shared_lib.anthropic_client_lib import test_anthropic_connection
    
    if not test_anthropic_connection():
        pytest.exit("API connection test failed. Please check your API key and connection.")
    return test_anthropic_connection


@pytest.fixture(scope="session")
def gmail_api():
    """Create Gmail API client for tests."""
    return GmailAPI()


@pytest.fixture(scope="session")
def catalog_chat():
    """Create CatalogChat client for tests."""
    return CatalogChat()


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
            full_api_response=json.dumps(
                {
                    "id": "msg1",
                    "threadId": "thread1",
                    "labelIds": ["INBOX", "UNREAD"],
                    "snippet": "This is a test email...",
                }
            ),
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
    now = datetime.now(pytz.utc)
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
def test_mode_analyzer():
    """Create an EmailAnalyzer instance in test mode."""
    from src.app_email_analyzer import EmailAnalyzer
    from tests.test_constants import TEST_MODE
    return EmailAnalyzer(test_mode=TEST_MODE)
