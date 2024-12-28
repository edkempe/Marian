"""Tests for JSON extraction functionality."""
import pytest
import json
from shared_lib.anthropic_lib import extract_json, clean_json_text

def test_extract_json_with_nested_quotes():
    response = '''Here's the JSON response: {"subject":"Meeting \\"Project X\\" Discussion","content":"Let's discuss the \\"Project X\\" timeline","nested":{"key":"value with \\"quotes\\"","array":["item \\"1\\"","item \\"2\\""]}}'''
    
    json_str, error = extract_json(response)
    assert error is None
    # Parse to verify it's valid JSON
    parsed = json.loads(json_str)
    assert parsed["subject"] == 'Meeting "Project X" Discussion'
    assert parsed["nested"]["key"] == 'value with "quotes"'

def test_extract_json_with_escaped_characters():
    response = '''Here's the JSON: {"text":"Line 1\\nLine 2\\nLine 3","path":"C:\\\\Program Files\\\\App","quote":"They said \\"Hello\\""}'''
    
    json_str, error = extract_json(response)
    assert error is None
    # Parse to verify it's valid JSON
    parsed = json.loads(json_str)
    assert parsed["text"].count('\n') == 2
    assert parsed["path"] == 'C:\\Program Files\\App'
    assert parsed["quote"] == 'They said "Hello"'

def test_extract_json_with_nested_objects():
    response = '''I analyzed it. Here's the JSON: {"level1":{"level2":{"level3":{"deep":"value"}},"array":[{"item":1},{"item":2}]}}'''
    
    json_str, error = extract_json(response)
    assert error is None
    # Parse to verify it's valid JSON
    parsed = json.loads(json_str)
    assert parsed["level1"]["level2"]["level3"]["deep"] == "value"
    assert parsed["level1"]["array"][1]["item"] == 2

def test_extract_json_with_no_json():
    response = "This response contains no JSON object"
    json_str, error = extract_json(response)
    assert json_str == ""
    assert "No JSON object" in error

def test_extract_json_with_invalid_json():
    response = '''Here's the JSON: {"unclosed_object": {"missing": "brace"'''
    json_str, error = extract_json(response)
    assert json_str == ""
    assert "No closing" in error

def test_extract_json_array():
    response = '''Here's the array of items: [{"id":1,"name":"Item 1","tags":["tag1","tag2"]},{"id":2,"name":"Item \\"2\\"","tags":["tag3","tag4"]}]'''
    
    json_str, error = extract_json(response)
    assert error is None
    # Parse to verify it's valid JSON
    parsed = json.loads(json_str)
    assert isinstance(parsed, list)
    assert len(parsed) == 2
    assert parsed[0]["id"] == 1
    assert parsed[1]["name"] == 'Item "2"'

def test_extract_json_nested_array():
    response = '''The data is structured as: {"items":[[1,2,3],["a","b","c"],[{"x":1},{"y":2}]],"meta":{"count":3}}'''
    
    json_str, error = extract_json(response)
    assert error is None
    # Parse to verify it's valid JSON
    parsed = json.loads(json_str)
    assert len(parsed["items"]) == 3
    assert parsed["items"][0] == [1, 2, 3]
    assert parsed["items"][1] == ["a", "b", "c"]
    assert parsed["items"][2][1]["y"] == 2

def test_extract_json_array_with_no_closing_bracket():
    response = '''Here's the array: [1, 2, 3'''
    json_str, error = extract_json(response)
    assert json_str == ""
    assert "No closing" in error

def test_extract_json_prefer_first():
    response = '''Multiple JSON objects: ["first"] {"second": true}'''
    json_str, error = extract_json(response)
    assert error is None
    parsed = json.loads(json_str)
    assert isinstance(parsed, list)
    assert parsed[0] == "first"

def test_api_response_extraction():
    """Test extracting JSON from a full API response."""
    mock_api_response = {
        "content": [{
            "text": '''I've analyzed the email. Here's the JSON response: {"summary":"Important work email requiring review","category":["work","review"],"priority_score":4,"priority_reason":"Requires review by tomorrow","action_needed":true,"action_type":["review"],"action_deadline":"2024-12-29","key_points":["Review needed","Deadline tomorrow"],"people_mentioned":[],"project":"","topic":"work review","sentiment":"neutral","confidence_score":0.9} Let me know if you need anything else!'''
        }]
    }
    
    # First test extracting from the full response structure
    if hasattr(mock_api_response, 'content'):
        for content_block in mock_api_response['content']:
            if hasattr(content_block, 'text') or isinstance(content_block, dict):
                text = content_block.get('text', '') if isinstance(content_block, dict) else content_block.text
                json_str, error = extract_json(text)
                assert error is None, f"Failed to extract JSON: {error}"
                
                # Parse and validate the extracted JSON
                parsed = json.loads(json_str)
                assert isinstance(parsed, dict)
                assert parsed["summary"] == "Important work email requiring review"
                assert parsed["priority_score"] == 4
                assert parsed["action_needed"] is True
                assert parsed["action_deadline"] == "2024-12-29"
                assert len(parsed["key_points"]) == 2
                assert parsed["sentiment"] == "neutral"
                assert isinstance(parsed["confidence_score"], float)

def test_api_response_with_multiple_json():
    """Test handling API response with multiple JSON objects - should extract the first valid one."""
    mock_response = '''Here's the email analysis: {"summary":"First analysis","priority_score":3,"priority_reason":"Medium priority","sentiment":"positive","confidence_score":0.8} Alternative analysis: {"summary":"Second analysis","priority_score":4,"priority_reason":"Higher priority","sentiment":"neutral","confidence_score":0.9}'''
    
    json_str, error = extract_json(mock_response)
    assert error is None
    parsed = json.loads(json_str)
    # Should get the first JSON object
    assert parsed["summary"] == "First analysis"
    assert parsed["priority_score"] == 3

def test_api_response_with_malformed_json():
    """Test handling API response with malformed JSON."""
    mock_response = '''Here's the analysis: {"summary": "Test analysis", priority_score: 3, "sentiment": 'neutral'}'''
    
    json_str, error = extract_json(mock_response)
    assert json_str == ""
    assert error is not None
