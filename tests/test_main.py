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
def setup_test_dbs():
    """Set up test databases."""
    # Initialize test databases
    conn = sqlite3.connect(TEST_EMAIL_DB)
    init_database(conn)
    conn.close()
    
    # Clean up after tests
    yield
    
    for db in [TEST_EMAIL_DB, TEST_ANALYSIS_DB, TEST_LABELS_DB]:
        if os.path.exists(db):
            os.remove(db)

@pytest.fixture
def mock_gmail_service():
    """Mock Gmail API service."""
    service = MagicMock()
    service.users().messages().list().execute.return_value = {
        'messages': [{'id': 'test1'}, {'id': 'test2'}]
    }
    service.users().messages().get().execute.return_value = {
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
            'body': {'data': 'Test email content'}
        }
    }
    return service

def test_email_fetching(setup_test_dbs, mock_gmail_service):
    """Test email fetching functionality."""
    # Test fetching emails
    messages = fetch_emails(mock_gmail_service)
    assert len(messages) == 2
    assert messages[0]['id'] == 'test1'
    
    # Test processing email
    conn = sqlite3.connect(TEST_EMAIL_DB)
    email_data = process_email(mock_gmail_service, 'test1', conn)
    assert email_data is not None
    assert email_data['subject'] == 'Test Email'
    conn.close()

@patch('anthropic.Anthropic')
def test_email_analysis(mock_anthropic, setup_test_dbs):
    """Test email analysis functionality."""
    # Mock Anthropic API response
    mock_response = MagicMock()
    mock_response.content = [{
        'text': '''{
            "summary": "Test email summary",
            "category": ["test"],
            "priority": {"score": 3, "reason": "test"},
            "action": {"needed": false, "type": [], "deadline": null},
            "key_points": ["test point"],
            "people_mentioned": [],
            "links_found": [],
            "links_display": [],
            "context": {"project": null, "topic": null, "ref_docs": null},
            "sentiment": "neutral",
            "confidence_score": 0.9
        }'''
    }]
    mock_anthropic.return_value.messages.create.return_value = mock_response
    
    # Test analysis
    analyzer = EmailAnalyzer()
    result = analyzer.analyze_email(
        email_id='test1',
        subject='Test Email',
        body='Test content'
    )
    
    assert result is not None
    assert result.summary == "Test email summary"
    assert result.sentiment == "neutral"

def test_email_reports(setup_test_dbs):
    """Test email reporting functionality."""
    # Prepare test data
    conn = sqlite3.connect(TEST_EMAIL_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emails (id, thread_id, subject, sender, recipient, date, body, labels)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('test1', 'thread1', 'Test Email', 'test@example.com', 'me@example.com',
          datetime.now().isoformat(), 'Test content', '["INBOX"]'))
    conn.commit()
    conn.close()
    
    # Test reports
    analytics = EmailAnalytics(TEST_EMAIL_DB, TEST_LABELS_DB, TEST_ANALYSIS_DB)
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
        INSERT INTO emails (id, thread_id, subject, sender, recipient, date, body, labels)
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