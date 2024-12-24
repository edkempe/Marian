"""Common test fixtures and configuration."""
import pytest
from unittest.mock import MagicMock, patch
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.email import Email
from models.email_analysis import EmailAnalysis
from constants import API_CONFIG, DATABASE_CONFIG

@pytest.fixture
def test_db_session():
    """Create an in-memory database session for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture(autouse=True)
def mock_external_apis():
    """Mock all external API calls to prevent test stalls."""
    with patch('anthropic.Anthropic') as mock_anthropic, \
         patch('lib_gmail.GmailAPI') as mock_gmail:
        
        # Configure Anthropic API mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content = [{'text': '{"summary": "Test summary"}'}]
        mock_client.messages.create.return_value = mock_message
        
        # Configure Gmail API mock
        mock_gmail_service = MagicMock()
        mock_gmail.return_value.service = mock_gmail_service
        
        # Mock basic profile info
        mock_gmail_service.users().getProfile().execute.return_value = {
            'emailAddress': 'test.user@example.com'
        }
        
        yield
