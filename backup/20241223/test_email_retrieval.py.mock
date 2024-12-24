"""Tests for email retrieval functionality."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from app_get_mail import fetch_emails, process_email
from models.email import Email
from constants import EMAIL_CONFIG

TEST_MESSAGES = {
    'msg1': {
        'id': 'msg1',
        'threadId': 'thread1',
        'labelIds': ['INBOX'],
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender1@example.com'},
                {'name': 'To', 'value': 'recipient1@example.com'},
                {'name': 'Subject', 'value': 'Test Email 1'},
                {'name': 'Date', 'value': '2024-01-01T00:00:00Z'}
            ],
            'body': {'data': 'VGVzdCBjb250ZW50IDE='}  # "Test content 1"
        }
    },
    'msg2': {
        'id': 'msg2',
        'threadId': 'thread2',
        'labelIds': ['SENT'],
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender2@example.com'},
                {'name': 'To', 'value': 'recipient2@example.com'},
                {'name': 'Subject', 'value': 'Test Email 2'},
                {'name': 'Date', 'value': '2024-01-02T00:00:00Z'}
            ],
            'body': {'data': 'VGVzdCBjb250ZW50IDI='}  # "Test content 2"
        }
    }
}

@pytest.fixture
def mock_gmail():
    """Create a mock Gmail service with predefined responses."""
    with patch('lib_gmail.GmailAPI') as mock:
        service = MagicMock()
        mock.return_value.service = service
        
        # Mock messages.list
        list_response = MagicMock()
        list_response.execute.return_value = {
            'messages': [
                {'id': 'msg1', 'threadId': 'thread1'},
                {'id': 'msg2', 'threadId': 'thread2'}
            ]
        }
        service.users.return_value.messages.return_value.list.return_value = list_response
        
        # Mock messages.get
        def mock_get(userId, id, **kwargs):
            response = MagicMock()
            response.execute.return_value = TEST_MESSAGES[id]
            return response
        
        service.users.return_value.messages.return_value.get.side_effect = mock_get
        
        yield service

def test_fetch_emails_success(mock_gmail):
    """Test successful email fetching."""
    messages = fetch_emails(mock_gmail)
    assert len(messages) == 2
    assert messages[0]['id'] == 'msg1'
    assert messages[1]['id'] == 'msg2'

def test_fetch_emails_with_dates(mock_gmail):
    """Test fetching emails with date filters."""
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    messages = fetch_emails(mock_gmail, start_date=start_date, end_date=end_date)
    assert len(messages) == 2

def test_fetch_emails_with_label(mock_gmail):
    """Test fetching emails with label filter."""
    messages = fetch_emails(mock_gmail, label='INBOX')
    assert len(messages) == 2

def test_fetch_emails_error(mock_gmail):
    """Test handling of API errors in email fetching."""
    mock_gmail.users.return_value.messages.return_value.list.return_value.execute.side_effect = Exception('API Error')
    messages = fetch_emails(mock_gmail)
    assert messages == []

@pytest.mark.parametrize('msg_id,expected_subject', [
    ('msg1', 'Test Email 1'),
    ('msg2', 'Test Email 2'),
])
def test_process_email(mock_gmail, test_db_session, msg_id, expected_subject):
    """Test processing individual emails."""
    process_email(mock_gmail, msg_id, test_db_session)
    email = test_db_session.query(Email).filter_by(id=msg_id).first()
    assert email is not None
    assert email.subject == expected_subject

def test_process_email_error(mock_gmail, test_db_session):
    """Test handling of API errors in email processing."""
    mock_gmail.users.return_value.messages.return_value.get.side_effect = Exception('API Error')
    with pytest.raises(Exception):
        process_email(mock_gmail, 'msg1', test_db_session)
