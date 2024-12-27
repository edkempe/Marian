"""Test email report generation."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.email import Email
from models.email_analysis import EmailAnalysis
from models.base import Base
from app_email_reports import EmailAnalytics
from shared_lib.database_session_util import get_email_session, get_analysis_session
from shared_lib.constants import DATABASE_CONFIG

@pytest.fixture(autouse=True)
def setup_test_data():
    """Set up test data in the databases."""
    # Create test emails
    with get_email_session(testing=True) as session:
        for i in range(10):
            email = Email(
                id=f'test_{i}_{datetime.now().timestamp()}',
                thread_id=f'thread_{i}',
                subject=f'Test Email {i}',
                from_address=f'sender{i}@example.com',
                to_address='recipient@example.com',
                received_date=datetime.now() - timedelta(days=i),
                content=f'This is test email {i} content.',
                labels='["INBOX"]'
            )
            session.add(email)
        session.commit()

    # Create test analyses
    with get_analysis_session(testing=True) as session:
        for i in range(10):
            analysis = EmailAnalysis(
                email_id=f'test_{i}_{datetime.now().timestamp()}',
                thread_id=f'thread_{i}',
                analysis_date=datetime.now().isoformat(),
                analyzed_date=datetime.now().isoformat(),
                prompt_version='1.0',
                summary=f'Summary of email {i}',
                _category='["Work"]',
                priority_score=3,
                priority_reason='Medium priority',
                action_needed=True,
                action_type='["Reply"]',
                action_deadline=None,
                key_points='["Point 1", "Point 2"]',
                people_mentioned='["Person A", "Person B"]',
                links_found='[]',
                links_display='[]',
                project='Project A',
                topic='Topic A',
                sentiment='neutral',
                confidence_score=0.9,
                full_api_response='{}'
            )
            session.add(analysis)
        session.commit()

@pytest.fixture
def email_analytics():
    """Create EmailAnalytics instance."""
    return EmailAnalytics(testing=True)

def test_get_total_emails(email_analytics):
    """Test getting total email count."""
    total = email_analytics.get_total_emails()
    assert total == 10

def test_get_top_senders(email_analytics):
    """Test getting top email senders."""
    senders = email_analytics.get_top_senders()
    assert len(senders) > 0
    assert isinstance(senders[0][0], str)
    assert isinstance(senders[0][1], int)

def test_get_email_by_date(email_analytics):
    """Test getting email distribution by date."""
    distribution = email_analytics.get_email_by_date()
    assert len(distribution) > 0
    assert isinstance(distribution[0][0], str)
    assert isinstance(distribution[0][1], int)

def test_get_label_distribution(email_analytics):
    """Test getting label distribution."""
    distribution = email_analytics.get_label_distribution()
    assert len(distribution) > 0
    assert isinstance(distribution[0][0], str)
    assert isinstance(distribution[0][1], int)

def test_get_priority_distribution(email_analytics):
    """Test getting priority distribution."""
    distribution = email_analytics.get_priority_distribution()
    assert len(distribution) > 0
    assert isinstance(distribution[0][0], int)
    assert isinstance(distribution[0][1], int)

def test_get_action_needed_count(email_analytics):
    """Test getting action needed count."""
    count = email_analytics.get_action_needed_count()
    assert isinstance(count, int)
    assert count >= 0

def test_get_sentiment_distribution(email_analytics):
    """Test getting sentiment distribution."""
    distribution = email_analytics.get_sentiment_distribution()
    assert len(distribution) > 0
    assert isinstance(distribution[0][0], str)
    assert isinstance(distribution[0][1], int)

def test_get_project_distribution(email_analytics):
    """Test getting project distribution."""
    distribution = email_analytics.get_project_distribution()
    assert len(distribution) > 0
    assert isinstance(distribution[0][0], str)
    assert isinstance(distribution[0][1], int)

def test_get_topic_distribution(email_analytics):
    """Test getting topic distribution."""
    distribution = email_analytics.get_topic_distribution()
    assert len(distribution) > 0
    assert isinstance(distribution[0][0], str)
    assert isinstance(distribution[0][1], int)

def test_get_analysis_by_topic(email_analytics):
    """Test getting analyses by topic."""
    analyses = email_analytics.get_analysis_by_topic('Topic A')
    assert len(analyses) > 0
    assert all(a['topic'] == 'Topic A' for a in analyses)

def test_get_analysis_by_category(email_analytics):
    """Test getting analyses by category."""
    analyses = email_analytics.get_analysis_by_category('Work')
    assert len(analyses) > 0
    assert all('Work' in a['category'] for a in analyses)

def test_get_analysis_stats(email_analytics):
    """Test getting analysis statistics."""
    stats = email_analytics.get_analysis_stats()
    assert isinstance(stats, dict)
    assert 'total_emails' in stats
    assert 'analyzed_emails' in stats
    assert 'action_needed' in stats
    assert 'avg_priority' in stats
