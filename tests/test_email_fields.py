"""Tests for new Email and GmailLabel fields."""

import pytest
from datetime import datetime, timezone
import json
from models.email import Email
from models.gmail_label import GmailLabel

def test_email_to_address(db_session, sample_emails):
    """Test to_address field in Email model."""
    session = db_session()
    email = sample_emails[0]
    
    # Add email to database
    session.add(email)
    session.commit()
    
    # Verify to_address was stored correctly
    stored_email = session.query(Email).filter_by(id=email.id).first()
    assert stored_email.to_address == "recipient1@example.com"

def test_email_api_response(db_session, sample_emails):
    """Test full_api_response field in Email model."""
    session = db_session()
    email = sample_emails[0]
    
    # Add email to database
    session.add(email)
    session.commit()
    
    # Verify API response was stored correctly
    stored_email = session.query(Email).filter_by(id=email.id).first()
    api_response = json.loads(stored_email.full_api_response)
    assert api_response["id"] == "msg1"
    assert api_response["threadId"] == "thread1"
    assert "INBOX" in api_response["labelIds"]

def test_gmail_label_lifecycle(db_session, sample_gmail_labels):
    """Test Gmail label lifecycle fields."""
    session = db_session()
    active_label = sample_gmail_labels[0]  # INBOX
    deleted_label = sample_gmail_labels[2]  # Custom Label
    
    # Add labels to database
    session.add(active_label)
    session.add(deleted_label)
    session.commit()
    
    # Verify active label
    stored_active = session.query(GmailLabel).filter_by(id=active_label.id).first()
    assert stored_active.is_active is True
    assert stored_active.deleted_at is None
    assert stored_active.first_seen_at is not None
    assert stored_active.last_seen_at is not None
    
    # Verify deleted label
    stored_deleted = session.query(GmailLabel).filter_by(id=deleted_label.id).first()
    assert stored_deleted.is_active is False
    assert stored_deleted.deleted_at is not None
    
    # Test last_seen_at update
    now = datetime.now(timezone.utc)
    stored_active.last_seen_at = now
    session.commit()
    
    refreshed_active = session.query(GmailLabel).filter_by(id=active_label.id).first()
    assert refreshed_active.last_seen_at == now

def test_label_soft_deletion(db_session, sample_gmail_labels):
    """Test soft deletion of Gmail labels."""
    session = db_session()
    label = sample_gmail_labels[0]  # INBOX
    
    # Add label to database
    session.add(label)
    session.commit()
    
    # Soft delete the label
    now = datetime.now(timezone.utc)
    label.is_active = False
    label.deleted_at = now
    session.commit()
    
    # Verify soft deletion
    stored_label = session.query(GmailLabel).filter_by(id=label.id).first()
    assert stored_label.is_active is False
    assert stored_label.deleted_at == now
    
    # Verify label still exists in database
    assert stored_label is not None
