"""Test models with configuration-based schema."""

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, Email, EmailAnalysis, GmailLabel
from shared_lib.config_loader import get_schema_config


@pytest.fixture
def test_config():
    """Create a test configuration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "schema.test.yaml"
        config_data = {
            "email": {
                "columns": {
                    "id": {"size": 100, "type": "string", "description": "Email ID"},
                    "thread_id": {"size": 100, "type": "string", "description": "Thread ID"},
                    "message_id": {"size": 100, "type": "string", "description": "Message ID"},
                    "subject": {"size": 200, "type": "string", "description": "Subject"},
                    "snippet": {"size": 500, "type": "string", "description": "Snippet"},
                    "sender": {"size": 100, "type": "string", "description": "Sender"},
                    "recipient": {"size": 100, "type": "string", "description": "Recipient"},
                    "cc": {"size": 200, "type": "string", "description": "CC"},
                    "bcc": {"size": 200, "type": "string", "description": "BCC"}
                },
                "defaults": {
                    "subject": "",
                    "has_attachments": False,
                    "is_read": False,
                    "is_important": False,
                    "api_response": "{}"
                },
                "validation": {
                    "max_subject_length": 200,
                    "max_snippet_length": 500
                }
            },
            "analysis": {
                "columns": {
                    "sentiment": {"size": 50, "type": "string", "description": "Sentiment"},
                    "category": {"size": 100, "type": "string", "description": "Category"},
                    "summary": {"size": 1000, "type": "string", "description": "Summary"}
                },
                "defaults": {
                    "sentiment": "neutral",
                    "category": "uncategorized"
                },
                "validation": {
                    "valid_sentiments": ["positive", "negative", "neutral", "mixed"],
                    "max_summary_length": 1000
                }
            },
            "label": {
                "columns": {
                    "id": {"size": 100, "type": "string", "description": "Label ID"},
                    "name": {"size": 100, "type": "string", "description": "Label name"},
                    "type": {"size": 50, "type": "string", "description": "Label type"},
                    "visibility": {"size": 50, "type": "string", "description": "Visibility"}
                },
                "defaults": {
                    "type": "user",
                    "is_system": False
                },
                "validation": {
                    "valid_types": ["system", "user"],
                    "max_name_length": 100
                }
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        os.environ["ENV"] = "test"
        os.environ["SCHEMA_CONFIG_PATH"] = str(config_path)
        
        yield get_schema_config()


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


def test_email_model(test_config, db_session):
    """Test Email model with configuration."""
    # Test creation from API response
    api_response = {
        "id": "msg123",
        "threadId": "thread123",
        "messageId": "message123",
        "subject": "Test Email",
        "body": "Test body",
        "snippet": "Test snippet",
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "cc": "cc@example.com",
        "bcc": "bcc@example.com",
        "hasAttachments": True,
        "isRead": True,
        "isImportant": False,
        "receivedAt": "2024-12-29T22:00:00+00:00"
    }
    
    email = Email.from_api_response(api_response)
    db_session.add(email)
    db_session.commit()
    
    # Test field values
    assert email.id == "msg123"
    assert email.thread_id == "thread123"
    assert email.subject == "Test Email"
    assert email.sender == "sender@example.com"
    assert email.has_attachments is True
    assert email.is_read is True
    assert email.is_important is False
    
    # Test relationships
    assert email.analysis is None
    assert len(email.labels) == 0


def test_email_analysis_model(test_config, db_session):
    """Test EmailAnalysis model with configuration."""
    # Create parent email
    email = Email(
        id="msg123",
        thread_id="thread123",
        subject="Test Email",
        received_at=datetime.now(timezone.utc)
    )
    db_session.add(email)
    
    # Test creation from API response
    api_response = {
        "sentiment": "positive",
        "category": "work",
        "summary": "This is a test email about work."
    }
    
    analysis = EmailAnalysis.from_api_response(email.id, api_response)
    db_session.add(analysis)
    db_session.commit()
    
    # Test field values
    assert analysis.email_id == "msg123"
    assert analysis.sentiment == "positive"
    assert analysis.category == "work"
    assert analysis.summary == "This is a test email about work."
    
    # Test relationship
    assert analysis.email == email
    assert email.analysis == analysis


def test_gmail_label_model(test_config, db_session):
    """Test GmailLabel model with configuration."""
    # Test creation from API response
    api_response = {
        "id": "Label_123",
        "name": "Important Work",
        "type": "user",
        "messageListVisibility": "show",
        "labelListVisibility": "labelShow"
    }
    
    label = GmailLabel.from_api_response(api_response)
    db_session.add(label)
    db_session.commit()
    
    # Test field values
    assert label.id == "Label_123"
    assert label.name == "Important Work"
    assert label.type == "user"
    assert label.message_list_visibility == "show"
    assert label.label_list_visibility == "labelShow"
    assert label.is_system is False
    
    # Test relationships
    assert len(label.emails) == 0


def test_model_relationships(test_config, db_session):
    """Test relationships between models."""
    # Create email
    email = Email(
        id="msg123",
        thread_id="thread123",
        subject="Test Email",
        received_at=datetime.now(timezone.utc)
    )
    db_session.add(email)
    
    # Create analysis
    analysis = EmailAnalysis(
        email_id=email.id,
        sentiment="positive",
        category="work",
        summary="Test summary"
    )
    db_session.add(analysis)
    
    # Create labels
    label1 = GmailLabel(
        id="Label_1",
        name="Work",
        type="user"
    )
    label2 = GmailLabel(
        id="Label_2",
        name="Important",
        type="user"
    )
    db_session.add_all([label1, label2])
    
    # Add labels to email
    email.labels.extend([label1, label2])
    db_session.commit()
    
    # Test relationships
    assert email.analysis == analysis
    assert analysis.email == email
    assert len(email.labels) == 2
    assert email in label1.emails
    assert email in label2.emails
