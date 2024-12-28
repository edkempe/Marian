"""Test configuration and shared fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.base import Base
from models.email import Email
from models.email_analysis import EmailAnalysis
from models.catalog import CatalogItem, Tag, CatalogTag
from models.asset_catalog import AssetCatalogItem, AssetCatalogTag, AssetDependency
from models.gmail_label import GmailLabel
from shared_lib.constants import (
    API_CONFIG, DATABASE_CONFIG, EMAIL_CONFIG, 
    METRICS_CONFIG, CATALOG_CONFIG
)
from shared_lib.gmail_lib import GmailAPI
from app_catalog import CatalogChat

@pytest.fixture(scope="session", autouse=True)
def validate_config():
    """Validate all configuration values before any tests run."""
    # Validate email config
    assert 'DAYS_TO_FETCH' in EMAIL_CONFIG
    assert 'BATCH_SIZE' in EMAIL_CONFIG
    
    # Validate metrics config
    assert 'METRICS_PORT' in METRICS_CONFIG
    
    # Validate API config
    assert 'API_KEY' in API_CONFIG
    
    # Validate database config
    assert 'DATABASE_URL' in DATABASE_CONFIG
    
    # Validate catalog config
    assert 'MODEL' in CATALOG_CONFIG

@pytest.fixture(scope="session", autouse=True)
def gmail_api():
    """Create and initialize Gmail API instance."""
    gmail = GmailAPI()
    gmail.setup_label_database()
    gmail.sync_labels()
    return gmail

@pytest.fixture(scope="session")
def catalog_chat():
    """Create a CatalogChat instance for testing."""
    return CatalogChat(mode='production')

@pytest.fixture(scope="session")
def db_engine(validate_schema):
    """Create test database engine.
    
    This fixture depends on validate_schema to ensure schema is valid before
    creating test database.
    """
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def db_session(db_engine):
    """Create database session factory."""
    Session = sessionmaker(bind=db_engine)
    return Session

@pytest.fixture(autouse=True)
def setup_test_db(db_session):
    """Set up clean test database before each test.
    
    This fixture:
    1. Starts a transaction
    2. Yields control to the test
    3. Rolls back the transaction after the test
    
    This ensures each test has a clean database state.
    """
    session = db_session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
