"""Unit tests for pure functions that don't require external dependencies."""
import pytest
from datetime import datetime
import json
from shared_lib.anthropic_lib import clean_json_text, extract_json, parse_claude_response
from models.email_analysis import EmailAnalysisResponse

def test_clean_json_text():
    """Test cleaning text that contains JSON."""
    test_cases = [
        (
            'Here is the JSON response: {"key": "value"}',
            '{"key": "value"}'
        ),
        (
            'Based on the analysis, here\'s the JSON:\n{"key": "value"}\nHope this helps!',
            '{"key": "value"}'
        ),
        (
            '{"key": "value"}',
            '{"key": "value"}'
        ),
        (
            'No JSON here',
            'No JSON here'
        )
    ]
    
    for input_text, expected in test_cases:
        result = clean_json_text(input_text)
        assert result == expected

def test_extract_json():
    """Test extracting JSON from text with various formats."""
    test_cases = [
        # Basic JSON object
        (
            '{"key": "value"}',
            '{"key": "value"}',
            None
        ),
        # JSON with prefix
        (
            'Here is JSON: {"key": "value"}',
            '{"key": "value"}',
            None
        ),
        # JSON with suffix
        (
            '{"key": "value"} Hope this helps!',
            '{"key": "value"}',
            None
        ),
        # JSON array
        (
            '[1, 2, 3]',
            '[1, 2, 3]',
            None
        ),
        # No JSON
        (
            'No JSON here',
            '',
            'No JSON object or array found in response'
        ),
        # Invalid JSON
        (
            '{"key": value}',  # Missing quotes
            '',
            'Invalid JSON'
        )
    ]
    
    for input_text, expected_json, expected_error in test_cases:
        json_str, error = extract_json(input_text)
        assert json_str == expected_json
        if expected_error:
            assert error is not None
            assert expected_error in error
        else:
            assert error is None

def test_email_analysis_response_validation():
    """Test EmailAnalysisResponse model validation."""
    # Valid response
    valid_data = {
        "summary": "Test email about project review.",
        "category": ["work"],
        "priority_score": 3,
        "priority_reason": "Regular project update",
        "action_needed": True,
        "action_type": ["review"],
        "action_deadline": "2024-12-31",
        "key_points": ["Review status", "Update timeline"],
        "people_mentioned": ["John", "Jane"],
        "project": "Test Project",
        "topic": "Project Review",
        "sentiment": "neutral",
        "confidence_score": 0.9
    }
    
    response = EmailAnalysisResponse(**valid_data)
    assert response.summary == valid_data["summary"]
    assert response.category == valid_data["category"]
    assert response.priority_score == valid_data["priority_score"]
    
    # Test invalid priority score
    with pytest.raises(ValueError):
        invalid_data = valid_data.copy()
        invalid_data["priority_score"] = 6  # Must be 1-5
        EmailAnalysisResponse(**invalid_data)
    
    # Test invalid sentiment
    with pytest.raises(ValueError):
        invalid_data = valid_data.copy()
        invalid_data["sentiment"] = "happy"  # Must be positive/negative/neutral
        EmailAnalysisResponse(**invalid_data)
    
    # Test invalid confidence score
    with pytest.raises(ValueError):
        invalid_data = valid_data.copy()
        invalid_data["confidence_score"] = 1.5  # Must be 0-1
        EmailAnalysisResponse(**invalid_data)

def test_parse_claude_response():
    """Test parsing Claude API responses."""
    # Valid response
    valid_response = '''
    {
        "summary": "Test email",
        "category": ["work"],
        "priority_score": 3,
        "priority_reason": "Regular update",
        "action_needed": true,
        "action_type": ["review"],
        "action_deadline": "2024-12-31",
        "key_points": ["Point 1"],
        "people_mentioned": ["John"],
        "project": "Test",
        "topic": "Update",
        "sentiment": "neutral",
        "confidence_score": 0.9
    }
    '''
    
    result = parse_claude_response(valid_response)
    assert result is not None
    assert result["summary"] == "Test email"
    assert result["category"] == ["work"]
    
    # Invalid JSON
    invalid_response = "Not JSON"
    result = parse_claude_response(invalid_response)
    assert result is None
    
    # Missing required fields
    incomplete_response = '{"summary": "Test"}'
    result = parse_claude_response(incomplete_response)
    assert result is not None  # We don't validate fields here, that's done by EmailAnalysisResponse
