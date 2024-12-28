"""Unit tests for semantic search functionality that don't require API calls."""
import pytest
from app_catalog import CatalogChat
from models.catalog import CatalogItem, Tag
from shared_lib.constants import CATALOG_CONFIG

def test_semantic_search_disabled():
    """Test that semantic search returns empty list when disabled."""
    chat = CatalogChat(mode='test', enable_semantic=False)
    items = [
        CatalogItem(title="Python Tutorial"),
        CatalogItem(title="JavaScript Guide")
    ]
    
    matches = chat.get_semantic_matches("python programming", items)
    assert len(matches) == 0

def test_semantic_search_empty_query():
    """Test handling of empty or whitespace queries."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    
    # Empty string
    matches = chat.get_semantic_matches("", items)
    assert len(matches) == 0
    
    # Whitespace only
    matches = chat.get_semantic_matches("   ", items)
    assert len(matches) == 0

def test_semantic_search_threshold_adjustment():
    """Test threshold adjustment based on query length."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    
    # Keep track of the threshold used
    used_threshold = None
    
    def mock_messages_create(*args, **kwargs):
        nonlocal used_threshold
        system_prompt = kwargs.get('system', '')
        # Extract threshold based on whether the prompt includes short query instructions
        if 'For short queries, prioritize abbreviations and key terms.' in system_prompt:
            used_threshold = CATALOG_CONFIG['TAG_MATCH_THRESHOLD']
        else:
            used_threshold = CATALOG_CONFIG['POTENTIAL_MATCH_THRESHOLD']
        # Return a valid response format
        return type('Response', (), {
            'content': [type('Content', (), {'text': '[{"matches": [(0, 0.9, "test")]}]'})]
        })
    
    # Replace the API client's messages.create method
    chat.client.messages.create = mock_messages_create
    
    # Short query should use TAG_MATCH_THRESHOLD
    chat.get_semantic_matches("api", items)
    assert used_threshold == CATALOG_CONFIG['TAG_MATCH_THRESHOLD']
    
    # Longer query should use POTENTIAL_MATCH_THRESHOLD
    chat.get_semantic_matches("how to use the api", items)
    assert used_threshold == CATALOG_CONFIG['POTENTIAL_MATCH_THRESHOLD']

def test_semantic_search_item_conversion():
    """Test conversion of different item types to title strings."""
    chat = CatalogChat(mode='test')
    
    # Create mixed list of items
    items = [
        "Plain string title",
        CatalogItem(title="CatalogItem title"),
        CatalogItem(title="Another item")
    ]
    
    # Mock the API call to verify item conversion
    def mock_messages_create(*args, **kwargs):
        messages = kwargs.get('messages', [])
        content = messages[0]['content'] if messages else ''
        assert "Plain string title" in content
        assert "CatalogItem title" in content
        assert "Another item" in content
        return type('Response', (), {
            'content': [type('Content', (), {'text': '[{"matches": [(0, 0.9, "test")]}]'})]
        })
    
    chat.client.messages.create = mock_messages_create
    chat.get_semantic_matches("test query", items)

def test_semantic_search_error_handling():
    """Test error handling in semantic search."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    
    # Mock API error
    def mock_messages_create(*args, **kwargs):
        raise Exception("API Error")
    
    chat.client.messages.create = mock_messages_create
    
    # Should handle error gracefully and return empty list
    matches = chat.get_semantic_matches("test query", items)
    assert matches == []

def test_semantic_search_prompt_construction():
    """Test construction of semantic search prompt."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    
    # Mock to capture the constructed prompt
    def mock_messages_create(*args, **kwargs):
        messages = kwargs.get('messages', [])
        assert len(messages) > 0
        content = messages[0]['content']
        assert "Test Item" in content
        return type('Response', (), {
            'content': [type('Content', (), {'text': '[{"matches": [(0, 0.9, "test")]}]'})]
        })
    
    chat.client.messages.create = mock_messages_create
    chat.get_semantic_matches("test query", items)

def test_semantic_search_json_parsing():
    """Test parsing of semantic search JSON responses."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    
    # Mock different JSON response formats
    test_cases = [
        # Valid response with matches
        (
            '[{"matches": [(0, 0.9, "test")]}]',
            lambda matches: len(matches) == 1 and matches[0][1] == 0.9
        ),
        # Empty matches
        (
            '[{"matches": []}]',
            lambda matches: len(matches) == 0
        ),
        # Multiple matches
        (
            '[{"matches": [(0, 0.9, "test"), (1, 0.8, "test2")]}]',
            lambda matches: len(matches) == 2 and matches[0][1] > matches[1][1]
        )
    ]
    
    for response_text, validator in test_cases:
        def mock_messages_create(*args, **kwargs):
            return type('Response', (), {
                'content': [type('Content', (), {'text': response_text})]
            })
        
        chat.client.messages.create = mock_messages_create
        matches = chat.get_semantic_matches("test query", items)
        assert validator(matches)

def test_semantic_search_response_validation():
    """Test validation of semantic search response format."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    
    # Test invalid JSON
    def mock_invalid_json(*args, **kwargs):
        return type('Response', (), {
            'content': [type('Content', (), {'text': 'invalid json'})]
        })
    
    chat.client.messages.create = mock_invalid_json
    matches = chat.get_semantic_matches("test query", items)
    assert matches == []
    
    # Test missing matches key
    def mock_missing_matches(*args, **kwargs):
        return type('Response', (), {
            'content': [type('Content', (), {'text': '{"no_matches": []}'})]
        })
    
    chat.client.messages.create = mock_missing_matches
    matches = chat.get_semantic_matches("test query", items)
    assert matches == []
    
    # Test invalid matches type
    def mock_invalid_matches_type(*args, **kwargs):
        return type('Response', (), {
            'content': [type('Content', (), {'text': '{"matches": "not a list"}'})]
        })
    
    chat.client.messages.create = mock_invalid_matches_type
    matches = chat.get_semantic_matches("test query", items)
    assert matches == []

def test_semantic_search_score_filtering():
    """Test filtering of matches based on threshold."""
    chat = CatalogChat(mode='test')
    items = [
        CatalogItem(title="Item 1"),
        CatalogItem(title="Item 2"),
        CatalogItem(title="Item 3")
    ]
    
    def mock_scores(*args, **kwargs):
        return type('Response', (), {
            'content': [type('Content', (), {'text': '''[{
                "matches": [
                    (0, 0.9, "High score"),
                    (1, 0.7, "Medium score"),
                    (2, 0.3, "Low score")
                ]
            }]'''})]
        })
    
    chat.client.messages.create = mock_scores
    matches = chat.get_semantic_matches("test query", items)
    
    # Only high and medium scores should be included
    assert len(matches) == 2
    assert matches[0][1] == 0.9
    assert matches[1][1] == 0.7

def test_semantic_search_index_validation():
    """Test validation of match indices."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    
    def mock_invalid_indices(*args, **kwargs):
        return type('Response', (), {
            'content': [type('Content', (), {'text': '''[{
                "matches": [
                    (99, 0.9, "Invalid index"),
                    (-1, 0.8, "Negative index"),
                    (0, 0.7, "Valid index")
                ]
            }]'''})]
        })
    
    chat.client.messages.create = mock_invalid_indices
    matches = chat.get_semantic_matches("test query", items)
    
    # Only valid indices should be included
    assert len(matches) == 1
    assert matches[0][0] == items[0]

def test_semantic_search_prompt_variations():
    """Test prompt construction with different query types."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    
    # Keep track of prompts used
    prompts = []
    
    def mock_capture_prompt(*args, **kwargs):
        prompts.append(kwargs.get('messages', [])[0]['content'])
        return type('Response', (), {
            'content': [type('Content', (), {'text': '[{"matches": [(0, 0.9, "test")]}]'})]
        })
    
    chat.client.messages.create = mock_capture_prompt
    
    # Test different query types
    queries = [
        "short",
        "longer search query",
        "very specific technical term",
        "natural language question about something"
    ]
    
    for query in queries:
        chat.get_semantic_matches(query, items)
    
    # Verify each query generated a unique prompt
    assert len(set(prompts)) == len(queries)

def test_semantic_search_item_types():
    """Test handling of different item types in search."""
    chat = CatalogChat(mode='test')
    
    # Create items with different properties
    items = [
        CatalogItem(title="Item with tags", tags=[Tag(name="test")]),
        CatalogItem(title="Item without tags"),
        "Plain string item"
    ]
    
    def mock_check_items(*args, **kwargs):
        content = kwargs.get('messages', [])[0]['content']
        # Verify all items are included
        assert "Item with tags" in content
        assert "Item without tags" in content
        assert "Plain string item" in content
        # Verify tags are included
        assert "test" in content
        return type('Response', (), {
            'content': [type('Content', (), {'text': '[{"matches": [(0, 0.9, "test")]}]'})]
        })
    
    chat.client.messages.create = mock_check_items
    chat.get_semantic_matches("test query", items)
