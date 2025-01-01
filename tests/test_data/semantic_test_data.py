"""Test data for semantic search tests."""

from typing import List, Dict, Any

def get_similar_titles() -> List[str]:
    """Get a list of similar titles for testing."""
    return [
        "How to write Python code",
        "Writing Python code tutorial",
        "Python coding guide",
        "Learn to program in Python",
        "Python programming basics",
        "Getting started with Python",
        "Python development tips",
        "Python coding best practices",
        "Python programming tutorial",
        "Introduction to Python coding"
    ]

def get_test_items() -> List[Dict[str, Any]]:
    """Get test items for semantic search."""
    return [
        {
            "id": 1,
            "title": "How to write Python code",
            "content": "This is a guide about writing Python code...",
            "tags": ["python", "programming", "tutorial"]
        },
        {
            "id": 2,
            "title": "Writing Python code tutorial",
            "content": "Learn how to write Python code step by step...",
            "tags": ["python", "tutorial", "beginner"]
        },
        {
            "id": 3,
            "title": "Python coding guide",
            "content": "A comprehensive guide to Python coding...",
            "tags": ["python", "guide", "programming"]
        }
    ]
