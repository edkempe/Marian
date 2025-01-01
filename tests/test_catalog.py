"""Integration tests for the catalog functionality.

This test suite uses real integration testing instead of mocks:
- All API calls to Claude are real calls
- All database operations use a real SQLite database (file-based)
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
from models.catalog import CatalogEntry, CatalogTag, Tag
from shared_lib.constants import CONFIG
from shared_lib.logging_util import setup_logging
from src.app_catalog import CatalogChat
from config.test_settings import test_settings


@pytest.fixture(scope="function")
def db_engine():
    """Create test database engine."""
    engine = create_engine(test_settings.DATABASE_URLS["catalog"])
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create test database session."""
    session = Session(db_engine)
    yield session
    session.close()


@pytest.fixture
def catalog_chat():
    """Create a test CatalogChat instance"""
    return CatalogChat(db_path=test_settings.DATABASE_URLS["catalog"], mode="test")


@pytest.fixture
def sample_catalog_entries():
    """Create sample catalog entries"""
    return [
        CatalogEntry(
            title="Python Tutorial", description="A tutorial on Python programming"
        ),
        CatalogEntry(
            title="Machine Learning Basics",
            description="An introduction to machine learning concepts",
        ),
        CatalogEntry(
            title="Data Science with Python",
            description="A guide to data science using Python",
        ),
    ]


@pytest.fixture
def sample_tags():
    """Create sample tags"""
    return [Tag(name="Python"), Tag(name="Machine Learning"), Tag(name="Data Science")]


def test_add_catalog_entry(db_session, catalog_chat, sample_catalog_entries):
    """Test adding a new catalog entry."""
    # Add entries directly to the session
    current_time = int(datetime.now().timestamp())
    for entry in sample_catalog_entries:
        entry.status = "active"  # Set status to active
        entry.created_date = current_time
        entry.modified_date = current_time
        db_session.add(entry)
    db_session.commit()

    # Query all entries
    all_entries = db_session.query(CatalogEntry).all()
    assert len(all_entries) == len(sample_catalog_entries)

    # Verify each entry was added correctly
    for added_entry, sample_entry in zip(all_entries, sample_catalog_entries):
        assert added_entry.title == sample_entry.title
        assert added_entry.status == "active"
        assert added_entry.created_date == current_time
        assert added_entry.modified_date == current_time


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


def test_tag_catalog_entry(db_session, sample_catalog_entries, sample_tags):
    """Test tagging a catalog entry."""
    session = db_session

    # Add entry and tags
    current_time = int(datetime.now().timestamp())

    # Set up entry
    entry = sample_catalog_entries[0]
    entry.status = "active"
    entry.created_date = current_time
    entry.modified_date = current_time
    session.add(entry)

    # Set up tags
    for tag in sample_tags[:2]:  # Add first two tags
        tag.created_date = current_time
        tag.modified_date = current_time
        session.add(tag)
    session.commit()

    # Create relationship
    entry.tags.extend(sample_tags[:2])
    session.commit()

    # Verify relationships
    stored_entry = session.query(CatalogEntry).filter_by(title=entry.title).first()
    assert len(stored_entry.tags) == 2
    assert {t.name for t in stored_entry.tags} == {t.name for t in sample_tags[:2]}


def test_semantic_search(db_session, catalog_chat, sample_catalog_entries):
    """Test semantic search functionality."""
    session = db_session

    # Add entries to database
    current_time = int(datetime.now().timestamp())
    for entry in sample_catalog_entries:
        entry.status = "active"
        entry.created_date = current_time
        entry.modified_date = current_time
        session.add(entry)
    session.commit()

    # Get all entries
    entries = session.query(CatalogEntry).all()

    # Test basic search
    matches = catalog_chat.get_semantic_matches("python programming", entries)
    assert len(matches) > 0
    assert any("Python" in match[0].title for match in matches)


if __name__ == "__main__":
    pytest.main()
