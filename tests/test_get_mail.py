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
from shared_lib.constants import DATABASE_CONFIG, API_CONFIG

@pytest.fixture
def mock_gmail_service():
    """Create a mock Gmail service."""
    mock_service = MagicMock()
    
    # Mock the service chain
    mock_users = MagicMock()
    mock_labels = MagicMock()
    mock_messages = MagicMock()
    
    # Set up the chain
    mock_service.users = MagicMock(return_value=mock_users)
    mock_users.labels = MagicMock(return_value=mock_labels)
    mock_users.messages = MagicMock(return_value=mock_messages)
    
    # Mock labels list
    mock_labels_response = {
        'labels': [
            {'id': 'INBOX', 'name': 'INBOX'},
            {'id': 'SENT', 'name': 'SENT'},
            {'id': 'IMPORTANT', 'name': 'IMPORTANT'}
        ]
    }
    mock_labels.list().execute.return_value = mock_labels_response
    
    # Mock messages list
    mock_messages_response = {
        'messages': [{'id': '123', 'threadId': 'thread123'}],
        'nextPageToken': None
    }
    mock_messages.list().execute.return_value = mock_messages_response
    
    # Mock message get
    mock_message_response = {
        'id': '123',
        'threadId': 'thread123',
        'labelIds': ['INBOX'],
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'To', 'value': 'recipient@example.com'},
                {'name': 'Subject', 'value': 'Test Email'},
                {'name': 'Date', 'value': '2024-01-01T00:00:00Z'}
            ],
            'body': {'data': 'VGVzdCBjb250ZW50'}  # Base64 "Test content"
        }
    }
    mock_messages.get().execute.return_value = mock_message_response
    
    return mock_service

@pytest.fixture
def mock_db():
    """Create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create tables using the same schema as the real database
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            thread_id TEXT,
            subject TEXT,
            from_address TEXT,
            to_address TEXT,
            content TEXT,
            received_date DATETIME,
            labels TEXT
        )
    ''')
    
    conn.commit()
    return conn

def test_init_database():
    """Test database initialization."""
    db_path = ':memory:'  # Use in-memory database for testing
    init_database(db_path)
    
    # Verify database was created with correct schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if emails table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='emails'
    """)
    assert cursor.fetchone() is not None
    
    # Check table schema
    cursor.execute("PRAGMA table_info(emails)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    expected_columns = [
        'id', 'thread_id', 'subject', 'from_address', 
        'to_address', 'content', 'received_date', 'labels'
    ]
    for col in expected_columns:
        assert col in column_names
    
    conn.close()

@pytest.mark.parametrize('label_name,expected_id', [
    ('INBOX', 'INBOX'),
    ('SENT', 'SENT'),
    ('IMPORTANT', 'IMPORTANT'),
    ('NONEXISTENT', None),
    ('', None),
    (None, None),
])
def test_get_label_id(mock_gmail_service, label_name, expected_id):
    """Test label ID retrieval with various inputs."""
    assert get_label_id(mock_gmail_service, label_name) == expected_id

def test_get_label_id_error(mock_gmail_service):
    """Test handling of API errors in label ID retrieval."""
    mock_gmail_service.users().labels().list.side_effect = Exception('API Error')
    assert get_label_id(mock_gmail_service, 'INBOX') is None

def test_fetch_emails_success(mock_gmail_service):
    """Test successful email fetching."""
    messages = fetch_emails(mock_gmail_service)
    assert len(messages) == 1
    assert messages[0]['id'] == '123'

def test_fetch_emails_with_label(mock_gmail_service):
    """Test fetching emails with label filter."""
    messages = fetch_emails(mock_gmail_service, label='IMPORTANT')
    assert len(messages) == 1
    assert messages[0]['id'] == '123'

def test_process_email(mock_gmail_service, mock_db):
    """Test email processing and storage."""
    cursor = mock_db.cursor()
    
    # Process a test email
    email_data = {
        'id': '123',
        'threadId': 'thread123',
        'labelIds': ['INBOX']
    }
    process_email(mock_gmail_service, email_data, cursor)
    
    # Verify email was stored correctly
    cursor.execute("SELECT id, thread_id FROM emails WHERE id = '123'")
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == '123'
    assert result[1] == 'thread123'

def test_get_oldest_email_date(mock_db):
    """Test getting oldest email date."""
    cursor = mock_db.cursor()
    
    # Insert test data
    old_date = (datetime.now() - timedelta(days=30)).isoformat()
    new_date = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO emails (id, received_date) VALUES (?, ?), (?, ?)",
        ('1', old_date, '2', new_date)
    )
    mock_db.commit()
    
    oldest_date = get_oldest_email_date(cursor)
    assert oldest_date.date() == datetime.fromisoformat(old_date).date()

def test_get_newest_email_date(mock_db):
    """Test getting newest email date."""
    cursor = mock_db.cursor()
    
    # Insert test data
    old_date = (datetime.now() - timedelta(days=30)).isoformat()
    new_date = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO emails (id, received_date) VALUES (?, ?), (?, ?)",
        ('1', old_date, '2', new_date)
    )
    mock_db.commit()
    
    newest_date = get_newest_email_date(cursor)
    assert newest_date.date() == datetime.fromisoformat(new_date).date()

def test_count_emails(mock_db):
    """Test email counting."""
    cursor = mock_db.cursor()
    
    # Insert test data
    cursor.execute(
        "INSERT INTO emails (id) VALUES (?), (?)",
        ('1', '2')
    )
    mock_db.commit()
    
    count = count_emails(cursor)
    assert count == 2

def test_list_labels(mock_gmail_service):
    """Test listing Gmail labels."""
    labels = list_labels(mock_gmail_service)
    assert len(labels) == 3
    assert any(label['name'] == 'INBOX' for label in labels)
    assert any(label['name'] == 'SENT' for label in labels)
    assert any(label['name'] == 'IMPORTANT' for label in labels)
