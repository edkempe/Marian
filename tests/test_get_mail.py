"""Tests for email fetching functionality."""
import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from models.email import Email
from app_get_mail import (
    init_database, get_label_id, fetch_emails,
    process_email, get_oldest_email_date,
    get_newest_email_date, count_emails,
    list_labels
)

@pytest.fixture
def mock_gmail_service():
    """Create a mock Gmail service."""
    mock_service = MagicMock()
    
    # Mock users().labels().list()
    mock_labels = MagicMock()
    mock_labels.execute.return_value = {
        'labels': [
            {'id': 'IMPORTANT', 'name': 'IMPORTANT'},
            {'id': 'INBOX', 'name': 'INBOX'}
        ]
    }
    mock_service.users.return_value.labels.return_value.list.return_value = mock_labels
    
    # Mock users().messages().list()
    mock_messages = MagicMock()
    mock_messages.execute.return_value = {
        'messages': [{'id': '123', 'threadId': 'thread123'}],
        'nextPageToken': None
    }
    mock_service.users.return_value.messages.return_value.list.return_value = mock_messages
    
    # Mock users().messages().get()
    mock_message = MagicMock()
    mock_message.execute.return_value = {
        'id': '123',
        'threadId': 'thread123',
        'labelIds': ['IMPORTANT'],
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'To', 'value': 'recipient@example.com'},
                {'name': 'Subject', 'value': 'Test Email'},
                {'name': 'Date', 'value': '2024-12-23T10:00:00Z'}
            ]
        }
    }
    mock_service.users.return_value.messages.return_value.get.return_value = mock_message
    
    return mock_service

@pytest.fixture
def mock_db():
    """Create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id TEXT PRIMARY KEY,
                  thread_id TEXT NOT NULL,
                  subject TEXT DEFAULT 'No Subject',
                  from_address TEXT NOT NULL,
                  to_address TEXT NOT NULL,
                  cc_address TEXT DEFAULT '',
                  bcc_address TEXT DEFAULT '',
                  received_date TIMESTAMP WITH TIME ZONE NOT NULL,
                  content TEXT DEFAULT '',
                  labels TEXT DEFAULT '',
                  has_attachments BOOLEAN NOT NULL DEFAULT 0,
                  full_api_response TEXT DEFAULT '{}')''')  # Complete Gmail API response for future reference
    conn.commit()
    return conn

def test_init_database():
    """Test database initialization."""
    with patch('sqlite3.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Call init_database
        init_database()
        
        # Verify the database connection was made
        mock_connect.assert_called_once_with('db_email_store.db')
        
        # Verify table creation
        mock_cursor.execute.assert_any_call('''
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                thread_id TEXT,
                subject TEXT,
                from_address TEXT,
                to_address TEXT,
                received_date TEXT,
                content TEXT,
                labels TEXT,
                raw_json TEXT
            )
        ''')

def test_get_label_id_success(mock_gmail_service):
    """Test successful label ID retrieval."""
    label_id = get_label_id(mock_gmail_service, 'IMPORTANT')
    assert label_id == 'IMPORTANT'

def test_get_label_id_not_found(mock_gmail_service):
    """Test when label is not found."""
    label_id = get_label_id(mock_gmail_service, 'NonexistentLabel')
    assert label_id is None

def test_fetch_emails_success(mock_gmail_service):
    """Test successful email fetching."""
    emails = fetch_emails(mock_gmail_service)
    assert len(emails) == 1
    assert emails[0]['id'] == '123'

def test_fetch_emails_with_label(mock_gmail_service):
    """Test fetching emails with label filter."""
    emails = fetch_emails(mock_gmail_service, label='IMPORTANT')
    assert len(emails) == 1
    assert emails[0]['id'] == '123'

def test_process_email(mock_gmail_service, mock_db):
    """Test email processing and storage."""
    msg_id = '123'
    process_email(mock_gmail_service, msg_id, mock_db)
    
    cursor = mock_db.cursor()
    cursor.execute('SELECT * FROM emails WHERE id = ?', (msg_id,))
    email_data = cursor.fetchone()
    
    assert email_data is not None
    assert email_data[0] == msg_id  # id
    assert email_data[2] == 'Test Email'  # subject
    assert email_data[3] == 'sender@example.com'  # sender
    assert email_data[4] == 'recipient@example.com'  # recipient

def test_get_oldest_email_date(mock_db):
    """Test getting oldest email date."""
    cursor = mock_db.cursor()
    cursor.execute('''INSERT INTO emails 
                     (id, thread_id, from_address, to_address, received_date) 
                     VALUES (?, ?, ?, ?, ?)''', 
                  ('1', 'thread1', 'sender1@example.com', 'recipient1@example.com', '2024-12-18T10:00:00Z'))
    cursor.execute('''INSERT INTO emails 
                     (id, thread_id, from_address, to_address, received_date) 
                     VALUES (?, ?, ?, ?, ?)''',
                  ('2', 'thread2', 'sender2@example.com', 'recipient2@example.com', '2024-12-19T10:00:00Z'))
    mock_db.commit()
    
    oldest_date = get_oldest_email_date(mock_db)
    assert oldest_date.isoformat().replace('+00:00', 'Z') == '2024-12-18T10:00:00Z'

def test_get_newest_email_date(mock_db):
    """Test getting newest email date."""
    cursor = mock_db.cursor()
    cursor.execute('''INSERT INTO emails 
                     (id, thread_id, from_address, to_address, received_date) 
                     VALUES (?, ?, ?, ?, ?)''',
                  ('1', 'thread1', 'sender1@example.com', 'recipient1@example.com', '2024-12-18T10:00:00Z'))
    cursor.execute('''INSERT INTO emails 
                     (id, thread_id, from_address, to_address, received_date) 
                     VALUES (?, ?, ?, ?, ?)''',
                  ('2', 'thread2', 'sender2@example.com', 'recipient2@example.com', '2024-12-19T10:00:00Z'))
    mock_db.commit()
    
    newest_date = get_newest_email_date(mock_db)
    assert newest_date.isoformat().replace('+00:00', 'Z') == '2024-12-19T10:00:00Z'

def test_count_emails(mock_db):
    """Test email counting."""
    cursor = mock_db.cursor()
    cursor.execute('''INSERT INTO emails 
                     (id, thread_id, from_address, to_address, received_date) 
                     VALUES (?, ?, ?, ?, ?)''',
                  ('1', 'thread1', 'sender1@example.com', 'recipient1@example.com', '2024-12-18T10:00:00Z'))
    mock_db.commit()
    
    count = count_emails(mock_db)
    assert count == 1

def test_list_labels(mock_gmail_service):
    """Test listing Gmail labels."""
    labels = list_labels(mock_gmail_service)
    assert len(labels) == 2
    assert 'IMPORTANT' in [label['name'] for label in labels]
    assert 'INBOX' in [label['name'] for label in labels]
