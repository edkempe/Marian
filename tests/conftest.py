"""Test configuration and fixtures."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import sys
import json
from models.email import Email
from models.email_analysis import EmailAnalysis
from constants import API_CONFIG, DATABASE_CONFIG

@pytest.fixture
def mock_gmail_service():
    """Create a mock Gmail service for testing."""
    with patch('lib_gmail.GmailAPI') as mock_gmail:
        mock_service = MagicMock()
        mock_gmail.return_value.service = mock_service
        
        # Mock users().labels().list().execute()
        mock_labels = {
            'labels': [
                {'id': 'INBOX', 'name': 'INBOX'},
                {'id': 'SENT', 'name': 'SENT'},
                {'id': 'IMPORTANT', 'name': 'IMPORTANT'}
            ]
        }
        mock_service.users().labels().list().execute.return_value = mock_labels
        
        # Mock users().messages().list().execute()
        mock_messages = {
            'messages': [{'id': '123', 'threadId': 'thread123'}],
            'nextPageToken': None
        }
        mock_service.users().messages().list().execute.return_value = mock_messages
        
        yield mock_service

@pytest.fixture(autouse=True)
def mock_external_apis():
    """Mock all external API calls to prevent test stalls."""
    
    # Configure Gmail API mock
    mock_gmail = MagicMock()
    mock_service = MagicMock()
    mock_gmail.service = mock_service
    
    # Mock users().getProfile().execute()
    mock_service.users().getProfile().execute.return_value = {
        'emailAddress': 'test.user@example.com'
    }
    
    # Mock users().messages().get().execute()
    mock_service.users().messages().get().execute.return_value = {
        'id': 'test1',
        'threadId': 'thread1',
        'labelIds': ['INBOX'],
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'test.sender@example.com'},
                {'name': 'To', 'value': 'test.recipient@example.com'},
                {'name': 'Subject', 'value': 'Test Email'},
                {'name': 'Date', 'value': datetime.now().isoformat()}
            ],
            'parts': [{'body': {'data': 'VGVzdCBjb250ZW50'}}]  # Base64 "Test content"
        }
    }
    
    # Mock Anthropic API responses using API_CONFIG
    mock_response = {
        'summary': 'Test summary',
        'category': ['work'],
        'priority_score': 3,
        'project': 'Test Project',
        'topic': 'Test Topic',
        'sentiment': 'neutral',
        'confidence_score': 0.95
    }
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(mock_response))]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    
    # Apply all the mocks
    with patch('app_get_mail.GmailAPI', return_value=mock_gmail), \
         patch('anthropic.Client', return_value=mock_client):
        yield

@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    mock_session = MagicMock()
    
    # Mock email query results
    mock_email = Email(
        id='test1',
        thread_id='thread1',
        subject='Test Email',
        from_address='test.sender@example.com',
        to_address='test.recipient@example.com',
        content='Test content',
        received_date=datetime.now(),
        labels='["INBOX"]'
    )
    
    # Mock analysis query results
    mock_analysis = EmailAnalysis(
        email_id='test1',
        thread_id='thread1',
        summary='Test summary',
        category='work',
        priority_score=3,
        project='Test Project',
        topic='Test Topic',
        sentiment='neutral',
        confidence_score=0.95,
        raw_json=json.dumps({
            'summary': 'Test summary',
            'category': ['work'],
            'priority_score': 3,
            'project': 'Test Project',
            'topic': 'Test Topic',
            'sentiment': 'neutral',
            'confidence_score': 0.95
        })
    )
    
    # Configure mock query results
    mock_query = MagicMock()
    mock_query.all.return_value = [mock_email]
    mock_query.first.return_value = mock_email
    mock_query.filter_by.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    
    # Configure mock session
    mock_session.query.side_effect = lambda x: mock_query
    mock_session.commit = MagicMock()
    mock_session.add = MagicMock()
    mock_session.close = MagicMock()
    
    return mock_session
