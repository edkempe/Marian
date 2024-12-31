"""Tests for date utilities."""

import pytest
from datetime import datetime
from utils.date_utils import format_iso_date, parse_iso_date

def test_format_iso_date():
    """Test ISO date formatting."""
    date = datetime(2024, 12, 31, 9, 48)
    assert format_iso_date(date) == "2024-12-31T09:48:00"

def test_parse_iso_date():
    """Test ISO date parsing."""
    # Test valid date
    date_str = "2024-12-31T09:48:00"
    result = parse_iso_date(date_str)
    assert isinstance(result, datetime)
    assert result.year == 2024
    assert result.month == 12
    assert result.day == 31
    
    # Test invalid date
    assert parse_iso_date("invalid-date") is None
