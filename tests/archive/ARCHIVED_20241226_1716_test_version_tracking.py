#!/usr/bin/env python3
"""Tests for version tracking functionality."""
import os
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from models.email import Email
from models.email_analysis import EmailAnalysis
from shared_lib.database_session_util import get_email_session


def test_prompt_version_tracking():
    """Test that prompt versions are properly tracked in analysis results."""
    # Create a test email
    session = get_email_session()
    test_email = Email(
        message_id="test_msg_001",
        subject="Test Email",
        content="This is a test email for version tracking",
        received_date=datetime.utcnow(),
        processed=False,
    )
    session.add(test_email)
    session.commit()

    # Create analysis with specific prompt version
    analysis = EmailAnalysis(
        email_id=test_email.id,
        summary="Test summary",
        key_points=["Point 1", "Point 2"],
        action_items=["Action 1"],
        priority_score=5,
        category="test",
        prompt_version="1.0",  # Explicit version tracking
    )
    session.add(analysis)
    session.commit()

    # Verify the analysis was stored with correct version
    stored_analysis = (
        session.query(EmailAnalysis).filter_by(email_id=test_email.id).first()
    )
    assert stored_analysis is not None
    assert stored_analysis.prompt_version == "1.0"

    # Clean up
    session.delete(analysis)
    session.delete(test_email)
    session.commit()


if __name__ == "__main__":
    pytest.main([__file__])
