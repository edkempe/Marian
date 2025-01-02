"""Tests for Anthropic API response handling."""

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

from shared_lib.anthropic_lib import (
    clean_json_text,
    extract_json,
    parse_claude_response,
)
from shared_lib.constants import API

# Load environment variables
load_dotenv()


def test_extract_json_with_real_response():
    # Initialize Anthropic client
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Get a real response from Claude with JSON
    response = client.messages.create(
        model=API["TEST_MODEL"],
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": "Analyze this email and return a JSON object with these fields: subject, priority (1-5), action_needed (boolean), and summary. Here's the email: Subject: Team meeting tomorrow at 10am. We need to discuss the Q1 roadmap and assign tasks for the new project launch. Please review the attached docs before the meeting.",
            }
        ],
    )

    # Extract JSON from Claude's response
    json_str, error = extract_json(response.content[0].text)
    assert error is None

    # Verify the extracted JSON is valid and has expected fields
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)
    assert "subject" in parsed
    assert isinstance(parsed["priority"], int)
    assert isinstance(parsed["action_needed"], bool)
    assert isinstance(parsed["summary"], str)


def test_parse_claude_response_with_array():
    # Test with array response
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model=API["TEST_MODEL"],
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": "List 3 action items from this email as a JSON array of objects with 'task' and 'deadline' fields: Subject: Project Updates. 1. Submit Q4 report by Friday 2. Schedule team review for next week 3. Update documentation by end of month",
            }
        ],
    )

    # Extract JSON from Claude's response
    json_str, error = extract_json(response.content[0].text)
    assert error is None

    # Verify array structure
    parsed = json.loads(json_str)
    assert isinstance(parsed, list)
    assert len(parsed) == 3
    for item in parsed:
        assert "task" in item
        assert "deadline" in item


def test_parse_claude_response_with_nested_structure():
    # Test with nested JSON structure
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model=API["TEST_MODEL"],
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": "Analyze this email thread and return nested JSON with 'thread' object containing 'emails' array and 'summary' field: Subject: Re: Project Status. Thanks for the update. I'll review the changes. --- On Mon, Jan 1: Here are the latest changes to the project.",
            }
        ],
    )

    # Extract JSON from Claude's response
    json_str, error = extract_json(response.content[0].text)
    assert error is None

    # Verify nested structure
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)
    assert "thread" in parsed
    assert isinstance(parsed["thread"]["emails"], list)
    assert isinstance(parsed["thread"]["summary"], str)


def test_error_handling_with_invalid_response():
    # Test with response that doesn't contain JSON
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model=API["TEST_MODEL"],
        max_tokens=1000,
        temperature=0,
        messages=[{"role": "user", "content": "Just say hello"}],
    )

    # Should handle non-JSON response gracefully
    json_str, error = extract_json(response.content[0].text)
    assert json_str == ""
    assert error is not None
