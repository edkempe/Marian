"""Minimal test suite using real implementations."""

import pytest
from datetime import datetime
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app_email_analyzer import EmailAnalyzer
from app_email_self_log import EmailSelfAnalyzer
from app_email_reports import EmailAnalytics
from models.email import Email, Base as EmailBase
from models.email_analysis import EmailAnalysis, Base as AnalysisBase
from .test_config import setup_test_env, cleanup_test_env, TEST_EMAIL_DB, TEST_ANALYSIS_DB

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Set up test environment and databases."""
    # Set up test environment
    setup_test_env()
    
    # Create test databases
    email_engine = create_engine(f'sqlite:///{TEST_EMAIL_DB}')
    analysis_engine = create_engine(f'sqlite:///{TEST_ANALYSIS_DB}')
    
    # Create tables
    EmailBase.metadata.create_all(email_engine)
    AnalysisBase.metadata.create_all(analysis_engine)
    
    yield
    
    # Clean up after all tests
    cleanup_test_env()

def test_email_analysis():
    """Test email analysis with real API calls."""
    analyzer = EmailAnalyzer(metrics_port=0)
    
    test_email = {
        'id': 'test1',
        'subject': 'Test Email',
        'content': 'This is an important work email that requires review by tomorrow.',
        'received_date': datetime.now().isoformat(),
        'thread_id': 'thread1',
        'labels': '["INBOX"]'
    }
    
    analysis = analyzer.analyze_email(test_email)
    assert analysis is not None
    assert analysis.email_id == test_email['id']
    assert analysis.summary is not None
    assert analysis.priority_score > 0
    assert analysis.priority_reason is not None

def test_email_fetching():
    """Test email fetching with real database."""
    analyzer = EmailSelfAnalyzer()
    
    # Add test email to database
    engine = create_engine(f'sqlite:///{TEST_EMAIL_DB}')
    Session = sessionmaker(bind=engine)
    with Session() as session:
        email = Email(
            id='test1',
            thread_id='thread1',
            subject='Test Email',
            content='Test content',
            received_date=datetime.now(),
            labels='["INBOX"]',
            from_address='test@example.com'
        )
        session.add(email)
        session.commit()
    
    # Test fetching
    emails = analyzer.get_self_emails()
    assert len(emails) > 0

def test_email_analytics():
    """Test email analytics with real database."""
    analytics = EmailAnalytics()
    
    # Add test analysis to database
    engine = create_engine(f'sqlite:///{TEST_ANALYSIS_DB}')
    Session = sessionmaker(bind=engine)
    with Session() as session:
        analysis = EmailAnalysis(
            email_id='test1',
            summary='Test summary',
            category=['work'],
            priority_score=3,
            priority_reason='Important work email',
            action_needed=True,
            action_type=['review'],
            action_deadline='2024-12-31',
            project='Test Project',
            topic='Test Topic',
            sentiment='neutral',
            confidence_score=0.9
        )
        session.add(analysis)
        session.commit()
    
    # Test analytics
    stats = analytics.get_analysis_stats()
    assert stats is not None
    assert len(stats) > 0
