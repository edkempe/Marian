"""Test Gmail label model and schema."""

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from models.base import Base
from models.gmail_label import GmailLabel, email_labels
from models.email import EmailMessage
from config.settings.label import (
    label_settings,
    LabelType,
    MessageListVisibility,
    LabelListVisibility
)
from tests.factories import GmailLabelFactory, EmailFactory


@pytest.fixture(scope="function")
def test_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create test database session."""
    session = Session(bind=test_engine)
    yield session
    session.close()


def test_label_schema(test_session):
    """Test Gmail label table schema."""
    # Create test label
    label = GmailLabelFactory()
    test_session.add(label)
    test_session.commit()

    # Verify label was created
    saved_label = test_session.query(GmailLabel).first()
    assert saved_label is not None
    assert saved_label.id == label.id
    assert saved_label.name == label.name
    assert saved_label.type in [LabelType.SYSTEM.value, LabelType.USER.value]
    assert saved_label.message_list_visibility in [v.value for v in MessageListVisibility]
    assert saved_label.label_list_visibility in [v.value for v in LabelListVisibility]

    # Color fields should only be set for user labels
    if saved_label.type == LabelType.USER.value:
        assert saved_label.color is not None
        assert saved_label.background_color is not None
        assert saved_label.text_color is not None
    else:
        assert saved_label.color is None
        assert saved_label.background_color is None
        assert saved_label.text_color is None

    # Verify counters are initialized to 0
    assert saved_label.messages_total == 0
    assert saved_label.messages_unread == 0
    assert saved_label.threads_total == 0
    assert saved_label.threads_unread == 0


def test_label_email_relationship(test_session):
    """Test relationship between labels and emails."""
    # Create test data
    label = GmailLabelFactory()
    email = EmailFactory()
    
    # Associate email with label
    email.labels.append(label)
    
    test_session.add_all([label, email])
    test_session.commit()

    # Verify relationship
    saved_label = test_session.query(GmailLabel).first()
    assert len(saved_label.emails) == 1
    assert saved_label.emails[0].id == email.id

    saved_email = test_session.query(EmailMessage).first()
    assert len(saved_email.labels) == 1
    assert saved_email.labels[0].id == label.id


def test_label_constraints(test_session):
    """Test label model constraints."""
    # Test unique name constraint
    label1 = GmailLabelFactory(name="test_label")
    test_session.add(label1)
    test_session.commit()

    label2 = GmailLabelFactory(name="test_label")
    test_session.add(label2)
    with pytest.raises(Exception) as exc_info:  # SQLite doesn't provide specific integrity errors
        test_session.commit()
    assert "UNIQUE constraint failed" in str(exc_info.value)
    test_session.rollback()

    # Test required fields
    with pytest.raises(ValueError) as exc_info:
        label = GmailLabelFactory(name=None)
        test_session.add(label)
        test_session.commit()
    assert "Label name cannot be None" in str(exc_info.value)
    test_session.rollback()

    # Test field length constraints
    with pytest.raises(ValueError) as exc_info:
        GmailLabelFactory(
            name="x" * (label_settings.NAME_MAX_LENGTH + 1)
        )
    assert "exceeds maximum length" in str(exc_info.value)

    # Test enum value constraints
    with pytest.raises(ValueError) as exc_info:
        GmailLabelFactory(
            type="invalid_type"
        )
    assert "Invalid label type" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        GmailLabelFactory(
            message_list_visibility="invalid_visibility"
        )
    assert "Invalid message list visibility" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        GmailLabelFactory(
            label_list_visibility="invalid_visibility"
        )
    assert "Invalid label list visibility" in str(exc_info.value)
