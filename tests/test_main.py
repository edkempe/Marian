#!/usr/bin/env python3
"""
Main Test Suite
--------------
Integration tests for core applications:
- app_get_mail.py
- app_email_analyzer.py
- app_email_reports.py
- app_email_self_log.py
"""

import os
import sqlite3
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import base64

# Import core applications
from app_get_mail import (
    get_gmail_service, init_database, fetch_emails,
    process_email, get_newest_email_date
)
from app_email_analyzer import EmailAnalyzer
from app_email_reports import EmailAnalytics
from app_email_self_log import EmailSelfAnalyzer
from models.email import Email
from models.email_analysis import EmailAnalysis

# Test database paths
TEST_EMAIL_DB = "test_db_email_store.db"
TEST_ANALYSIS_DB = "test_db_email_analysis.db"
TEST_LABELS_DB = "test_db_email_labels.db"

@pytest.fixture(scope="function")
def setup_test_dbs(monkeypatch):
    """Set up test databases."""
    print("\nSetting up test databases...")  # Debug print
    
    # Mock get_email_db to use test database
    def mock_get_email_db():
        return sqlite3.connect(TEST_EMAIL_DB)
    monkeypatch.setattr('app_get_mail.get_email_db', mock_get_email_db)
    
    # Initialize test databases
    conn = sqlite3.connect(TEST_EMAIL_DB)
    c = conn.cursor()
    
    # Create emails table with correct schema
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id TEXT PRIMARY KEY,
                  thread_id TEXT,
                  subject TEXT,
                  from_address TEXT,
                  to_address TEXT,
                  cc_address TEXT DEFAULT '',
                  bcc_address TEXT DEFAULT '',
                  received_date TEXT,
                  content TEXT,
                  labels TEXT,
                  has_attachments BOOLEAN DEFAULT 0,
                  full_api_response TEXT)''')
    conn.commit()
    conn.close()
    print("Test databases initialized")  # Debug print
    
    # Clean up after tests
    yield
    
    print("\nCleaning up test databases...")  # Debug print
    for db in [TEST_EMAIL_DB, TEST_ANALYSIS_DB, TEST_LABELS_DB]:
        if os.path.exists(db):
            try:
                os.remove(db)
                print(f"Removed {db}")  # Debug print
            except Exception as e:
                print(f"Error removing {db}: {e}")  # Debug print

@pytest.fixture
def mock_gmail_service(monkeypatch):
    """Mock Gmail API service."""
    mock_service = MagicMock()
    
    # Mock the messages.list() response
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        'messages': [{'id': 'test1'}, {'id': 'test2'}]
    }
    mock_service.users().messages().list.return_value = mock_list
    
    # Mock list_next to return None (no more pages)
    mock_service.users().messages().list_next.return_value = None
    
    # Mock the messages.get() response
    mock_get = MagicMock()
    mock_get.execute.return_value = {
        'id': 'test1',
        'threadId': 'thread1',
        'labelIds': ['INBOX'],
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': 'Test Email'},
                {'name': 'From', 'value': 'test@example.com'},
                {'name': 'To', 'value': 'me@example.com'},
                {'name': 'Date', 'value': datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}
            ],
            'body': {'data': base64.b64encode(b'Test email content').decode()}
        }
    }
    mock_service.users().messages().get.return_value = mock_get
    
    # Mock the get_gmail_service function
    def mock_get_service():
        print("Using mock Gmail service")  # Debug print
        return mock_service
    
    monkeypatch.setattr('app_get_mail.get_gmail_service', mock_get_service)
    
    # Mock the GmailAPI class
    mock_gmail_api = MagicMock()
    mock_gmail_api.return_value.service = mock_service
    monkeypatch.setattr('app_get_mail.GmailAPI', mock_gmail_api)
    
    return mock_service

def test_email_fetching(setup_test_dbs, mock_gmail_service):
    """Test email fetching functionality."""
    print("\nStarting email fetching test...")  # Debug print
    # Test fetching emails
    messages = fetch_emails(mock_gmail_service)
    print(f"Fetched {len(messages)} messages")  # Debug print
    assert len(messages) == 2
    assert messages[0]['id'] == 'test1'
    
    # Test processing email
    print("Processing test email...")  # Debug print
    conn = sqlite3.connect(TEST_EMAIL_DB)
    email_data = process_email(mock_gmail_service, 'test1', conn)
    print("Email processed")  # Debug print
    assert email_data is not None
    assert email_data['subject'] == 'Test Email'
    conn.close()
    print("Test completed successfully")  # Debug print

@patch('anthropic.Anthropic')
def test_email_analysis(mock_anthropic, setup_test_dbs):
    """Test email analysis functionality."""
    # Mock Anthropic API response
    mock_response = MagicMock()
    mock_response.content = [{
        'text': '''{
            "summary": "Test email summary",
            "category": ["test"],
            "priority_score": 3,
            "priority_reason": "test",
            "action_needed": false,
            "action_type": [],
            "action_deadline": null,
            "key_points": ["test point"],
            "people_mentioned": [],
            "links_found": [],
            "links_display": [],
            "project": null,
            "topic": null,
            "sentiment": "neutral",
            "confidence_score": 0.9
        }'''
    }]
    mock_anthropic.return_value.messages.create.return_value = mock_response
    
    # Test analysis
    analyzer = EmailAnalyzer()
    result = analyzer.analyze_email({
        'id': 'test1',
        'thread_id': 'thread1',
        'subject': 'Test Email',
        'content': 'Test content',
        'date': datetime.now().isoformat(),
        'labels': ['INBOX']
    })
    
    assert result is not None
    assert result.summary == "Test email summary"
    assert result.category == ["test"]
    assert result.priority_score == 3

def test_email_reports(setup_test_dbs):
    """Test email reporting functionality."""
    # Prepare test data
    conn = sqlite3.connect(TEST_EMAIL_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emails (id, thread_id, subject, from_address, to_address, received_date, content, labels)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('test1', 'thread1', 'Test Email', 'test@example.com', 'me@example.com',
          datetime.now().isoformat(), 'Test content', '["INBOX"]'))
    conn.commit()
    conn.close()
    
    # Test reports
    analytics = EmailAnalytics()
    total = analytics.get_total_emails()
    assert total == 1
    
    top_senders = analytics.get_top_senders()
    assert len(top_senders) == 1
    assert top_senders[0][0] == 'test@example.com'

def test_self_email_analysis(setup_test_dbs):
    """Test self-email analysis functionality."""
    # Prepare test data
    conn = sqlite3.connect(TEST_EMAIL_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emails (id, thread_id, subject, from_address, to_address, received_date, content, labels)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('test1', 'thread1', 'Note to Self', 'me@example.com', 'me@example.com',
          datetime.now().isoformat(), 'Self reminder', '["INBOX"]'))
    conn.commit()
    conn.close()
    
    # Test self-email analysis
    analyzer = EmailSelfAnalyzer(db_path=TEST_EMAIL_DB)
    with patch.object(analyzer, '_get_user_email', return_value='me@example.com'):
        emails = analyzer.get_self_emails()
        assert len(emails) == 1
        assert emails[0]['subject'] == 'Note to Self'