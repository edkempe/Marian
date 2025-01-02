"""Test models with configuration-based schema."""

import os
import tempfile
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel
from shared_lib.config_loader import get_schema_config
from config.test_settings import test_settings
import yaml
from pathlib import Path
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


@pytest.fixture(scope="function")
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
                    "analysis_id": {"size": 100, "type": "string", "description": "Analysis ID"},
                    "email_id": {"size": 100, "type": "string", "description": "Email ID"},
                    "summary": {"size": 1000, "type": "text", "description": "Summary"},
                    "sentiment": {"size": 50, "type": "string", "description": "Sentiment"},
                    "categories": {"size": 200, "type": "text", "description": "Categories"},
                    "key_points": {"size": 200, "type": "text", "description": "Key Points"},
                    "action_items": {"size": 200, "type": "text", "description": "Action Items"},
                    "priority_score": {"size": 10, "type": "integer", "description": "Priority Score"},
                    "confidence_score": {"size": 10, "type": "float", "description": "Confidence Score"},
                    "model_version": {"size": 100, "type": "string", "description": "Model Version"},
                    "analysis_metadata": {"size": 200, "type": "text", "description": "Analysis Metadata"}
                },
                "defaults": {
                    "sentiment": "neutral",
                    "categories": "[]",
                    "key_points": "[]",
                    "action_items": "[]",
                    "priority_score": 0,
                    "confidence_score": 0.0,
                    "model_version": "",
                    "analysis_metadata": "{}"
                },
                "validation": {
                    "valid_sentiments": ["positive", "negative", "neutral", "mixed"],
                    "max_summary_length": 1000,
                    "max_categories_length": 200,
                    "max_key_points_length": 200,
                    "max_action_items_length": 200,
                    "min_priority_score": 0,
                    "max_priority_score": 5,
                    "min_confidence_score": 0.0,
                    "max_confidence_score": 1.0,
                    "valid_model_versions": ["claude-3-opus-20240229"]
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


@pytest.fixture(scope="function")
def test_engine():
    """Create test database engine."""
    engine = create_engine(test_settings.DATABASE_URLS["default"])
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create test database session."""
    session = Session(test_engine)
    yield session
    session.close()


def test_email_model(test_config, test_session):
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
    
    email = EmailMessage.from_api_response(api_response)
    test_session.add(email)
    test_session.commit()
    
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


def test_email_analysis_model(test_config, test_session):
    """Test EmailAnalysis model with configuration."""
    # Create parent email
    email = EmailMessage(
        id="msg123",
        thread_id="thread123",
        subject="Test Email",
        received_at=datetime.now(timezone.utc)
    )
    test_session.add(email)
    
    # Test creation from Anthropic API response
    api_response = {
        "id": "analysis_123",
        "email_id": "msg123",
        "summary": "This is a test email about work.",
        "sentiment": "positive",
        "categories": ["work", "important"],
        "key_points": ["Point 1", "Point 2"],
        "action_items": [
            {
                "description": "Follow up with team",
                "due_date": "2025-01-02T12:00:00Z",
                "priority": "high",
                "assignee": "john@example.com"
            }
        ],
        "priority_score": 4,
        "confidence_score": 0.95,
        "model_version": "claude-3-opus-20240229",
        "analysis_metadata": {
            "source": "email",
            "version": "1.0",
            "processing_time": 0.5
        }
    }
    
    analysis = EmailAnalysis.from_api_response(api_response)
    test_session.add(analysis)
    test_session.commit()
    
    # Test field values
    assert analysis.analysis_id == "analysis_123"
    assert analysis.email_id == email.id
    assert analysis.summary == "This is a test email about work."
    assert analysis.sentiment == "positive"
    assert analysis.categories == ["work", "important"]
    assert analysis.key_points == ["Point 1", "Point 2"]
    assert len(analysis.action_items) == 1
    assert analysis.action_items[0]["description"] == "Follow up with team"
    assert analysis.action_items[0]["priority"] == "high"
    assert analysis.priority_score == 4
    assert analysis.confidence_score == 0.95
    assert analysis.model_version == "claude-3-opus-20240229"
    assert analysis.analysis_metadata["source"] == "email"
    assert analysis.analysis_metadata["version"] == "1.0"
    
    # Test relationship
    assert analysis.email == email
    assert email.analysis == analysis
    
    # Test response model
    response = EmailAnalysisResponse.from_model(analysis)
    assert response.analysis_id == analysis.analysis_id
    assert response.email_id == str(analysis.email_id)
    assert response.summary == analysis.summary
    assert response.sentiment == analysis.sentiment
    assert response.categories == analysis.categories
    assert response.key_points == analysis.key_points
    assert response.action_items == analysis.action_items
    assert response.priority_score == analysis.priority_score
    assert response.confidence_score == analysis.confidence_score
    assert response.model_version == analysis.model_version
    assert response.analysis_metadata == analysis.analysis_metadata


def test_email_analysis_validation(test_config, test_session):
    """Test EmailAnalysis validation rules."""
    email = EmailMessage(
        id="msg123",
        thread_id="thread123",
        subject="Test Email",
        received_at=datetime.now(timezone.utc)
    )
    test_session.add(email)
    
    # Test invalid sentiment
    with pytest.raises(ValueError):
        EmailAnalysis(
            analysis_id="analysis_123",
            email_id=email.id,
            summary="Test summary",
            sentiment="invalid"
        )
    
    # Test invalid priority score
    with pytest.raises(ValueError):
        EmailAnalysis(
            analysis_id="analysis_123",
            email_id=email.id,
            summary="Test summary",
            priority_score=6
        )
    
    # Test invalid confidence score
    with pytest.raises(ValueError):
        EmailAnalysis(
            analysis_id="analysis_123",
            email_id=email.id,
            summary="Test summary",
            confidence_score=1.5
        )
    
    # Test invalid model version
    with pytest.raises(ValueError):
        EmailAnalysis(
            analysis_id="analysis_123",
            email_id=email.id,
            summary="Test summary",
            model_version="invalid-model"
        )


def test_gmail_label_model(test_config, test_session):
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
    test_session.add(label)
    test_session.commit()
    
    # Test field values
    assert label.id == "Label_123"
    assert label.name == "Important Work"
    assert label.type == "user"
    assert label.message_list_visibility == "show"
    assert label.label_list_visibility == "labelShow"
    assert label.is_system is False
    
    # Test relationships
    assert len(label.emails) == 0


def test_model_relationships(test_config, test_session):
    """Test relationships between models."""
    # Create email
    email = EmailMessage(
        id="msg123",
        thread_id="thread123",
        subject="Test Email",
        received_at=datetime.now(timezone.utc)
    )
    test_session.add(email)
    
    # Create analysis
    analysis = EmailAnalysis(
        analysis_id="analysis_123",
        email_id=email.id,
        summary="Test summary",
        sentiment="positive",
        categories=["work", "important"],
        key_points=["Point 1", "Point 2"],
        action_items=[
            {
                "description": "Follow up with team",
                "due_date": "2025-01-02T12:00:00Z",
                "priority": "high",
                "assignee": "john@example.com"
            }
        ],
        priority_score=4,
        confidence_score=0.95,
        model_version="claude-3-opus-20240229",
        analysis_metadata={
            "source": "email",
            "version": "1.0",
            "processing_time": 0.5
        }
    )
    test_session.add(analysis)
    
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
    test_session.add_all([label1, label2])
    
    # Add labels to email
    email.labels.extend([label1, label2])
    test_session.commit()
    
    # Test relationships
    assert email.analysis == analysis
    assert analysis.email == email
    assert len(email.labels) == 2
    assert email in label1.emails
    assert email in label2.emails
