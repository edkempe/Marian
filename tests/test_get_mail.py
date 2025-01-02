"""Tests for email fetching functionality."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import os
import uuid
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from models.base import Base
from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel
from shared_lib.constants import DATABASE_CONFIG, ROOT_DIR, TESTING_CONFIG
from shared_lib.gmail_lib import GmailAPI
from shared_lib.api_version_utils import verify_gmail_version, check_api_changelog
from shared_lib.api_utils import GmailTestManager, validate_response_schema
from shared_lib.gmail_test_utils import (
    create_mock_gmail_service,
    create_test_email,
    create_test_label,
    setup_mock_messages,
    setup_mock_labels,
    setup_mock_message
)

from tests.utils.gmail_test_utils import gmail_test_context
from tests.utils.db_test_utils import create_test_db_session
from tests.utils.test_constants import (
    TEST_EMAIL,
    TEST_LABELS,
    TEST_MESSAGE,
    TEST_MESSAGES,
    TEST_ATTACHMENTS,
    API_ERROR_MESSAGE,
    TEST_DATES,
    TEST_MESSAGE_IDS,
    TEST_PLAIN_TEXT,
    TEST_HTML_CONTENT,
    TEST_UNICODE_TEXT,
)

from src.app_get_mail import (
    fetch_emails,
    get_label_id,
    process_email,
    list_labels,
)


@pytest.fixture
def email_session():
    """Get database session for testing."""
    with create_test_db_session() as session:
        Base.metadata.create_all(session.get_bind())
        yield session
        session.rollback()
        Base.metadata.drop_all(session.get_bind())


@pytest.fixture
def gmail_service():
    """Create a mock Gmail service."""
    return create_mock_gmail_service()


@pytest.fixture
def gmail_api(gmail_service):
    """Get Gmail API client for testing."""
    return GmailAPI(service=gmail_service)


@pytest.mark.parametrize("label_name,expected_id", [
    ("INBOX", "INBOX"),
    ("SENT", "SENT"),
    ("IMPORTANT", "IMPORTANT"),
    ("NONEXISTENT", None),
    ("", None),
    (None, None),
])
def test_get_label_id(gmail_service, label_name, expected_id):
    """Test label ID retrieval with various inputs."""
    with gmail_test_context(GmailAPI(service=gmail_service)) as ctx:
        # Set up test labels
        if expected_id:
            ctx.create_message(
                subject="Test Email",
                body="Test Body",
                label_ids=[expected_id]
            )
        
        # Test label retrieval
        result = get_label_id(gmail_service, label_name)
        assert result == expected_id


def test_get_label_id_error():
    """Test handling of API errors in label ID retrieval."""
    service = MagicMock()
    service.users().labels().list.side_effect = Exception(API_ERROR_MESSAGE)
    
    result = get_label_id(service, "INBOX")
    assert result is None


@pytest.mark.timeout(5)
def test_fetch_emails_success(gmail_service):
    """Test successful email fetching with pagination handling."""
    with gmail_test_context(GmailAPI(service=gmail_service)) as ctx:
        # Create test messages
        msg1 = ctx.create_message(subject="Test 1", body="Body 1")
        msg2 = ctx.create_message(subject="Test 2", body="Body 2")
        
        # Test email fetching
        result = fetch_emails(gmail_service)
        assert len(result) == 2
        assert any(m["id"] == msg1["id"] for m in result)
        assert any(m["id"] == msg2["id"] for m in result)


def test_fetch_emails_with_label(gmail_service):
    """Test fetching emails with label filter."""
    with gmail_test_context(GmailAPI(service=gmail_service), test_labels=["TEST_LABEL"]) as ctx:
        # Create test message with label
        msg = ctx.create_message(
            subject="Test Email",
            body="Test Body",
            label_ids=[ctx.created_labels[0]["id"]]
        )
        
        # Test email fetching with label
        result = fetch_emails(gmail_service, label_id=ctx.created_labels[0]["id"])
        assert len(result) == 1
        assert result[0]["id"] == msg["id"]


def test_fetch_emails_error():
    """Test error handling in email fetching."""
    service = MagicMock()
    service.users().messages().list.side_effect = Exception(API_ERROR_MESSAGE)
    
    result = fetch_emails(service)
    assert result == []


def test_process_email(gmail_service, email_session):
    """Test email processing and storage."""
    with gmail_test_context(GmailAPI(service=gmail_service)) as ctx:
        # Create test message
        msg = ctx.create_message(
            subject="Test Email",
            body="Test Body",
            from_address="sender@example.com",
            to_addresses=["recipient@example.com"]
        )
        
        # Process email
        process_email(gmail_service, msg["id"], email_session)
        
        # Verify email was stored
        stored_email = email_session.query(EmailMessage).first()
        assert stored_email is not None
        assert stored_email.subject == "Test Email"
        assert stored_email.from_address == "sender@example.com"
        assert stored_email.to_addresses == ["recipient@example.com"]


def test_process_email_with_labels(gmail_service, email_session):
    """Test email processing with labels."""
    with gmail_test_context(GmailAPI(service=gmail_service), test_labels=["TEST_LABEL"]) as ctx:
        # Create test message with label
        msg = ctx.create_message(
            subject="Test Email",
            body="Test Body",
            label_ids=[ctx.created_labels[0]["id"]]
        )
        
        # Process email
        process_email(gmail_service, msg["id"], email_session)
        
        # Verify email and labels were stored
        stored_email = email_session.query(EmailMessage).first()
        assert stored_email is not None
        assert len(stored_email.labels) == 1
        assert stored_email.labels[0].name == "TEST_LABEL"


def test_list_labels(gmail_service):
    """Test listing Gmail labels."""
    with gmail_test_context(GmailAPI(service=gmail_service), test_labels=["TEST_LABEL"]) as ctx:
        # Test label listing
        result = list_labels(gmail_service)
        assert len(result) > 0
        assert any(label["name"] == "TEST_LABEL" for label in result)


def test_list_labels_error():
    """Test error handling in label listing."""
    service = MagicMock()
    service.users().labels().list.side_effect = Exception(API_ERROR_MESSAGE)
    
    result = list_labels(service)
    assert result == []


@pytest.mark.integration
def test_get_messages_integration(gmail_test):
    """Test getting messages with real API."""
    with gmail_test_context(gmail_test.api) as ctx:
        # Create test message
        msg = ctx.create_message(subject="Integration Test", body="Test Body")
        
        # Test message retrieval
        result = gmail_test.api.service.users().messages().get(
            userId="me",
            id=msg["id"]
        ).execute()
        
        assert result["id"] == msg["id"]


@pytest.mark.integration
def test_label_operations_integration(gmail_test):
    """Test label operations with real API."""
    with gmail_test_context(gmail_test.api, test_labels=["TEST_LABEL"]) as ctx:
        # Create test message
        msg = ctx.create_message(
            subject="Label Test",
            body="Test Body",
            label_ids=[ctx.created_labels[0]["id"]]
        )
        
        # Test label application
        message = gmail_test.api.service.users().messages().get(
            userId="me",
            id=msg["id"]
        ).execute()
        
        assert ctx.created_labels[0]["id"] in message["labelIds"]
