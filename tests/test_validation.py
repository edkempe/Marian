"""Test validation functionality."""

import pytest
from datetime import datetime, timezone

from models.email import EmailMessage
from models.email_analysis import EmailAnalysis, EmailAnalysisResponse
from models.validators.api_schema import api_validator
from shared_lib.constants.validation import VALIDATION_ERRORS, RULES
from shared_lib.schema_constants import COLUMN_SIZES, VALUE_RANGES, ENUMS


def test_email_message_validation(sample_emails):
    """Test EmailMessage validation."""
    # Test valid email
    email = sample_emails[0]
    assert email.id == "msg1"
    assert email.threadId == "thread1"
    assert "INBOX" in email.labelIds
    
    # Test invalid message ID
    with pytest.raises(ValueError, match=VALIDATION_ERRORS.INVALID_MESSAGE_ID):
        EmailMessage(
            id="invalid!id",
            threadId="thread1",
            labelIds=["INBOX"],
            snippet="Test",
            historyId="12345",
            internalDate=datetime.now(timezone.utc),
            sizeEstimate=1024,
            payload={"mimeType": "text/plain"}
        )
    
    # Test invalid thread ID
    with pytest.raises(ValueError, match=VALIDATION_ERRORS.INVALID_THREAD_ID):
        EmailMessage(
            id="msg1",
            threadId="invalid!thread",
            labelIds=["INBOX"],
            snippet="Test",
            historyId="12345",
            internalDate=datetime.now(timezone.utc),
            sizeEstimate=1024,
            payload={"mimeType": "text/plain"}
        )
    
    # Test too many labels
    with pytest.raises(ValueError, match=VALIDATION_ERRORS.TOO_MANY_LABELS):
        EmailMessage(
            id="msg1",
            threadId="thread1",
            labelIds=["LABEL_" + str(i) for i in range(RULES.MAX_LABEL_IDS + 1)],
            snippet="Test",
            historyId="12345",
            internalDate=datetime.now(timezone.utc),
            sizeEstimate=1024,
            payload={"mimeType": "text/plain"}
        )


def test_email_analysis_validation(sample_analysis):
    """Test EmailAnalysis validation."""
    # Test valid analysis
    analysis = sample_analysis[0]
    assert analysis.id == "analysis_abc123"
    assert analysis.email_id == "msg1"
    assert analysis.sentiment == "positive"
    
    # Test invalid analysis ID
    with pytest.raises(ValueError, match=VALIDATION_ERRORS.INVALID_ANALYSIS_ID):
        EmailAnalysis(
            id="invalid!id",
            email_id="msg1",
            summary="Test",
            sentiment="positive",
            priority_score=3,
            confidence_score=0.9
        )
    
    # Test invalid priority score
    with pytest.raises(ValueError, match=VALIDATION_ERRORS.INVALID_PRIORITY_SCORE):
        EmailAnalysis(
            id="analysis_test",
            email_id="msg1",
            summary="Test",
            sentiment="positive",
            priority_score=10,  # Out of range
            confidence_score=0.9
        )
    
    # Test invalid confidence score
    with pytest.raises(ValueError, match=VALIDATION_ERRORS.INVALID_CONFIDENCE_SCORE):
        EmailAnalysis(
            id="analysis_test",
            email_id="msg1",
            summary="Test",
            sentiment="positive",
            priority_score=3,
            confidence_score=2.0  # Out of range
        )
    
    # Test invalid sentiment
    with pytest.raises(ValueError, match=VALIDATION_ERRORS.INVALID_SENTIMENT):
        EmailAnalysis(
            id="analysis_test",
            email_id="msg1",
            summary="Test",
            sentiment="invalid_sentiment",
            priority_score=3,
            confidence_score=0.9
        )
    
    # Test too many categories
    with pytest.raises(ValueError, match=VALIDATION_ERRORS.TOO_MANY_CATEGORIES):
        EmailAnalysis(
            id="analysis_test",
            email_id="msg1",
            summary="Test",
            sentiment="positive",
            categories=["category_" + str(i) for i in range(RULES.MAX_CATEGORIES + 1)],
            priority_score=3,
            confidence_score=0.9
        )
    
    # Test too many key points
    with pytest.raises(ValueError, match=VALIDATION_ERRORS.TOO_MANY_KEY_POINTS):
        EmailAnalysis(
            id="analysis_test",
            email_id="msg1",
            summary="Test",
            sentiment="positive",
            key_points=["point_" + str(i) for i in range(RULES.MAX_KEY_POINTS + 1)],
            priority_score=3,
            confidence_score=0.9
        )
    
    # Test too many action items
    with pytest.raises(ValueError, match=VALIDATION_ERRORS.TOO_MANY_ACTION_ITEMS):
        EmailAnalysis(
            id="analysis_test",
            email_id="msg1",
            summary="Test",
            sentiment="positive",
            action_items=[{"description": f"task_{i}"} for i in range(RULES.MAX_ACTION_ITEMS + 1)],
            priority_score=3,
            confidence_score=0.9
        )


def test_email_analysis_response():
    """Test EmailAnalysisResponse model."""
    now = datetime.now(timezone.utc)
    
    # Create analysis instance
    analysis = EmailAnalysis(
        id="analysis_test",
        email_id="msg1",
        summary="Test summary",
        sentiment="positive",
        categories=["test"],
        key_points=["key point"],
        action_items=[{"description": "task"}],
        priority_score=3,
        confidence_score=0.9,
        model_version="claude-3-opus-20240229",
        analysis_metadata={"test": "data"},
        created_at=now,
        updated_at=now
    )
    
    # Convert to response
    response = EmailAnalysisResponse.from_model(analysis)
    
    # Verify fields
    assert response.analysis_id == analysis.id
    assert response.email_id == analysis.email_id
    assert response.summary == analysis.summary
    assert response.sentiment == analysis.sentiment
    assert response.categories == analysis.categories
    assert response.key_points == analysis.key_points
    assert response.action_items == analysis.action_items
    assert response.priority_score == analysis.priority_score
    assert response.confidence_score == analysis.confidence_score
    assert response.model_version == analysis.model_version
    assert response.analysis_metadata == analysis.analysis_metadata
    assert response.created_at == analysis.created_at
    assert response.updated_at == analysis.updated_at
