"""Tests for email processing functionality."""
import pytest
from unittest.mock import Mock, patch, mock_open, call
import json
from datetime import datetime
from process_emails import (
    get_emails,
    parse_email,
    save_processed_emails,
    main
)

@pytest.fixture
def mock_gmail_service():
    """Mock Gmail service."""
    # Create mock objects
    mock_service = Mock()
    users = Mock()
    messages = Mock()
    list_request = Mock()
    get_request = Mock()
    
    # Configure mock chain
    mock_service.users = Mock(return_value=users)
    users.messages = Mock(return_value=messages)
    messages.list = Mock(return_value=list_request)
    messages.get = Mock(return_value=get_request)
    
    # Configure responses
    list_request.execute.return_value = {
        'messages': [
            {'id': '123', 'threadId': 'thread123'},
            {'id': '456', 'threadId': 'thread456'}
        ]
    }
    
    get_request.execute.return_value = {
        'id': '123',
        'threadId': 'thread123',
        'labelIds': ['INBOX', 'IMPORTANT'],
        'snippet': 'Email content preview...',
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': 'Test Subject'},
                {'name': 'Date', 'value': 'Thu, 19 Dec 2024 19:05:00 -0700'},
                {'name': 'From', 'value': 'sender@example.com'}
            ]
        }
    }
    
    return mock_service

def test_get_emails_success(mock_gmail_service):
    """Test successful email fetching."""
    emails = get_emails(mock_gmail_service, max_results=2)
    
    assert len(emails) == 2
    assert emails[0]['id'] == '123'
    assert emails[0]['threadId'] == 'thread123'
    
    # Verify service calls
    mock_gmail_service.users().messages().list.assert_called_with(
        userId='me',
        q='from:me',
        maxResults=2
    )

def test_get_emails_no_messages(mock_gmail_service):
    """Test when no emails are found."""
    mock_gmail_service.users().messages().list().execute.return_value = {}
    
    emails = get_emails(mock_gmail_service)
    
    assert len(emails) == 0

def test_get_emails_error(mock_gmail_service):
    """Test error handling in email fetching."""
    mock_gmail_service.users().messages().list().execute.side_effect = Exception("API Error")
    
    emails = get_emails(mock_gmail_service)
    
    assert len(emails) == 0

def test_parse_email():
    """Test email parsing functionality."""
    test_message = {
        'id': '123',
        'threadId': 'thread123',
        'labelIds': ['INBOX', 'IMPORTANT'],
        'snippet': 'Email content preview...',
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': 'Test Subject'},
                {'name': 'Date', 'value': 'Thu, 19 Dec 2024 19:05:00 -0700'},
                {'name': 'From', 'value': 'sender@example.com'}
            ]
        }
    }
    
    parsed = parse_email(test_message)
    
    assert parsed['id'] == '123'
    assert parsed['thread_id'] == 'thread123'
    assert parsed['subject'] == 'Test Subject'
    assert parsed['date'] == 'Thu, 19 Dec 2024 19:05:00 -0700'
    assert parsed['from'] == 'sender@example.com'
    assert 'Email content preview...' in parsed['snippet']
    assert isinstance(parsed['labels'], list)

def test_parse_email_missing_fields():
    """Test email parsing with missing fields."""
    test_message = {
        'id': '123',
        'threadId': 'thread123',
        'payload': {
            'headers': []
        }
    }
    
    parsed = parse_email(test_message)
    
    assert parsed['id'] == '123'
    assert parsed['subject'] == 'No Subject'
    assert parsed['date'] is None
    assert parsed['from'] is None
    assert parsed['labels'] == []
    assert parsed['snippet'] == ''

@patch('builtins.open', new_callable=mock_open)
def test_save_processed_emails(mock_file):
    """Test saving processed emails to file."""
    test_emails = [
        {
            'id': '123',
            'subject': 'Test Subject',
            'date': 'Thu, 19 Dec 2024 19:05:00 -0700'
        }
    ]
    
    save_processed_emails(test_emails, 'test_output.json')
    
    # Verify file operations
    mock_file.assert_called_once_with('test_output.json', 'w', encoding='utf-8')
    
    # Get all write calls
    write_calls = mock_file().write.call_args_list
    written_content = ''.join(call_args[0][0] for call_args in write_calls)
    
    # Verify JSON content
    parsed_content = json.loads(written_content)
    assert len(parsed_content) == 1
    assert parsed_content[0]['id'] == '123'
    assert parsed_content[0]['subject'] == 'Test Subject'

@patch('process_emails.get_gmail_service')
@patch('process_emails.get_emails')
@patch('process_emails.save_processed_emails')
def test_main_success(mock_save, mock_get_emails, mock_get_service):
    """Test main function success path."""
    # Mock service and email data
    mock_service = Mock()
    mock_get_service.return_value = mock_service
    
    test_messages = [
        {
            'id': '123',
            'threadId': 'thread123',
            'labelIds': ['INBOX'],
            'snippet': 'Test content',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'}
                ]
            }
        }
    ]
    mock_get_emails.return_value = test_messages
    
    # Run main function
    main()
    
    # Verify function calls
    mock_get_service.assert_called_once()
    mock_get_emails.assert_called_once_with(mock_service)
    mock_save.assert_called_once()
    
    # Verify saved data
    saved_emails = mock_save.call_args[0][0]
    assert len(saved_emails) == 1
    assert saved_emails[0]['id'] == '123'

@patch('process_emails.get_gmail_service')
@patch('process_emails.get_emails')
def test_main_no_emails(mock_get_emails, mock_get_service):
    """Test main function when no emails are found."""
    mock_get_emails.return_value = []
    
    main()
    
    mock_get_service.assert_called_once()
    mock_get_emails.assert_called_once()
