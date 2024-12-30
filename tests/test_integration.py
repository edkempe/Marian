"""Integration tests for Gmail API functionality.

IMPORTANT: These are real integration tests that use the actual Gmail API.
Mock testing is NOT used in this codebase. Any changes to use mocks require explicit permission.

The tests interact with real Gmail data and require:
1. Valid Gmail API credentials
2. Access to a Gmail account
3. Real emails in the account to test with

Test data is limited to prevent timeouts:
- Email fetching is limited to small batches (max 10 messages)
- Processing tests use only 3 messages at a time
- Date ranges are kept to 1-7 days
"""

import json
import os
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.email import Email
from models.email_analysis import EmailAnalysis
from shared_lib.constants import API_CONFIG, DATABASE_CONFIG, EMAIL_CONFIG
from shared_lib.database_session_util import get_analysis_session, get_email_session
from shared_lib.gmail_lib import GmailAPI
from src.app_email_analyzer import EmailAnalyzer
from src.app_email_reports import EmailAnalytics
from src.app_get_mail import (
    fetch_emails,
    get_email_session,
    init_database,
    list_labels,
    process_email,
)

# test_db_session fixture is automatically available from conftest.py


@pytest.fixture(scope="session")
def gmail_api():
    """Create and initialize Gmail API instance."""
    gmail = GmailAPI()
    gmail.setup_label_database()  # Initialize label database
    gmail.sync_labels()  # Sync labels from Gmail
    return gmail


def test_gmail_authentication(gmail_api):
    """Test Gmail API authentication."""
    assert gmail_api.service is not None

    # Test basic profile access
    profile = gmail_api.service.users().getProfile(userId="me").execute()
    assert "emailAddress" in profile
    print(f"Authenticated as: {profile['emailAddress']}")


def test_label_operations(gmail_api):
    """Test Gmail label operations."""
    # List all labels
    labels = list_labels(gmail_api.service)
    assert len(labels) > 0

    # Print found labels
    print("\nAvailable labels:")
    for label in labels:
        print(f"- {label['name']} ({label['id']})")

    # Test getting specific system labels
    system_labels = ["INBOX", "SENT", "DRAFT", "SPAM"]
    for label in system_labels:
        label_id = gmail_api.get_label_id(label)
        assert label_id is not None
        print(f"\nFound {label} label: {label_id}")


def test_label_operations_error(gmail_api):
    """Test error handling in label operations."""
    # Test non-existent label
    non_existent_label = "NON_EXISTENT_LABEL_12345"
    label_id = gmail_api.get_label_id(non_existent_label)
    assert label_id is None

    # Test empty label name
    empty_label = ""
    label_id = gmail_api.get_label_id(empty_label)
    assert label_id is None


def test_email_fetching(gmail_api):
    """Test fetching emails from Gmail."""
    # Test fetching with date range
    start_date = datetime.now() - timedelta(days=1)
    messages = fetch_emails(gmail_api.service, start_date=start_date, max_results=10)
    assert isinstance(messages, list)

    # Test fetching with label
    messages = fetch_emails(gmail_api.service, label="INBOX", max_results=10)
    assert isinstance(messages, list)

    # Test fetching with invalid label
    messages = fetch_emails(
        gmail_api.service, label="NONEXISTENT_LABEL", max_results=10
    )
    assert len(messages) == 0

    # Print details of a few messages
    for msg_id in [m["id"] for m in messages[: EMAIL_CONFIG["BATCH_SIZE"]]]:
        try:
            # Get full message details
            message = (
                gmail_api.service.users()
                .messages()
                .get(userId="me", id=msg_id)
                .execute()
            )
            headers = {
                header["name"]: header["value"]
                for header in message["payload"]["headers"]
            }
            print("\nMessage details:")
            print(f"Subject: {headers.get('Subject', 'No subject')}")
            print(f"Date: {headers.get('Date', 'Unknown')}")
        except Exception as e:
            print(f"Error getting message details: {str(e)}")


def test_email_fetching_error_handling(gmail_api):
    """Test error handling in email fetching."""
    # Test with future date
    future_date = datetime.now() + timedelta(days=365)
    messages = fetch_emails(gmail_api.service, start_date=future_date)
    assert len(messages) == 0

    # Test with very old date
    old_date = datetime.now() - timedelta(days=3650)  # 10 years ago
    messages = fetch_emails(gmail_api.service, start_date=old_date)
    assert isinstance(messages, list), "Should return a list even for old dates"


def test_email_processing(gmail_api, test_db_session):
    """Test processing and storing emails."""
    print("\nFetching recent emails for processing...")
    start_date = datetime.now() - timedelta(days=1)
    messages = fetch_emails(gmail_api.service, start_date=start_date, max_results=3)
    print(f"Found {len(messages)} messages to process")

    # Process messages
    processed_count = 0
    for msg_id in [m["id"] for m in messages]:
        print(f"\nProcessing message {processed_count + 1} of {len(messages)}")
        try:
            # Get full message details
            message = (
                gmail_api.service.users()
                .messages()
                .get(userId="me", id=msg_id)
                .execute()
            )

            # Extract headers
            headers = {
                header["name"]: header["value"]
                for header in message["payload"]["headers"]
            }

            # Create email object
            email = Email(
                id=message["id"],
                threadId=message["threadId"],
                subject=headers.get("Subject", "[No Subject]"),
                from_=headers.get("From", "[No Sender]"),
                to=headers.get("To", "[No Recipient]"),
                received_date=parsedate_to_datetime(headers.get("Date", "")),
                labels=",".join(message.get("labelIds", [])),
                body=message.get("snippet", ""),
            )

            # Store in database
            test_db_session.add(email)
            test_db_session.commit()
            processed_count += 1
            print(
                f"Successfully processed message with subject: {email.subject[:50]}..."
            )

        except Exception as e:
            print(f"Error processing message {msg_id}: {str(e)}")
            continue

    print(f"\nProcessed {processed_count} emails successfully")
    assert processed_count > 0, "Should process at least one email"

    # Verify emails were stored in database
    stored_emails = test_db_session.query(Email).all()
    assert len(stored_emails) >= processed_count

    # Verify email structure (not specific content)
    latest_email = stored_emails[-1]
    assert isinstance(latest_email.subject, str)
    assert isinstance(latest_email.from_, str)
    assert isinstance(latest_email.to, str)
    assert isinstance(latest_email.labels, str)
    assert len(latest_email.labels) > 0  # Should have at least one label


def test_email_processing_error_handling(gmail_api, test_db_session):
    """Test error handling in email processing."""
    # Test with invalid message ID
    invalid_msg_id = "INVALID_MESSAGE_ID_12345"
    with pytest.raises(Exception) as exc_info:
        result = (
            gmail_api.service.users()
            .messages()
            .get(userId="me", id=invalid_msg_id)
            .execute()
        )
    error_msg = str(exc_info.value).lower()
    assert "invalid" in error_msg or "not found" in error_msg

    # Test with missing required fields
    msg_with_missing_fields = {
        "id": "12345",
        "threadId": "thread123",
        "labelIds": ["INBOX"],
        "payload": {"headers": []},  # Empty headers
    }

    try:
        # Directly test the processing logic
        headers = {}
        email = Email(
            id=msg_with_missing_fields["id"],
            threadId=msg_with_missing_fields["threadId"],
            subject=headers.get("Subject", "[No Subject]"),  # Provide default
            from_=headers.get("From", "[No Sender]"),  # Provide default
            to=headers.get("To", "[No Recipient]"),  # Provide default
            received_date=datetime.now(),  # Use current time as fallback
            labels=",".join(msg_with_missing_fields.get("labelIds", [])),
            body=msg_with_missing_fields.get("snippet", ""),
        )
        test_db_session.add(email)
        test_db_session.commit()
    except Exception as e:
        assert False, f"Should handle missing fields gracefully: {str(e)}"

    # Verify the email was stored with default values
    stored_email = (
        test_db_session.query(Email).filter_by(id=msg_with_missing_fields["id"]).first()
    )
    assert stored_email is not None
    assert stored_email.subject == "[No Subject]"
    assert stored_email.from_ == "[No Sender]"
    assert stored_email.to == "[No Recipient]"


def test_email_date_queries(gmail_api, test_db_session):
    """Test email date querying functionality."""
    print("\nTesting email date queries...")

    # Test querying by date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    print(f"Fetching emails from {start_date.date()} to {end_date.date()}")

    messages = fetch_emails(
        gmail_api.service, start_date=start_date, end_date=end_date, max_results=10
    )

    print(f"Found {len(messages)} messages in date range")

    # Process some messages to test with
    processed_count = 0
    for msg_id in [m["id"] for m in messages[:3]]:  # Process up to 3
        print(f"\nProcessing message {processed_count + 1} of 3")
        try:
            message = (
                gmail_api.service.users()
                .messages()
                .get(userId="me", id=msg_id)
                .execute()
            )

            headers = {
                header["name"]: header["value"]
                for header in message["payload"]["headers"]
            }

            email = Email(
                id=message["id"],
                threadId=message["threadId"],
                subject=headers.get("Subject", "[No Subject]"),
                from_=headers.get("From", "[No Sender]"),
                to=headers.get("To", "[No Recipient]"),
                received_date=parsedate_to_datetime(headers.get("Date", "")),
                labels=",".join(message.get("labelIds", [])),
                body=message.get("snippet", ""),
            )

            test_db_session.add(email)
            test_db_session.commit()
            processed_count += 1
            print(f"Successfully stored message from {email.received_date}")

        except Exception as e:
            print(f"Error processing message {msg_id}: {str(e)}")
            continue

    print(f"\nProcessed {processed_count} emails for date testing")
    assert processed_count > 0, "Should process at least one email for date testing"

    # Test date filtering in database
    print("\nTesting database date queries...")

    # Query emails from last week
    week_ago = datetime.now() - timedelta(days=7)
    recent_emails = (
        test_db_session.query(Email).filter(Email.received_date >= week_ago).all()
    )
    print(f"Found {len(recent_emails)} emails from last 7 days")
    assert len(recent_emails) > 0

    # Query emails from last 24 hours
    day_ago = datetime.now() - timedelta(days=1)
    very_recent = (
        test_db_session.query(Email).filter(Email.received_date >= day_ago).all()
    )
    print(f"Found {len(very_recent)} emails from last 24 hours")

    # Verify date ordering
    assert all(
        email.received_date >= week_ago for email in recent_emails
    ), "All emails should be from within the last week"


def test_email_counting(gmail_api, test_db_session):
    """Test email counting functionality."""
    # First, add some test emails
    start_date = datetime.now() - timedelta(days=7)
    messages = fetch_emails(gmail_api.service, start_date=start_date)

    for msg_id in [m["id"] for m in messages[: EMAIL_CONFIG["BATCH_SIZE"]]]:
        message = (
            gmail_api.service.users().messages().get(userId="me", id=msg_id).execute()
        )
        headers = {
            header["name"]: header["value"] for header in message["payload"]["headers"]
        }

        email = Email(
            id=message["id"],
            threadId=message["threadId"],
            subject=headers.get("Subject", "[No Subject]"),
            from_=headers.get("From", "[No Sender]"),
            to=headers.get("To", "[No Recipient]"),
            received_date=parsedate_to_datetime(headers.get("Date", "")),
            labels=",".join(message.get("labelIds", [])),
            body=message.get("snippet", ""),
        )
        test_db_session.add(email)

    test_db_session.commit()

    # Count total emails
    total_count = test_db_session.query(Email).count()
    print(f"\nTotal emails in database: {total_count}")
    assert total_count > 0

    # Count emails by label
    for label in ["INBOX", "SENT", "IMPORTANT"]:
        label_count = (
            test_db_session.query(Email).filter(Email.labels.like(f"%{label}%")).count()
        )
        print(f"Emails with {label} label: {label_count}")

    # Count emails by date range
    recent_count = (
        test_db_session.query(Email)
        .filter(Email.received_date >= datetime.now() - timedelta(days=1))
        .count()
    )
    print(f"Emails received in last 24 hours: {recent_count}")

    # Verify counts are consistent
    assert recent_count <= total_count


def test_database_session_management():
    """Test database session management in real application context."""
    from src.app_get_mail import get_email_session, init_database

    # Test session context manager
    with get_email_session() as session:
        init_database(session)
        assert session.bind is not None
        # Try a simple query
        result = session.query(Email).first()
        assert isinstance(result, Email) or result is None
