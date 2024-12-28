"""Integration tests for semantic search functionality with real API calls."""
import pytest
from src.app_catalog import CatalogChat
from models.catalog import CatalogItem, Tag
from shared_lib.constants import CATALOG_CONFIG

@pytest.fixture
def chat():
    """Create a CatalogChat instance for testing."""
    return CatalogChat(mode='production')

def test_semantic_search_real():
    """Test semantic search with real API calls."""
    chat = CatalogChat(mode='production')
    items = [
        CatalogItem(title="Python Tutorial for Beginners"),
        CatalogItem(title="Advanced JavaScript Guide"),
        CatalogItem(title="Introduction to Machine Learning")
    ]
    
    # Test exact match
    matches = chat.get_semantic_matches("python tutorial", items)
    assert len(matches) > 0
    assert matches[0].index == 0  # Python Tutorial should be first
    
    # Test semantic match
    matches = chat.get_semantic_matches("ML guide", items)
    assert len(matches) > 0
    assert matches[0].index == 2  # Machine Learning should be first
    
    # Test no matches
    matches = chat.get_semantic_matches("quantum computing", items)
    assert len(matches) == 0

def test_semantic_search_with_tags():
    """Test semantic search with items containing tags."""
    chat = CatalogChat(mode='production')
    items = [
        CatalogItem(
            title="Python Tutorial",
            tags=[Tag(name="programming"), Tag(name="beginner")]
        ),
        CatalogItem(
            title="JavaScript Guide",
            tags=[Tag(name="programming"), Tag(name="web")]
        )
    ]
    
    # Test matching by tag
    matches = chat.get_semantic_matches("web development", items)
    assert len(matches) > 0
    assert matches[0].index == 1  # JavaScript Guide should be first
    
    # Test matching by both title and tag
    matches = chat.get_semantic_matches("python programming", items)
    assert len(matches) > 0
    assert matches[0].index == 0  # Python Tutorial should be first

def test_semantic_search_multilingual():
    """Test semantic search with multilingual content."""
    chat = CatalogChat(mode='production')
    items = [
        CatalogItem(title="Python Tutorial"),
        CatalogItem(title="Guía de Python"),  # Spanish
        CatalogItem(title="Python チュートリアル")  # Japanese
    ]
    
    # Test matching across languages
    matches = chat.get_semantic_matches("python guide", items)
    assert len(matches) > 0
    # All items should match since they're about Python tutorials
    assert len(matches) == 3
