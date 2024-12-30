"""Tests for core email processing functionality."""

from datetime import datetime

import pytest

from app_get_mail import process_email
from models.email import Email


def test_store_email(test_db_session):
    """Test storing an email in the database."""
    # Simple test email data
    email_data = {
        "id": "test123",
        "thread_id": "thread123",
        "subject": "Test Email",
        "from_address": "sender@example.com",
        "to_address": "me@example.com",
        "received_date": datetime.utcnow(),
        "content": "Hello World",
        "labels": "INBOX,IMPORTANT",
    }

    # Create and store email
    email = Email(**email_data)
    test_db_session.add(email)
    test_db_session.commit()

    # Verify storage
    stored = test_db_session.query(Email).filter_by(id="test123").first()
    assert stored is not None
    assert stored.subject == "Test Email"
    assert stored.from_address == "sender@example.com"
    assert "INBOX" in stored.labels
    assert "IMPORTANT" in stored.labels


def test_store_email_missing_fields(test_db_session):
    """Test storing an email with missing fields."""
    email_data = {
        "id": "test456",
        "thread_id": "thread456",
        "subject": "Incomplete Email",
        # Missing other fields
    }

    # Create and store email
    email = Email(**email_data)
    test_db_session.add(email)
    test_db_session.commit()

    # Verify storage
    stored = test_db_session.query(Email).filter_by(id="test456").first()
    assert stored is not None
    assert stored.subject == "Incomplete Email"
    assert stored.from_address is None
    assert stored.to_address is None


def test_email_labels(test_db_session):
    """Test email label handling."""
    # Email with multiple labels
    email = Email(
        id="test789",
        thread_id="thread789",
        subject="Labeled Email",
        labels="INBOX,IMPORTANT,STARRED",
    )
    test_db_session.add(email)
    test_db_session.commit()

    # Verify labels
    stored = test_db_session.query(Email).filter_by(id="test789").first()
    labels = stored.labels.split(",")
    assert len(labels) == 3
    assert "INBOX" in labels
    assert "IMPORTANT" in labels
    assert "STARRED" in labels
