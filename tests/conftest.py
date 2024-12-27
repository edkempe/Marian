"""Database test fixtures for pytest.

This module provides SQLAlchemy session fixtures for database testing. Following pytest
convention, it's named 'conftest.py' to make fixtures automatically available to all tests.

Database Fixtures:
- test_db_session: Creates an in-memory SQLite database for testing email storage and analysis

Components Using These Fixtures:
- Email storage and retrieval tests
- Email analysis persistence tests
- Historical email data query tests

Example Usage:
    def test_email_storage(test_db_session):
        email = Email(...)
        test_db_session.add(email)
        test_db_session.commit()
        
        stored = test_db_session.query(Email).first()
        assert stored.id == email.id

Note:
    Uses SQLite in-memory database to ensure test isolation and avoid affecting
    production data.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.email import Email
from models.email_analysis import EmailAnalysis
from shared_lib.constants import API_CONFIG, DATABASE_CONFIG

@pytest.fixture
def test_db_session():
    """Create an in-memory SQLite database session for testing email components.
    
    This fixture:
    1. Creates an in-memory SQLite database
    2. Sets up all database tables (Email, EmailAnalysis, etc.)
    3. Provides a session for test operations
    4. Automatically closes the session after the test
    
    Returns:
        SQLAlchemy session: Session connected to in-memory test database
    """
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
