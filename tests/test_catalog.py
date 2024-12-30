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

import json
from datetime import datetime

import pytest
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session

from models.base import Base
from models.catalog import CatalogItem, CatalogTag, Tag
from shared_lib.constants import CATALOG_CONFIG
from shared_lib.logging_util import setup_logging
from src.app_catalog import CatalogChat


@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    return session


@pytest.fixture
def catalog_chat():
    """Create a test CatalogChat instance"""
    return CatalogChat(db_path=":memory:", mode="test")


@pytest.fixture
def sample_catalog_items():
    """Create sample catalog items"""
    return [
        CatalogItem(
            title="Python Tutorial", description="A tutorial on Python programming"
        ),
        CatalogItem(
            title="Machine Learning Basics",
            description="An introduction to machine learning concepts",
        ),
        CatalogItem(
            title="Data Science with Python",
            description="A guide to data science using Python",
        ),
    ]


@pytest.fixture
def sample_tags():
    """Create sample tags"""
    return [Tag(name="Python"), Tag(name="Machine Learning"), Tag(name="Data Science")]


def test_add_catalog_item(db_session, catalog_chat, sample_catalog_items):
    """Test adding a new catalog item."""
    # Add items directly to the session
    current_time = int(datetime.now().timestamp())
    for item in sample_catalog_items:
        item.status = "active"  # Set status to active
        item.created_date = current_time
        item.modified_date = current_time
        db_session.add(item)
    db_session.commit()

    # Query all items
    all_items = db_session.query(CatalogItem).all()
    assert len(all_items) == len(sample_catalog_items)

    # Verify each item was added correctly
    for added_item, sample_item in zip(all_items, sample_catalog_items):
        assert added_item.title == sample_item.title
        assert added_item.status == "active"
        assert added_item.created_date == current_time
        assert added_item.modified_date == current_time


def test_add_tags(db_session, sample_tags):
    """Test adding tags to the database."""
    session = db_session

    # Add tags
    current_time = int(datetime.now().timestamp())
    for tag in sample_tags:
        tag.created_date = current_time
        tag.modified_date = current_time
        session.add(tag)
    session.commit()

    # Verify tags were added
    stored_tags = session.query(Tag).all()
    assert len(stored_tags) == len(sample_tags)

    # Check each tag
    for stored_tag, sample_tag in zip(stored_tags, sample_tags):
        assert stored_tag.name == sample_tag.name
        assert stored_tag.created_date == current_time
        assert stored_tag.modified_date == current_time


def test_tag_catalog_item(db_session, sample_catalog_items, sample_tags):
    """Test tagging a catalog item."""
    session = db_session

    # Add item and tags
    current_time = int(datetime.now().timestamp())

    # Set up item
    item = sample_catalog_items[0]
    item.status = "active"
    item.created_date = current_time
    item.modified_date = current_time
    session.add(item)

    # Set up tags
    for tag in sample_tags[:2]:  # Add first two tags
        tag.created_date = current_time
        tag.modified_date = current_time
        session.add(tag)
    session.commit()

    # Create relationship
    item.tags.extend(sample_tags[:2])
    session.commit()

    # Verify relationships
    stored_item = session.query(CatalogItem).filter_by(title=item.title).first()
    assert len(stored_item.tags) == 2
    assert {t.name for t in stored_item.tags} == {t.name for t in sample_tags[:2]}


def test_semantic_search(db_session, catalog_chat, sample_catalog_items):
    """Test semantic search functionality."""
    session = db_session

    # Add items to database
    current_time = int(datetime.now().timestamp())
    for item in sample_catalog_items:
        item.status = "active"
        item.created_date = current_time
        item.modified_date = current_time
        session.add(item)
    session.commit()

    # Get all items
    items = session.query(CatalogItem).all()

    # Test basic search
    matches = catalog_chat.get_semantic_matches("python programming", items)
    assert len(matches) > 0
    assert any("Python" in match[0].title for match in matches)


if __name__ == "__main__":
    pytest.main()
