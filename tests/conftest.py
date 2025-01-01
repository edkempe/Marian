"""Test configuration and fixtures."""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, scoped_session

from models.registry import Base
from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel
from shared_lib.schema_constants import MessageDefaults, AnalysisDefaults
from config.test_settings import test_settings
from shared_lib.database_session_util import (
    Session,
    EmailSessionFactory,
    AnalysisSessionFactory,
    CatalogSessionFactory,
)


@pytest.fixture(scope="session")
def test_data_dir():
    """Create and manage test data directory."""
    test_dir = test_settings.TEST_DATA_DIR
    test_dir.mkdir(parents=True, exist_ok=True)
    
    yield test_dir
    
    # Clean up test directory after all tests
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture(scope="session")
def test_dbs(test_data_dir):
    """Initialize test databases."""
    engines = {
        "default": create_engine(test_settings.DATABASE_URLS["default"]),
        "email": create_engine(test_settings.DATABASE_URLS["email"]),
        "analysis": create_engine(test_settings.DATABASE_URLS["analysis"]),
        "catalog": create_engine(test_settings.DATABASE_URLS["catalog"])
    }
    
    # Create all tables
    for engine in engines.values():
        Base.metadata.create_all(engine)
    
    yield engines
    
    # Clean up databases
    for engine in engines.values():
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_dbs):
    """Create a database session for testing."""
    session = Session()
    
    yield session
    
    # Rollback any changes
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def email_session(test_dbs):
    """Create an email database session for testing."""
    session = EmailSessionFactory()
    
    yield session
    
    # Rollback any changes
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def analysis_session(test_dbs):
    """Create an analysis database session for testing."""
    session = AnalysisSessionFactory()
    
    yield session
    
    # Rollback any changes
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def catalog_session(test_dbs):
    """Create a catalog database session for testing."""
    session = CatalogSessionFactory()
    
    yield session
    
    # Rollback any changes
    session.rollback()
    session.close()


@pytest.fixture(scope="session")
def test_dbs_email_analysis():
    """Create test databases."""
    return {
        "email": "sqlite:///test_email.db",
        "analysis": "sqlite:///test_analysis.db",
        "catalog": "sqlite:///test_catalog.db"
    }


@pytest.fixture(scope="session")
def email_session_email_analysis(test_dbs_email_analysis):
    """Create email database session."""
    engine = create_engine(test_dbs_email_analysis["email"])
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    yield Session()
    Session.remove()
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def analysis_session_email_analysis(test_dbs_email_analysis):
    """Create analysis database session."""
    engine = create_engine(test_dbs_email_analysis["analysis"])
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    yield Session()
    Session.remove()
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def catalog_session_email_analysis(test_dbs_email_analysis):
    """Create catalog database session."""
    engine = create_engine(test_dbs_email_analysis["catalog"])
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    yield Session()
    Session.remove()
    Base.metadata.drop_all(engine)


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
