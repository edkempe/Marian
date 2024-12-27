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
            'content': [type('Content', (), {'text': '{"matches": [{"index": 0, "score": 0.9, "reasoning": "test"}]}'})]
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
            'content': [type('Content', (), {'text': '{"matches": []}'})]
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
        system_prompt = kwargs.get('system', '')
        # Verify prompt contains key instructions
        assert "semantic search expert" in system_prompt.lower()
        assert "scoring guidelines" in system_prompt.lower()
        assert "return matches in this format" in system_prompt.lower()
        return type('Response', (), {
            'content': [type('Content', (), {'text': '{"matches": []}'})]
        })
    
    chat.client.messages.create = mock_messages_create
    chat.get_semantic_matches("test query", items)

def test_semantic_search_json_parsing():
    """Test parsing of semantic search JSON responses."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    
    # Mock different JSON response formats
    test_cases = [
        # Valid response
        (
            '{"matches": [{"index": 0, "score": 0.9, "reasoning": "test"}]}',
            [(items[0], 0.9, "test")]
        ),
        # Missing fields - should be filtered out
        (
            '{"matches": [{"index": 0}]}',
            []
        ),
        # Invalid JSON - should return empty list
        (
            'not json',
            []
        ),
        # Empty matches
        (
            '{"matches": []}',
            []
        )
    ]
    
    for response_text, expected_matches in test_cases:
        def mock_messages_create(*args, **kwargs):
            return type('Response', (), {
                'content': [type('Content', (), {'text': response_text})]
            })
        
        chat.client.messages.create = mock_messages_create
        matches = chat.get_semantic_matches("test", items)
        
        # Compare only the structure and values we care about
        if expected_matches:
            assert len(matches) == len(expected_matches)
            for actual, expected in zip(matches, expected_matches):
                assert actual[0] == expected[0]  # Compare CatalogItem
                assert actual[1] == expected[1]  # Compare score
                # Don't compare reasoning text as it may vary
        else:
            assert matches == []

def test_semantic_search_response_validation():
    """Test validation of semantic search response format."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    
    # Test invalid JSON format
    def mock_invalid_json(*args, **kwargs):
        return type('Response', (), {
            'content': [type('Content', (), {'text': 'Invalid JSON'})]
        })
    chat.client.messages.create = mock_invalid_json
    assert chat.get_semantic_matches("query", items) == []
    
    # Test missing matches field
    def mock_missing_matches(*args, **kwargs):
        return type('Response', (), {
            'content': [type('Content', (), {'text': '{"results": []}'})]
        })
    chat.client.messages.create = mock_missing_matches
    assert chat.get_semantic_matches("query", items) == []
    
    # Test invalid matches type
    def mock_invalid_matches_type(*args, **kwargs):
        return type('Response', (), {
            'content': [type('Content', (), {'text': '{"matches": "not a list"}'})]
        })
    chat.client.messages.create = mock_invalid_matches_type
    assert chat.get_semantic_matches("query", items) == []

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
            'content': [type('Content', (), {'text': '''
                {
                    "matches": [
                        {"index": 0, "score": 0.9, "reasoning": "high match"},
                        {"index": 1, "score": 0.7, "reasoning": "medium match"},
                        {"index": 2, "score": 0.5, "reasoning": "low match"}
                    ]
                }
            '''})]
        })
    
    chat.client.messages.create = mock_scores
    
    # Test high threshold
    matches = chat.get_semantic_matches("query", items, threshold=0.8)
    assert len(matches) == 1
    assert matches[0][0].title == "Item 1"
    assert matches[0][1] == 0.9
    
    # Test medium threshold
    matches = chat.get_semantic_matches("query", items, threshold=0.6)
    assert len(matches) == 2
    assert matches[0][0].title == "Item 1"  # Should be sorted by score
    assert matches[1][0].title == "Item 2"

def test_semantic_search_index_validation():
    """Test validation of match indices."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    
    def mock_invalid_indices(*args, **kwargs):
        return type('Response', (), {
            'content': [type('Content', (), {'text': '''
                {
                    "matches": [
                        {"score": 0.9, "reasoning": "missing index"},
                        {"index": -1, "score": 0.9, "reasoning": "negative index"},
                        {"index": 1, "score": 0.9, "reasoning": "out of bounds"},
                        {"index": 0, "score": 0.9, "reasoning": "valid index"}
                    ]
                }
            '''})]
        })
    
    chat.client.messages.create = mock_invalid_indices
    matches = chat.get_semantic_matches("query", items, threshold=0.8)
    assert len(matches) == 1  # Only the valid index should be included
    assert matches[0][0].title == "Test Item"
    assert matches[0][1] == 0.9  # Check score
    assert matches[0][2] == "valid index"  # Check reasoning

def test_semantic_search_prompt_variations():
    """Test prompt construction with different query types."""
    chat = CatalogChat(mode='test')
    items = [CatalogItem(title="Test Item")]
    captured_prompts = []
    
    def mock_capture_prompt(*args, **kwargs):
        captured_prompts.append(kwargs.get('system', ''))
        return type('Response', (), {
            'content': [type('Content', (), {'text': '{"matches": []}'})]
        })
    
    chat.client.messages.create = mock_capture_prompt
    
    # Test short query prompt
    chat.get_semantic_matches("api", items)
    assert 'For short queries, prioritize abbreviations and key terms.' in captured_prompts[-1]
    assert 'Score advanced/specific content' in captured_prompts[-1]
    
    # Test long query prompt
    chat.get_semantic_matches("how to implement api authentication", items)
    assert 'Focus on conceptual similarity and meaning' in captured_prompts[-1]
    assert 'Consider synonyms, related concepts' in captured_prompts[-1]

def test_semantic_search_item_types():
    """Test handling of different item types in search."""
    chat = CatalogChat(mode='test')
    items = [
        "Plain string",
        CatalogItem(title="Catalog item"),
        Tag(name="Tag item")
    ]
    
    def mock_check_items(*args, **kwargs):
        prompt = kwargs.get('system', '')
        # Verify all items are converted to strings in the prompt
        assert '"Plain string"' in prompt
        assert '"Catalog item"' in prompt
        assert '"Tag item"' in prompt
        return type('Response', (), {
            'content': [type('Content', (), {'text': '{"matches": []}'})]
        })
    
    chat.client.messages.create = mock_check_items
    chat.get_semantic_matches("query", items)
