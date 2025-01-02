"""Tests for email utilities."""

import pytest
from utils.email_utils import (
    parse_email_address,
    normalize_email,
    extract_email_addresses
)

def test_parse_email_address():
    """Test email address parsing."""
    # Valid email
    assert parse_email_address("user@example.com") == ("user", "example.com")
    assert parse_email_address("first.last@sub.example.com") == ("first.last", "sub.example.com")
    
    # Invalid emails
    assert parse_email_address("invalid-email") is None
    assert parse_email_address("@domain.com") is None
    assert parse_email_address("user@") is None

def test_normalize_email():
    """Test email normalization."""
    assert normalize_email(" User@Example.COM ") == "user@example.com"
    assert normalize_email("first.last@example.com") == "first.last@example.com"
    assert normalize_email("   spaces@example.com   ") == "spaces@example.com"

def test_extract_email_addresses():
    """Test extracting email addresses from text."""
    text = """
    Contact us at support@example.com or sales@example.com.
    Invalid emails: not.an.email, @incomplete.com
    More valid ones: user.name@sub.example.com, another@test.co.uk
    """
    
    expected = [
        "support@example.com",
        "sales@example.com",
        "user.name@sub.example.com",
        "another@test.co.uk"
    ]
    
    assert extract_email_addresses(text) == expected
