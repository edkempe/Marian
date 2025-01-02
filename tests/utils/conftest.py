"""Pytest configuration for utility tests."""

import pytest
from datetime import datetime

@pytest.fixture
def sample_datetime():
    """Return a fixed datetime for testing."""
    return datetime(2024, 12, 31, 9, 48, 0)

@pytest.fixture
def sample_text():
    """Return a sample text with email addresses."""
    return """
    Hello, this is a test email.
    Contact us at support@example.com or sales@example.com.
    Thanks!
    """
