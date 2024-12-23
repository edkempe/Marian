"""Tests for Gmail email fetching functionality."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from ..app_get_mail import (
    get_gmail_service,
    init_database,
    get_label_id,
    fetch_emails,
    process_email
)
from ..models.email import Email

@pytest.fixture
def mock_gmail_service():
    """Mock Gmail service."""
    mock_service = Mock()
    users = Mock()
    messages = Mock()
    labels = Mock()
    list_request = Mock()
    get_request = Mock()
    
    # Configure mock chain
    mock_service.users = Mock(return_value=users)
    users.messages = Mock(return_value=messages)
    users.labels = Mock(return_value=labels)
    messages.list = Mock(return_value=list_request)
    messages.get = Mock(return_value=get_request)
    labels.list = Mock(return_value=Mock())
    
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
            ],
            'body': {'data': 'VGVzdCBlbWFpbCBib2R5'},  # Base64 encoded "Test email body"
            'parts': []
        }
    }
    
    return mock_service

@pytest.fixture
def mock_db():
    """Create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id TEXT PRIMARY KEY,
                  subject TEXT,
                  sender TEXT,
                  date TEXT,
                  body TEXT,
                  labels TEXT,
                  raw_data TEXT)''')
    conn.commit()
    return conn

def test_init_database():
    """Test database initialization."""
    with patch('sqlite3.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        conn = init_database()
        
        mock_connect.assert_called_once_with('db_email_store.db')
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

def test_get_label_id_success(mock_gmail_service):
    """Test successful label ID retrieval."""
    mock_gmail_service.users().labels().list().execute.return_value = {
        'labels': [
            {'id': 'Label_1', 'name': 'Important'},
            {'id': 'Label_2', 'name': 'Work'}
        ]
    }
    
    label_id = get_label_id(mock_gmail_service, 'Important')
    assert label_id == 'Label_1'

def test_get_label_id_not_found(mock_gmail_service):
    """Test when label is not found."""
    mock_gmail_service.users().labels().list().execute.return_value = {
        'labels': [
            {'id': 'Label_1', 'name': 'Important'},
            {'id': 'Label_2', 'name': 'Work'}
        ]
    }
    
    label_id = get_label_id(mock_gmail_service, 'NonexistentLabel')
    assert label_id is None

def test_fetch_emails_success(mock_gmail_service):
    """Test successful email fetching."""
    emails = fetch_emails(mock_gmail_service)
    assert len(emails) == 2
    assert emails[0]['id'] == '123'

def test_fetch_emails_with_label(mock_gmail_service):
    """Test fetching emails with label filter."""
    emails = fetch_emails(mock_gmail_service, label='IMPORTANT')
    assert len(emails) == 2
    mock_gmail_service.users().messages().list.assert_called_with(
        userId='me',
        q='label:IMPORTANT',
        maxResults=50
    )

def test_process_email(mock_gmail_service, mock_db):
    """Test email processing and storage."""
    msg_id = '123'
    process_email(mock_gmail_service, msg_id, mock_db)
    
    cursor = mock_db.cursor()
    cursor.execute('SELECT * FROM emails WHERE id = ?', (msg_id,))
    email_data = cursor.fetchone()
    
    assert email_data is not None
    assert email_data[0] == msg_id  # id
    assert email_data[1] == 'Test Subject'  # subject
    assert email_data[2] == 'sender@example.com'  # sender

def test_get_oldest_email_date(mock_db):
    """Test getting oldest email date."""
    cursor = mock_db.cursor()
    cursor.execute('INSERT INTO emails (id, date) VALUES (?, ?)', 
                  ('1', '2024-12-18T10:00:00Z'))
    cursor.execute('INSERT INTO emails (id, date) VALUES (?, ?)', 
                  ('2', '2024-12-19T10:00:00Z'))
    mock_db.commit()
    
    oldest_date = get_oldest_email_date(mock_db)
    assert oldest_date.strftime('%Y-%m-%d') == '2024-12-18'

def test_get_newest_email_date(mock_db):
    """Test getting newest email date."""
    cursor = mock_db.cursor()
    cursor.execute('INSERT INTO emails (id, date) VALUES (?, ?)', 
                  ('1', '2024-12-18T10:00:00Z'))
    cursor.execute('INSERT INTO emails (id, date) VALUES (?, ?)', 
                  ('2', '2024-12-19T10:00:00Z'))
    mock_db.commit()
    
    newest_date = get_newest_email_date(mock_db)
    assert newest_date.strftime('%Y-%m-%d') == '2024-12-19'

def test_count_emails(mock_db):
    """Test email counting."""
    cursor = mock_db.cursor()
    cursor.execute('INSERT INTO emails (id) VALUES (?)', ('1',))
    cursor.execute('INSERT INTO emails (id) VALUES (?)', ('2',))
    mock_db.commit()
    
    count = count_emails(mock_db)
    assert count == 2

def test_list_labels(mock_gmail_service):
    """Test listing Gmail labels."""
    mock_gmail_service.users().labels().list().execute.return_value = {
        'labels': [
            {'id': 'Label_1', 'name': 'Important'},
            {'id': 'Label_2', 'name': 'Work'}
        ]
    }
    
    labels = list_labels(mock_gmail_service)
    assert len(labels) == 2
    assert 'Important' in [label['name'] for label in labels]
