"""Test database schema and migrations."""

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from models.base import Base
from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from models.catalog import CatalogEntry, CatalogItem, Tag
from models.gmail_label import GmailLabel, email_labels
from tests.factories import EmailFactory, EmailAnalysisFactory, CatalogEntryFactory, GmailLabelFactory
from datetime import datetime


@pytest.fixture(scope="function")
def test_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create test database session."""
    session = Session(bind=test_engine)
    yield session
    session.close()


def test_create_tables(test_engine):
    """Test table creation."""
    # Tables should be created by the fixture
    # Verify tables exist
    inspector = inspect(test_engine)
    table_names = inspector.get_table_names()
    
    assert "email_messages" in table_names
    assert "email_analyses" in table_names
    assert "catalog_entries" in table_names
    assert "catalog_items" in table_names
    assert "tags" in table_names
    assert "catalog_tags" in table_names
    assert "gmail_labels" in table_names
    assert "email_labels" in table_names


def test_email_schema(test_session):
    """Test email table schema."""
    # Create test email
    email = EmailFactory()
    test_session.add(email)
    test_session.commit()
    
    # Verify columns
    stored_email = test_session.query(EmailMessage).first()
    assert stored_email.message_id is not None
    assert stored_email.subject is not None
    assert stored_email.from_address is not None
    assert isinstance(stored_email.to_addresses, list)
    assert isinstance(stored_email.cc_addresses, list)
    assert isinstance(stored_email.bcc_addresses, list)
    assert stored_email.body_text is not None
    assert stored_email.body_html is not None
    assert stored_email.received_date is not None
    assert stored_email.sent_date is not None


def test_analysis_schema(test_session):
    """Test analysis table schema."""
    # Create test analysis
    analysis = EmailAnalysisFactory()
    test_session.add(analysis)
    test_session.commit()
    
    # Verify columns
    stored_analysis = test_session.query(EmailAnalysis).first()
    assert stored_analysis.email_id is not None
    assert stored_analysis.sentiment is not None
    assert isinstance(stored_analysis.categories, list)
    assert stored_analysis.summary is not None
    assert isinstance(stored_analysis.key_points, list)
    assert isinstance(stored_analysis.action_items, list)
    assert stored_analysis.created_at is not None
    assert stored_analysis.updated_at is not None


def test_catalog_schema(test_session):
    """Test catalog table schema."""
    # Create test catalog entry and item
    entry = CatalogEntryFactory()
    test_session.add(entry)
    
    item = CatalogItem(
        title="Test Item",
        description="Test Description",
        content="Test Content",
        source="test",
        status="draft",
        created_date=int(datetime.now().timestamp()),
        modified_date=int(datetime.now().timestamp()),
    )
    test_session.add(item)
    test_session.commit()
    
    # Verify catalog entry columns
    stored_entry = test_session.query(CatalogEntry).first()
    assert stored_entry.email_id is not None
    assert stored_entry.title is not None
    assert stored_entry.description is not None
    assert isinstance(stored_entry.tags, list)
    assert isinstance(stored_entry.extra_metadata, dict)
    assert stored_entry.created_at is not None
    assert stored_entry.updated_at is not None
    
    # Verify catalog item columns
    stored_item = test_session.query(CatalogItem).first()
    assert stored_item.title == "Test Item"
    assert stored_item.description == "Test Description"
    assert stored_item.content == "Test Content"
    assert stored_item.source == "test"
    assert stored_item.status == "draft"
    assert stored_item.created_date is not None
    assert stored_item.modified_date is not None


def test_tag_schema(test_session):
    """Test tag table schema."""
    # Create test tag
    tag = Tag(
        name="test_tag",
        description="Test Tag Description",
        created_date=int(datetime.now().timestamp()),
        modified_date=int(datetime.now().timestamp()),
    )
    test_session.add(tag)
    test_session.commit()
    
    # Verify tag columns
    stored_tag = test_session.query(Tag).first()
    assert stored_tag.name == "test_tag"
    assert stored_tag.description == "Test Tag Description"
    assert not stored_tag.deleted
    assert stored_tag.created_date is not None
    assert stored_tag.modified_date is not None


def test_relationships(test_session):
    """Test relationships between models."""
    # Create test data
    email = EmailFactory()
    analysis = EmailAnalysisFactory(email=email)
    catalog = CatalogEntryFactory()
    label = GmailLabelFactory()
    
    # Set up relationships
    email.analysis = analysis
    email.catalog_entry = catalog
    email.labels.append(label)
    
    test_session.add_all([email, analysis, catalog, label])
    test_session.commit()
    
    # Test email -> analysis relationship
    saved_email = test_session.query(EmailMessage).first()
    assert saved_email.analysis is not None
    assert saved_email.analysis.id == analysis.id
    
    # Test email -> catalog relationship
    assert saved_email.catalog_entry is not None
    assert saved_email.catalog_entry.id == catalog.id
    
    # Test email -> label relationship
    assert len(saved_email.labels) == 1
    assert saved_email.labels[0].id == label.id
    
    # Test reverse relationships
    saved_analysis = test_session.query(EmailAnalysis).first()
    assert saved_analysis.email.id == email.id
    
    saved_catalog = test_session.query(CatalogEntry).first()
    assert saved_catalog.email.id == email.id
    
    saved_label = test_session.query(GmailLabel).first()
    assert len(saved_label.emails) == 1
    assert saved_label.emails[0].id == email.id
