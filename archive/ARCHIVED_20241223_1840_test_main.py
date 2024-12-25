"""Test module for email processing and analysis."""

import os
from datetime import datetime, timedelta
import json
import base64
from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session, sessionmaker

# Import models first to ensure they are registered with SQLAlchemy
from models.base import Base
from models.email import Email
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel

# Import database utilities
from database.config import get_email_session, get_analysis_session, init_db

# Import core applications
from app_get_mail import (
    get_gmail_service, init_database, fetch_emails,
    process_email, get_newest_email_date, GmailAPI
)
from app_email_analyzer import EmailAnalyzer
from app_email_reports import EmailAnalytics
from app_email_self_log import EmailSelfAnalyzer
from constants import DATABASE_CONFIG, API_CONFIG

# Test database paths - use the same names as production but with test_ prefix
TEST_EMAIL_DB = "test_" + DATABASE_CONFIG['EMAIL_DB_FILE']
TEST_ANALYSIS_DB = "test_" + DATABASE_CONFIG['ANALYSIS_DB_FILE']

@pytest.fixture(scope="function")
def setup_test_dbs(monkeypatch):
    """Set up test databases."""
    print("\nSetting up test databases...")

    # Clean up any existing test databases
    if os.path.exists(TEST_EMAIL_DB):
        os.remove(TEST_EMAIL_DB)
    if os.path.exists(TEST_ANALYSIS_DB):
        os.remove(TEST_ANALYSIS_DB)

    # Set up test database URLs
    monkeypatch.setenv('EMAIL_DB_URL', f'sqlite:///{TEST_EMAIL_DB}')
    monkeypatch.setenv('ANALYSIS_DB_URL', f'sqlite:///{TEST_ANALYSIS_DB}')

    # Import models to ensure they are registered with SQLAlchemy
    from models.base import Base
    from models.email_analysis import EmailAnalysis
    from models.email import Email
    from models.gmail_label import GmailLabel

    # Initialize databases
    init_db()

    # Verify tables exist and have correct columns
    email_engine = create_engine(f'sqlite:///{TEST_EMAIL_DB}')
    inspector = inspect(email_engine)
    tables = inspector.get_table_names()
    print(f"Email DB Tables: {tables}")
    
    if not tables:
        print("No tables found in email database. Creating tables...")
        Base.metadata.create_all(bind=email_engine)
        tables = inspector.get_table_names()
        print(f"Email DB Tables after creation: {tables}")
    
    if 'emails' in tables:
        columns = [col['name'] for col in inspector.get_columns('emails')]
        print(f"Emails table columns: {columns}")
        
        # Verify required columns exist
        required_columns = [
            'id', 'thread_id', 'subject', 'from_address', 'to_address',
            'cc_address', 'bcc_address', 'received_date', 'content',
            'labels', 'has_attachments', 'full_api_response'
        ]
        missing_columns = [col for col in required_columns if col not in columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in emails table: {missing_columns}")

    print("Test databases initialized")

    yield get_email_session, get_analysis_session

    # Clean up
    print("\nCleaning up test databases...")
    if os.path.exists(TEST_EMAIL_DB):
        os.remove(TEST_EMAIL_DB)
    if os.path.exists(TEST_ANALYSIS_DB):
        os.remove(TEST_ANALYSIS_DB)

@pytest.fixture
def mock_gmail_service():
    """Mock Gmail API service."""
    mock_service = MagicMock()
    
    # Mock message list response
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        'messages': [{'id': 'test1', 'threadId': 'thread1'}]
    }
    mock_service.users().messages().list.return_value = mock_list
    mock_service.users().messages().list_next.return_value = None
    
    # Mock message get response
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
                {'name': 'Date', 'value': datetime.now().isoformat()}
            ],
            'body': {'data': base64.b64encode(b'Test email content').decode('utf-8')}
        }
    }
    mock_service.users().messages().get.return_value = mock_get
    
    return mock_service

def test_email_fetching(setup_test_dbs, mock_gmail_service):
    """Test email fetching functionality."""
    get_email_session_fn, get_analysis_session_fn = setup_test_dbs
    with patch('app_get_mail.get_gmail_service', return_value=mock_gmail_service):
        init_database()
        
        # Fetch emails
        messages = fetch_emails(mock_gmail_service)
        assert len(messages) > 0
        
        # Process first message
        with get_email_session_fn() as session:
            email_data = process_email(mock_gmail_service, messages[0]['id'], session)
            assert email_data is not None
            assert email_data['id'] == 'test1'
            assert email_data['thread_id'] == 'thread1'
            assert email_data['subject'] == 'Test Email'
            assert email_data['from_address'] == 'test@example.com'
            assert email_data['to_address'] == 'me@example.com'
            
            # Check database
            email = session.query(Email).filter_by(id='test1').first()
            assert email is not None
            assert email.subject == 'Test Email'
            assert email.from_address == 'test@example.com'
            assert email.to_address == 'me@example.com'

def test_email_analysis(setup_test_dbs):
    """Test email analysis functionality."""
    get_email_session_fn, get_analysis_session_fn = setup_test_dbs
    
    # Create mock analyzer
    mock_analysis = MagicMock()
    mock_analysis.email_id = 'test1'
    mock_analysis.project = 'AI Development'
    mock_analysis.topic = 'Development'
    mock_analysis.summary = 'Test summary'
    mock_analysis.category = ['work']
    mock_analysis.priority_score = 3
    
    mock_analyzer = MagicMock()
    mock_analyzer.analyze_email.return_value = mock_analysis
    
    with patch('app_email_analyzer.EmailAnalyzer', return_value=mock_analyzer):
        analyzer = EmailAnalyzer()
        
        # Create test email
        test_email = {
            'id': 'test1',
            'subject': 'Project Update: AI Development',
            'content': 'Making good progress on the AI project.',
            'received_date': datetime.now().isoformat()
        }
        
        # Analyze email
        analysis = analyzer.analyze_email(test_email)
        assert analysis is not None
        assert analysis.email_id == 'test1'
        assert analysis.project == 'AI Development'
        assert analysis.topic == 'Development'

def test_email_reports(setup_test_dbs):
    """Test email reporting functionality."""
    get_email_session_fn, get_analysis_session_fn = setup_test_dbs
    
    # Add test email
    with get_email_session_fn() as session:
        test_email = Email(
            id='test1',
            thread_id='thread1',
            subject='Test Email',
            from_address='test@example.com',
            to_address='me@example.com',
            received_date=datetime.now(),
            content='Test content',
            labels='["INBOX"]'
        )
        session.add(test_email)
        session.commit()
    
    # Add test analysis
    with get_analysis_session_fn() as session:
        test_analysis = EmailAnalysis(
            email_id='test1',
            summary='Test summary',
            category=['work'],
            priority_score=3,
            project='Test Project',
            topic='Test Topic',
            sentiment='neutral',
            analyzed_date=datetime.now()
        )
        session.add(test_analysis)
        session.commit()
    
    # Create analytics instance and test reports
    analytics = EmailAnalytics()
    
    # Test basic reporting functions
    stats = analytics.get_analysis_stats()
    assert stats['total_emails'] >= 1
    
    project_dist = analytics.get_project_distribution()
    assert len(project_dist) >= 1
    assert 'Test Project' in [p['project'] for p in project_dist]

def test_self_email_analysis(setup_test_dbs):
    """Test self-email analysis functionality."""
    get_email_session_fn, get_analysis_session_fn = setup_test_dbs
    
    # Mock Gmail API
    mock_gmail = MagicMock()
    mock_gmail.service.users().getProfile().execute.return_value = {
        'emailAddress': 'test.user@example.com'
    }
    
    # Mock EmailAnalyzer with minimal response
    mock_analyzer = MagicMock()
    mock_analyzer.analyze_email.return_value = {
        'id': 'test1',
        'summary': 'Test summary',
        'category': ['test'],
        'priority_score': 3
    }
    
    with patch('app_email_self_log.GmailAPI', return_value=mock_gmail), \
         patch('app_email_self_log.EmailAnalyzer', return_value=mock_analyzer):
        
        analyzer = EmailSelfAnalyzer()
        
        # Add test self-email
        with get_email_session_fn() as session:
            test_email = Email(
                id='test1',
                thread_id='thread1',
                subject='Test Subject',
                from_address='test.user@example.com',
                to_address='test.user@example.com',
                received_date=datetime.now(),
                content='Test content',
                labels='["INBOX"]'
            )
            session.add(test_email)
            session.commit()
        
        # Test get_self_emails
        emails = analyzer.get_self_emails()
        assert len(emails) == 1
        assert emails[0].id == 'test1'
        
        # Test analyze_emails with minimal analysis
        analysis_results = analyzer.analyze_emails(emails[:1])  # Only analyze first email
        assert len(analysis_results) == 1
        assert analysis_results[0]['id'] == 'test1'
        assert analysis_results[0]['summary'] == 'Test summary'