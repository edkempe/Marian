"""Tests for email fetching functionality."""

import pytest
from datetime import datetime
from pathlib import Path
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from models.base import Base
from shared_lib.constants import DATABASE_CONFIG, ROOT_DIR, TESTING_CONFIG
from shared_lib.gmail_lib import GmailAPI
from shared_lib.api_version_utils import verify_gmail_version, check_api_changelog
from shared_lib.api_utils import GmailTestManager, validate_response_schema, build_gmail_service
from shared_lib.gmail_utils import (
    create_test_email,
    setup_test_labels,
    cleanup_test_labels,
    create_mock_gmail_service,
    setup_mock_message,
    setup_mock_messages
)

from src.app_get_mail import (
    count_emails,
    fetch_emails,
    get_label_id,
    process_email,
)

from tests.utils.db_test_utils import create_test_db_session
from tests.utils.email_test_utils import create_test_message
from tests.utils.test_constants import (
    TEST_EMAIL,
    TEST_LABELS,
    TEST_MESSAGE,
    TEST_MESSAGES,
    TEST_ATTACHMENTS,
    API_ERROR_MESSAGE,
)

# Gmail API response schemas
MESSAGE_SCHEMA = {
    "id": str,
    "threadId": str,
    "labelIds": list,
    "snippet": str,
    "payload": dict
}

LABEL_SCHEMA = {
    "id": str,
    "name": str,
    "type": str
}

@pytest.fixture
def email_session():
    """Get database session for testing."""
    with create_test_db_session() as session:
        yield session

@pytest.fixture
def gmail_service():
    """Create a mock Gmail service."""
    return create_mock_gmail_service()

@pytest.fixture
def gmail_api(gmail_service):
    """Get Gmail API client for testing."""
    api = GmailAPI(label_db_path=":memory:")
    api._get_gmail_service = lambda: gmail_service
    return api

@pytest.fixture
def sample_emails(email_session):
    """Create sample emails for testing."""
    emails = [
        create_test_email(id=f"test{i}", date=date)
        for i, date in enumerate(TEST_DATES, 1)
    ]
    
    for email in emails:
        email_session.add(email)
    email_session.commit()
    
    return emails

@pytest.fixture
def gmail_test():
    """Fixture for Gmail API testing."""
    test_manager = GmailTestManager()
    
    # Check API availability
    if not test_manager.get_test_account():
        pytest.skip("Gmail test account not configured")
    
    return test_manager

@pytest.fixture
def gmail_test_context(labels):
    """Context manager for Gmail API testing."""
    test_manager = GmailTestManager()
    
    # Check API availability
    if not test_manager.get_test_account():
        pytest.skip("Gmail test account not configured")
    
    # Create test labels
    created_labels = []
    for label_name in labels:
        label = test_manager.create_label(label_name)
        created_labels.append(label)
    
    try:
        yield test_manager
    finally:
        # Clean up test labels
        for label in created_labels:
            test_manager.delete_label(label['id'])

def test_init_database(email_session):
    """Test database initialization."""
    from sqlalchemy import inspect
    
    # Initialize database
    init_database(email_session)
    
    # Verify Email table exists
    inspector = inspect(email_session.get_bind())
    tables = inspector.get_table_names()
    assert "emails" in tables
    
    # Verify required columns exist
    columns = {col["name"] for col in inspector.get_columns("emails")}
    required_columns = {"id", "threadId", "subject", "from", "to", "body", "date"}
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

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
    # Set up mock response for valid labels
    if expected_id:
        setup_test_labels(gmail_service, [TEST_LABELS[label_name]])
    else:
        setup_test_labels(gmail_service, [])
    
    result = get_label_id(gmail_service, label_name)
    assert result == expected_id

def test_get_label_id_error():
    """Test handling of API errors in label ID retrieval."""
    service = MagicMock()
    service.users().labels().list.side_effect = Exception(API_ERROR_MESSAGE)
    
    result = get_label_id(service, "INBOX")
    assert result is None

def test_fetch_emails_success(gmail_service):
    """Test successful email fetching."""
    # Set up mock response
    setup_mock_messages(gmail_service, [
        {"id": "msg1"},
        {"id": "msg2"}
    ])
    
    # Call function
    result = fetch_emails(gmail_service)
    
    # Verify results
    assert len(result) == 2
    assert result[0]["id"] == "msg1"

def test_fetch_emails_with_label(gmail_service):
    """Test fetching emails with label filter."""
    # Set up mock response
    setup_mock_messages(gmail_service, [{"id": "msg1"}])
    
    # Call function with label
    result = fetch_emails(gmail_service, label_id="INBOX")
    assert len(result) == 1

def test_fetch_emails_error():
    """Test error handling in email fetching."""
    service = MagicMock()
    service.users().messages().list.side_effect = Exception(API_ERROR_MESSAGE)
    
    messages = fetch_emails(service)
    assert messages == []

def test_process_email(gmail_service, email_session):
    """Test email processing and storage."""
    # Create test message
    message = create_test_message(
        msg_id=TEST_EMAIL["id"],
        subject=TEST_EMAIL["subject"],
        from_addr=TEST_EMAIL["from_"],
        to_addr=TEST_EMAIL["to"],
        body_text=TEST_EMAIL["body"],
    )
    
    # Set up mock response
    setup_mock_message(gmail_service, message)
    
    # Process email
    process_email(gmail_service, TEST_EMAIL["id"], email_session)
    
    # Verify email was stored
    result = email_session.query(Email).filter_by(id=TEST_EMAIL["id"]).first()
    assert result is not None
    assert result.subject == TEST_EMAIL["subject"]
    assert result.from_ == TEST_EMAIL["from_"]
    assert result.to == TEST_EMAIL["to"]
    assert result.body == TEST_EMAIL["body"]

def test_process_email_with_body(gmail_service, email_session):
    """Test email processing with different body formats."""
    # Test plain text
    message = create_test_message(
        msg_id=TEST_MESSAGE_IDS["PLAIN"],
        body_text=TEST_PLAIN_TEXT
    )
    
    # Set up mock response
    setup_mock_message(gmail_service, message)
    
    process_email(gmail_service, TEST_MESSAGE_IDS["PLAIN"], email_session)
    
    result = email_session.query(Email).filter_by(id=TEST_MESSAGE_IDS["PLAIN"]).first()
    assert result is not None
    assert result.body == TEST_PLAIN_TEXT

def test_process_email_with_html(gmail_service, email_session):
    """Test processing email with HTML content."""
    message = create_test_message(
        msg_id=TEST_MESSAGE_IDS["HTML"],
        body_text="Hello World!",
        body_html=TEST_HTML_CONTENT
    )
    
    # Set up mock response
    setup_mock_message(gmail_service, message)
    
    process_email(gmail_service, TEST_MESSAGE_IDS["HTML"], email_session)
    
    result = email_session.query(Email).filter_by(id=TEST_MESSAGE_IDS["HTML"]).first()
    assert result is not None
    assert "Hello World!" in result.body  # Should prefer plain text over HTML

def test_process_email_with_attachments(gmail_service, email_session):
    """Test processing email with attachments."""
    message = create_test_message(
        msg_id=TEST_MESSAGE_IDS["ATTACHMENTS"],
        body_text="Email with attachment",
        attachments=TEST_ATTACHMENTS
    )
    
    # Set up mock response
    setup_mock_message(gmail_service, message)
    
    process_email(gmail_service, TEST_MESSAGE_IDS["ATTACHMENTS"], email_session)
    
    result = email_session.query(Email).filter_by(id=TEST_MESSAGE_IDS["ATTACHMENTS"]).first()
    assert result is not None
    assert result.has_attachments is True

def test_process_email_with_missing_fields(gmail_service, email_session):
    """Test processing email with missing optional fields."""
    message = create_test_message(
        msg_id=TEST_MESSAGE_IDS["MINIMAL"],
        subject="Minimal Email"
    )
    
    # Set up mock response
    setup_mock_message(gmail_service, message)
    
    process_email(gmail_service, TEST_MESSAGE_IDS["MINIMAL"], email_session)
    
    result = email_session.query(Email).filter_by(id=TEST_MESSAGE_IDS["MINIMAL"]).first()
    assert result is not None
    assert result.subject == "Minimal Email"
    assert result.to == ""  # Optional fields should be empty strings
    assert result.cc == ""
    assert result.bcc == ""
    assert result.threadId is None
    assert result.labelIds == ""

def test_process_email_with_unicode(gmail_service, email_session):
    """Test processing email with Unicode content."""
    message = create_test_message(
        msg_id=TEST_MESSAGE_IDS["UNICODE"],
        subject="Unicode Test",
        body_text=TEST_UNICODE_TEXT
    )
    
    # Set up mock response
    setup_mock_message(gmail_service, message)
    
    process_email(gmail_service, TEST_MESSAGE_IDS["UNICODE"], email_session)
    
    result = email_session.query(Email).filter_by(id=TEST_MESSAGE_IDS["UNICODE"]).first()
    assert result is not None
    assert result.body == TEST_UNICODE_TEXT

def test_get_oldest_email_date(email_session, sample_emails):
    """Test getting oldest email date."""
    oldest_date = get_oldest_email_date(email_session)
    assert oldest_date == TEST_DATES[0]

def test_get_newest_email_date(email_session, sample_emails):
    """Test getting newest email date."""
    newest_date = get_newest_email_date(email_session)
    assert newest_date == TEST_DATES[-1]

def test_count_emails(email_session, sample_emails):
    """Test email counting."""
    count = count_emails(email_session)
    assert count == len(sample_emails)

def test_list_labels(gmail_service):
    """Test listing Gmail labels."""
    setup_test_labels(gmail_service, [TEST_LABELS["INBOX"]])
    
    labels = list_labels(gmail_service)
    assert len(labels) == 1
    assert labels[0]["id"] == "INBOX"

def test_list_labels_error():
    """Test error handling in label listing."""
    service = MagicMock()
    service.users().labels().list.side_effect = Exception(API_ERROR_MESSAGE)
    
    labels = list_labels(service)
    assert labels == []

def test_get_messages(gmail_test):
    """Test getting messages with real API."""
    service = build_gmail_service()  # Your existing service builder
    
    # Get messages
    messages = get_messages(service)
    assert messages
    
    # Validate first message schema
    if messages:
        errors = validate_response_schema(messages[0], MESSAGE_SCHEMA)
        assert not errors, f"Schema validation errors: {errors}"
        
        # Save response for future reference
        gmail_test.save_test_response("sample_message", messages[0])

def test_label_operations(gmail_test):
    """Test label operations with real API."""
    service = build_gmail_service()
    
    # Use context manager for test labels
    with gmail_test.test_labels(service) as created_labels:
        # Create test label
        label_name = "TEST_LABEL_" + str(uuid.uuid4())
        label = create_label(service, label_name)
        created_labels.append(label)
        
        # Validate label schema
        errors = validate_response_schema(label, LABEL_SCHEMA)
        assert not errors, f"Schema validation errors: {errors}"
        
        # Test label operations
        assert label["name"] == label_name
        
        # Save response for future reference
        gmail_test.save_test_response("sample_label", label)

@pytest.mark.integration
def test_get_label_id_integration():
    """Test label ID retrieval with real API."""
    with gmail_test_context(['INBOX']) as ctx:
        # Create test label
        label_id = ctx.created_labels[0]['id']
        
        # Test retrieval
        api = GmailAPI()
        result = api.get_label_id('TEST_INBOX')
        assert result == label_id

@pytest.mark.integration
def test_process_email_integration():
    """Test email processing with real API."""
    with gmail_test_context(['INBOX']) as ctx:
        # Create test message
        msg_id = ctx.create_message(
            subject='Test Subject',
            body='Test content',
            sender='test@example.com'
        )
        
        # Process message
        api = GmailAPI()
        result = api.process_message(msg_id)
        
        # Verify result
        assert result['id'] == msg_id
        assert result['subject'] == 'Test Subject'
        assert result['sender'] == 'test@example.com'

@pytest.mark.integration
def test_list_labels_integration():
    """Test listing labels with real API."""
    with gmail_test_context(['INBOX', 'SENT']) as ctx:
        api = GmailAPI()
        labels = api.list_labels()
        
        # Verify test labels exist
        test_ids = {label['id'] for label in ctx.created_labels}
        result_ids = {label['id'] for label in labels}
        assert test_ids.issubset(result_ids)
