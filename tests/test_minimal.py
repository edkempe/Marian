"""Minimal test suite using real implementations."""

import pytest
from datetime import datetime
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src import EmailAnalyzer, EmailSelfAnalyzer, EmailAnalytics
from models.email import Email, Base as EmailBase
from models.email_analysis import EmailAnalysis, Base as AnalysisBase
from models.database_init import init_db, get_test_engines
from .test_config import setup_test_env, cleanup_test_env, TEST_EMAIL_DB, TEST_ANALYSIS_DB
from shared_lib.anthropic_client_lib import test_anthropic_connection
from shared_lib.constants import API_CONFIG

def setup_module():
    """Set up test databases."""
    init_db(testing=True)

@pytest.fixture(scope="function")
def test_db():
    """Create test databases for each test."""
    email_engine, analysis_engine, catalog_engine = get_test_engines()
    yield email_engine, analysis_engine, catalog_engine

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

@pytest.fixture(scope="session", autouse=True)
def verify_api_connection():
    """Verify API connection before running tests."""
    if not test_anthropic_connection():
        pytest.exit("API connection test failed. Please check your API key and connection.")

def test_email_analysis(verify_api_connection):
    """Test email analysis with real API calls."""
    analyzer = EmailAnalyzer(metrics_port=0, test_mode=True)
    
    test_email = {
        'id': f'test_{datetime.now().timestamp()}',
        'threadId': 'thread1',
        'subject': 'Test Email',
        'body': 'This is an important work email that requires review by tomorrow.',
        'date': datetime.now().isoformat(),
        'labelIds': '["INBOX"]',
        'from_': 'test@example.com',
        'to': 'recipient@example.com'
    }
    
    try:
        analysis = analyzer.analyze_email(test_email)
        assert analysis is not None
        assert analysis.email_id == test_email['id']
        assert analysis.summary is not None
        assert analysis.priority_score > 0
        assert analysis.priority_reason is not None
    except Exception as e:
        pytest.fail(f"Email analysis failed: {str(e)}")

def test_email_fetching():
    """Test email fetching with real database."""
    analyzer = EmailSelfAnalyzer()
    
    # Add test email to database
    engine = create_engine(f'sqlite:///{TEST_EMAIL_DB}')
    Session = sessionmaker(bind=engine)
    with Session() as session:
        email = Email(
            id=f'test_{datetime.now().timestamp()}',
            threadId='thread1',
            subject='Test Email',
            body='Test content',
            date=datetime.now(),
            labelIds=json.dumps(["INBOX"]),
            from_='test@example.com',
            to='recipient@example.com'
        )
        session.add(email)
        session.commit()
    
    # Verify email was added
    with Session() as session:
        email = session.query(Email).first()
        assert email is not None
        assert email.subject == 'Test Email'
        assert email.body == 'Test content'

def test_email_analytics():
    """Test email analytics with real database."""
    analytics = EmailAnalytics()
    
    # Add test analysis to database
    engine = create_engine(f'sqlite:///{TEST_ANALYSIS_DB}')
    Session = sessionmaker(bind=engine)
    with Session() as session:
        analysis = EmailAnalysis(
            email_id=f'test_{datetime.now().timestamp()}',
            threadId='thread1',
            analyzed_date=datetime.now(),
            prompt_version='1.0',
            summary='Test summary',
            category=json.dumps(['work']),
            priority_score=3,
            priority_reason='Important work email',
            action_needed=True,
            action_type=json.dumps(['review']),
            key_points=json.dumps(['Test point 1', 'Test point 2']),
            people_mentioned=json.dumps([]),
            links_found=json.dumps([]),
            links_display=json.dumps([]),
            sentiment='neutral',
            confidence_score=0.8,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(analysis)
        session.commit()
    
    # Verify analysis was added
    with Session() as session:
        analysis = session.query(EmailAnalysis).first()
        assert analysis is not None
        assert analysis.summary == 'Test summary'
        assert json.loads(analysis.category) == ['work']
        assert analysis.priority_score == 3
        assert analysis.sentiment == 'neutral'
