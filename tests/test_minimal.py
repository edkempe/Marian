"""Minimal test suite to verify mocking works."""

import pytest
from datetime import datetime
import json
from unittest.mock import patch, MagicMock
from app_email_analyzer import EmailAnalyzer
from app_email_self_log import EmailSelfAnalyzer
from app_email_reports import EmailAnalytics
from models.email import Email
from models.email_analysis import EmailAnalysis
from constants import API_CONFIG, DATABASE_CONFIG

@pytest.fixture
def mock_db_session():
    return MagicMock()

def test_email_analyzer_mocking(mock_db_session):
    """Test that EmailAnalyzer API calls are properly mocked."""
    mock_env = {
        'ANTHROPIC_API_KEY': 'test_key',
        'EMAIL_DB_URL': DATABASE_CONFIG['EMAIL_DB_URL'],
        'ANALYSIS_DB_URL': DATABASE_CONFIG['ANALYSIS_DB_URL']
    }
    mock_api_config = API_CONFIG.copy()
    mock_api_config.update({
        'EMAIL_ANALYSIS_PROMPT': 'Analyze this email: {email_content}',  # Simplified prompt for testing
        'ERROR_MESSAGES': {
            'api_error': 'API Error: {error}'
        }
    })
    
    with patch('app_email_analyzer.get_analysis_session', return_value=mock_db_session), \
         patch('app_email_analyzer.get_email_session', return_value=mock_db_session), \
         patch('anthropic.Client') as mock_client_class, \
         patch.dict('os.environ', mock_env), \
         patch.dict('app_email_analyzer.API_CONFIG', mock_api_config):
        
        # Configure Anthropic mock
        mock_response = {
            'summary': 'Test summary',
            'category': ['work'],
            'priority_score': 3,
            'project': 'Test Project',
            'topic': 'Test Topic',
            'sentiment': 'neutral'
        }
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client
        
        analyzer = EmailAnalyzer(metrics_port=0)  # Disable metrics server for tests
        
        test_email = {
            'id': 'test1',
            'subject': 'Test Email',
            'content': 'Test content',
            'received_date': datetime.now().isoformat(),
            'thread_id': 'thread1',
            'labels': '["INBOX"]'
        }
        
        analysis = analyzer.analyze_email(test_email)
        assert analysis is not None
        assert isinstance(analysis, dict)
        assert analysis.get('summary') == 'Test summary'
        assert analysis.get('project') == 'Test Project'

def test_gmail_api_mocking(mock_db_session):
    """Test that Gmail API calls are properly mocked."""
    mock_env = {
        'ANTHROPIC_API_KEY': 'test_key',
        'EMAIL_DB_URL': DATABASE_CONFIG['EMAIL_DB_URL'],
        'ANALYSIS_DB_URL': DATABASE_CONFIG['ANALYSIS_DB_URL']
    }
    with patch('app_email_self_log.get_email_session', return_value=mock_db_session), \
         patch('app_get_mail.GmailAPI') as mock_gmail_api, \
         patch.dict('os.environ', mock_env):
        
        # Configure Gmail mock
        mock_service = MagicMock()
        mock_service.users().getProfile().execute.return_value = {
            'emailAddress': 'test.user@example.com'
        }
        mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': 'test1', 'threadId': 'thread1'}],
            'nextPageToken': None
        }
        mock_gmail = MagicMock()
        mock_gmail.service = mock_service
        mock_gmail_api.return_value = mock_gmail
        
        analyzer = EmailSelfAnalyzer()
        emails = analyzer.get_self_emails()
        
        assert len(emails) > 0
        assert emails[0].id == 'test1'
        assert emails[0].subject == 'Test Email'
        assert emails[0].from_address == 'test.sender@example.com'

def test_anthropic_api_mocking(mock_db_session):
    """Test that Anthropic API calls are properly mocked."""
    mock_env = {
        'ANTHROPIC_API_KEY': 'test_key',
        'EMAIL_DB_URL': DATABASE_CONFIG['EMAIL_DB_URL'],
        'ANALYSIS_DB_URL': DATABASE_CONFIG['ANALYSIS_DB_URL']
    }
    mock_api_config = API_CONFIG.copy()
    mock_api_config.update({
        'EMAIL_ANALYSIS_PROMPT': 'Analyze this email: {email_content}',  # Simplified prompt for testing
        'ERROR_MESSAGES': {
            'api_error': 'API Error: {error}'
        }
    })
    
    with patch('app_email_analyzer.get_analysis_session', return_value=mock_db_session), \
         patch('app_email_analyzer.get_email_session', return_value=mock_db_session), \
         patch('anthropic.Client') as mock_client_class, \
         patch.dict('os.environ', mock_env), \
         patch.dict('app_email_analyzer.API_CONFIG', mock_api_config):
        
        # Configure Anthropic mock
        mock_response = {
            'summary': 'Test summary',
            'category': ['work'],
            'priority_score': 3,
            'project': 'Test Project',
            'topic': 'Test Topic',
            'sentiment': 'neutral'
        }
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client
        
        analyzer = EmailAnalyzer(metrics_port=0)  # Disable metrics server for tests
        
        test_email = {
            'id': 'test1',
            'subject': 'Test Email',
            'content': 'Test content',
            'received_date': datetime.now().isoformat(),
            'thread_id': 'thread1',
            'labels': '["INBOX"]'
        }
        
        analysis = analyzer.analyze_email(test_email)
        assert analysis is not None
        assert isinstance(analysis, dict)
        assert analysis.get('summary') == 'Test summary'
        assert analysis.get('project') == 'Test Project'
        assert analysis.get('topic') == 'Test Topic'
