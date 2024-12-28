"""Tests for email fetching functionality."""
import pytest
import sqlite3
from datetime import datetime, timedelta
from models.email import Email
from app_get_mail import (
    init_database, get_label_id, fetch_emails,
    process_email, get_oldest_email_date,
    get_newest_email_date, count_emails,
    list_labels
)
from shared_lib.gmail_lib import GmailAPI
from shared_lib.constants import DATABASE_CONFIG, API_CONFIG

@pytest.fixture
def gmail_service():
    """Get real Gmail service."""
    return GmailAPI().get_service()

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
    
    # Verify required columns exist
    column_names = [col[1] for col in columns]
    required_columns = [
        'id', 'thread_id', 'subject', 'from_address',
        'to_address', 'content', 'received_date', 'labels'
    ]
    for col in required_columns:
        assert col in column_names

@pytest.mark.parametrize("label_name,expected_id", [
    ('INBOX', 'INBOX'),
    ('SENT', 'SENT'),
    ('IMPORTANT', 'IMPORTANT'),
    ('NONEXISTENT', None),
    ('', None),
    (None, None),
])
def test_get_label_id(gmail_service, label_name, expected_id):
    """Test label ID retrieval with various inputs."""
    result = get_label_id(gmail_service, label_name)
    if expected_id:
        assert result is not None
    else:
        assert result is None

def test_get_label_id_error(gmail_service):
    """Test handling of API errors in label ID retrieval."""
    # Test with invalid service
    result = get_label_id(None, 'INBOX')
    assert result is None

def test_fetch_emails_success(gmail_service):
    """Test successful email fetching."""
    messages = fetch_emails(gmail_service, max_results=1)
    assert len(messages) > 0
    assert 'id' in messages[0]

def test_fetch_emails_with_label(gmail_service):
    """Test fetching emails with label filter."""
    messages = fetch_emails(gmail_service, label='INBOX', max_results=1)
    assert len(messages) > 0
    assert 'id' in messages[0]

def test_process_email(gmail_service, mock_db):
    """Test email processing and storage."""
    # First fetch an email
    messages = fetch_emails(gmail_service, max_results=1)
    assert len(messages) > 0
    
    # Process the email
    msg_id = messages[0]['id']
    process_email(gmail_service, msg_id, mock_db)
    
    # Verify email was stored
    cursor = mock_db.cursor()
    cursor.execute("SELECT * FROM emails WHERE id = ?", (msg_id,))
    result = cursor.fetchone()
    assert result is not None

def test_get_oldest_email_date(mock_db):
    """Test getting oldest email date."""
    cursor = mock_db.cursor()
    
    # Insert test data
    test_dates = [
        '2024-01-01T00:00:00Z',
        '2024-01-02T00:00:00Z',
        '2024-01-03T00:00:00Z'
    ]
    for i, date in enumerate(test_dates):
        cursor.execute(
            "INSERT INTO emails (id, received_date) VALUES (?, ?)",
            (f'test{i}', date)
        )
    mock_db.commit()
    
    oldest_date = get_oldest_email_date(mock_db)
    assert oldest_date == datetime.strptime(test_dates[0], '%Y-%m-%dT%H:%M:%SZ')

def test_get_newest_email_date(mock_db):
    """Test getting newest email date."""
    cursor = mock_db.cursor()
    
    # Insert test data
    test_dates = [
        '2024-01-01T00:00:00Z',
        '2024-01-02T00:00:00Z',
        '2024-01-03T00:00:00Z'
    ]
    for i, date in enumerate(test_dates):
        cursor.execute(
            "INSERT INTO emails (id, received_date) VALUES (?, ?)",
            (f'test{i}', date)
        )
    mock_db.commit()
    
    newest_date = get_newest_email_date(mock_db)
    assert newest_date == datetime.strptime(test_dates[-1], '%Y-%m-%dT%H:%M:%SZ')

def test_count_emails(mock_db):
    """Test email counting."""
    cursor = mock_db.cursor()
    
    # Insert test data
    for i in range(5):
        cursor.execute(
            "INSERT INTO emails (id) VALUES (?)",
            (f'test{i}',)
        )
    mock_db.commit()
    
    count = count_emails(mock_db)
    assert count == 5

def test_list_labels(gmail_service):
    """Test listing Gmail labels."""
    labels = list_labels(gmail_service)
    assert len(labels) > 0
    assert all('id' in label and 'name' in label for label in labels)
