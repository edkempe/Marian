"""Tests for JSON extraction functionality."""
import pytest
import json
from shared_lib.anthropic_lib import extract_json, clean_json_text

def test_extract_json_with_nested_quotes():
    response = '''Here's the JSON response: {
        "subject": "Meeting \"Project X\" Discussion",
        "content": "Let's discuss the \"Project X\" timeline",
        "nested": {
            "key": "value with \"quotes\"",
            "array": ["item \"1\"", "item \"2\""]
        }
    }'''
    
    json_str, error = extract_json(response)
    assert error is None
    # Parse to verify it's valid JSON
    parsed = json.loads(json_str)
    assert parsed["subject"] == 'Meeting "Project X" Discussion'
    assert parsed["nested"]["key"] == 'value with "quotes"'

def test_extract_json_with_escaped_characters():
    response = '''Here's the JSON: {
        "text": "Line 1\\nLine 2\\nLine 3",
        "path": "C:\\\\Program Files\\\\App",
        "quote": "They said \\"Hello\\""
    }'''
    
    json_str, error = extract_json(response)
    assert error is None
    # Parse to verify it's valid JSON
    parsed = json.loads(json_str)
    assert parsed["text"].count('\n') == 2
    assert parsed["path"] == 'C:\\Program Files\\App'
    assert parsed["quote"] == 'They said "Hello"'

def test_extract_json_with_nested_objects():
    response = '''I analyzed it. Here's the JSON: {
        "level1": {
            "level2": {
                "level3": {
                    "deep": "value"
                }
            },
            "array": [
                {"item": 1},
                {"item": 2}
            ]
        }
    }'''
    
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
    response = '''Here's the JSON: {
        "unclosed_object": {
        "missing": "brace"
    '''
    json_str, error = extract_json(response)
    assert json_str == ""
    assert "No closing" in error

def test_extract_json_array():
    response = '''Here's the array of items: [
        {
            "id": 1,
            "name": "Item 1",
            "tags": ["tag1", "tag2"]
        },
        {
            "id": 2,
            "name": "Item \"2\"",
            "tags": ["tag3", "tag4"]
        }
    ]'''
    
    json_str, error = extract_json(response)
    assert error is None
    # Parse to verify it's valid JSON
    parsed = json.loads(json_str)
    assert isinstance(parsed, list)
    assert len(parsed) == 2
    assert parsed[0]["id"] == 1
    assert parsed[1]["name"] == 'Item "2"'

def test_extract_json_nested_array():
    response = '''The data is structured as: {
        "items": [
            [1, 2, 3],
            ["a", "b", "c"],
            {"nested": ["x", "y", "z"]}
        ],
        "metadata": {
            "counts": [4, 5, 6]
        }
    }'''
    
    json_str, error = extract_json(response)
    assert error is None
    # Parse to verify it's valid JSON
    parsed = json.loads(json_str)
    assert isinstance(parsed["items"], list)
    assert len(parsed["items"]) == 3
    assert parsed["items"][0] == [1, 2, 3]
    assert parsed["items"][2]["nested"] == ["x", "y", "z"]
    assert parsed["metadata"]["counts"] == [4, 5, 6]

def test_extract_json_array_with_no_closing_bracket():
    response = '''Here's the array: [
        {"id": 1},
        {"id": 2},
    '''
    json_str, error = extract_json(response)
    assert json_str == ""
    assert "No closing ]" in error

def test_extract_json_prefer_first():
    response = '''Two JSON structures: {"first": true} ["second"]'''
    json_str, error = extract_json(response)
    assert error is None
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)
    assert parsed["first"] is True

    response = '''Two JSON structures: ["first"] {"second": true}'''
    json_str, error = extract_json(response)
    assert error is None
    parsed = json.loads(json_str)
    assert isinstance(parsed, list)
    assert parsed[0] == "first"
