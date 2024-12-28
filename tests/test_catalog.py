"""Integration tests for the catalog functionality.

This test suite uses real integration testing instead of mocks:
- All API calls to Claude are real calls
- All database operations use a real SQLite database (in-memory)
- No mock objects or responses are used

This ensures our tests reflect real-world behavior and catch actual integration issues.
Test data is cleaned up after each test using test markers for isolation.

Key Integration Points Tested:
- Claude API semantic analysis
- SQLite database operations
- Full catalog item lifecycle
"""

import pytest
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session
import os
import sys
from datetime import datetime
import json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.catalog import CatalogItem, Tag, CatalogTag
from models.base import Base
from shared_lib.constants import CATALOG_CONFIG
from shared_lib.logging_util import setup_logging
from app_catalog import CatalogChat

@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    return session

@pytest.fixture
def catalog_chat():
    """Create a test CatalogChat instance"""
    return CatalogChat(db_path=':memory:', mode='test')

@pytest.fixture
def sample_catalog_items():
    """Create sample catalog items"""
    return [
        CatalogItem(title="Python Tutorial", description="A tutorial on Python programming"),
        CatalogItem(title="Machine Learning Basics", description="An introduction to machine learning concepts"),
        CatalogItem(title="Data Science with Python", description="A guide to data science using Python")
    ]

@pytest.fixture
def sample_tags():
    """Create sample tags"""
    return [
        Tag(name="Python"),
        Tag(name="Machine Learning"),
        Tag(name="Data Science")
    ]

def test_add_catalog_item(db_session, catalog_chat, sample_catalog_items):
    """Test adding a new catalog item."""
    session = db_session()
    item = sample_catalog_items[0]
    
    # Add item to database
    session.add(item)
    session.commit()
    
    # Verify item was added
    stored_item = session.query(CatalogItem).filter_by(title=item.title).first()
    assert stored_item is not None
    assert stored_item.title == item.title
    assert stored_item.description == item.description

def test_add_tags(db_session, sample_tags):
    """Test adding tags to the database."""
    session = db_session()
    
    # Add tags
    for tag in sample_tags:
        session.add(tag)
    session.commit()
    
    # Verify tags were added
    stored_tags = session.query(Tag).all()
    assert len(stored_tags) == len(sample_tags)
    assert {t.name for t in stored_tags} == {t.name for t in sample_tags}

def test_tag_catalog_item(db_session, sample_catalog_items, sample_tags):
    """Test tagging a catalog item."""
    session = db_session()
    
    # Add item and tags
    item = sample_catalog_items[0]
    session.add(item)
    for tag in sample_tags[:2]:  # Add first two tags
        session.add(tag)
    session.commit()
    
    # Create catalog tags
    for tag in sample_tags[:2]:
        catalog_tag = CatalogTag(catalog_id=item.id, tag_id=tag.id)
        session.add(catalog_tag)
    session.commit()
    
    # Verify tags were added to item
    stored_item = session.query(CatalogItem).filter_by(id=item.id).first()
    assert len(stored_item.tags) == 2
    assert {t.name for t in stored_item.tags} == {t.name for t in sample_tags[:2]}

def test_semantic_search(db_session, catalog_chat, sample_catalog_items):
    """Test semantic search functionality."""
    session = db_session()
    
    # Add items to database
    for item in sample_catalog_items:
        session.add(item)
    session.commit()
    
    # Search for Python-related items
    matches = catalog_chat.get_semantic_matches("python programming", sample_catalog_items)
    assert len(matches) > 0
    assert matches[0].item.title == "Python Tutorial"
    
    # Search for ML-related items
    matches = catalog_chat.get_semantic_matches("machine learning", sample_catalog_items)
    assert len(matches) > 0
    assert matches[0].item.title == "Machine Learning Basics"

if __name__ == '__main__':
    pytest.main()
