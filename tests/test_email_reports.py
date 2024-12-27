"""Tests for email reporting functionality."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.email import Email
from models.email_analysis import EmailAnalysis
from app_email_reports import EmailAnalytics
from shared_lib.database_session_util import get_email_session, get_analysis_session

@pytest.fixture(scope="session")
def email_analytics():
    """Create EmailAnalytics instance for testing."""
    return EmailAnalytics()

def setup_test_data():
    """Set up test data in real databases."""
    with get_email_session() as session:
        # Add test emails
        for i in range(10):
            email = Email(
                id=f'test_{i}_{datetime.now().timestamp()}',
                thread_id=f'thread_{i}',
                subject=f'Test Email {i}',
                content=f'This is test email {i} content.',
                received_date=datetime.now() - timedelta(days=i),
                labels='["INBOX"]',
                from_address=f'sender{i}@example.com',
                to_address='recipient@example.com'
            )
            session.add(email)
        session.commit()

    with get_analysis_session() as session:
        # Add test analysis results
        for i in range(10):
            analysis = EmailAnalysis(
                email_id=f'test_{i}_{datetime.now().timestamp()}',
                summary=f'Summary of email {i}',
                category=['work', 'important'] if i % 2 == 0 else ['personal'],
                priority_score=i % 5 + 1,
                priority_reason=f'Priority reason {i}',
                action_needed=i % 2 == 0,
                action_type=['review'] if i % 2 == 0 else [],
                sentiment='positive' if i % 3 == 0 else 'neutral',
                confidence_score=0.8 + (i / 100),
                project=f'Project {i}' if i % 2 == 0 else '',
                topic=f'Topic {i}'
            )
            session.add(analysis)
        session.commit()

def test_get_total_emails(email_analytics):
    """Test getting total email count."""
    setup_test_data()
    total = email_analytics.get_total_emails()
    assert total > 0
    assert isinstance(total, int)

def test_get_top_senders(email_analytics):
    """Test getting top email senders."""
    senders = email_analytics.get_top_senders()
    assert len(senders) > 0
    for sender in senders:
        assert 'sender' in sender
        assert 'count' in sender
        assert isinstance(sender['count'], int)
        assert sender['count'] > 0

def test_get_email_by_date(email_analytics):
    """Test getting email distribution by date."""
    distribution = email_analytics.get_email_by_date()
    assert len(distribution) > 0
    for entry in distribution:
        assert 'date' in entry
        assert 'count' in entry
        assert isinstance(entry['count'], int)

def test_get_label_distribution(email_analytics):
    """Test getting label distribution."""
    labels = email_analytics.get_label_distribution()
    assert len(labels) > 0
    for label in labels:
        assert 'label' in label
        assert 'count' in label
        assert isinstance(label['count'], int)
        assert label['count'] > 0

def test_get_anthropic_analysis(email_analytics):
    """Test getting AI analysis results."""
    analysis = email_analytics.get_anthropic_analysis()
    assert len(analysis) > 0
    for entry in analysis:
        assert 'email_id' in entry
        assert 'summary' in entry
        assert 'priority_score' in entry
        assert isinstance(entry['priority_score'], int)
        assert 1 <= entry['priority_score'] <= 5

def test_get_confidence_distribution(email_analytics):
    """Test getting confidence score distribution."""
    distribution = email_analytics.get_confidence_distribution()
    assert len(distribution) > 0
    for entry in distribution:
        assert 'range' in entry
        assert 'count' in entry
        assert isinstance(entry['count'], int)

def test_get_priority_distribution(email_analytics):
    """Test getting priority score distribution."""
    distribution = email_analytics.get_priority_distribution()
    assert len(distribution) > 0
    for score in distribution:
        assert 'score' in score
        assert 'count' in score
        assert isinstance(score['count'], int)

def test_get_sentiment_distribution(email_analytics):
    """Test getting sentiment distribution."""
    distribution = email_analytics.get_sentiment_distribution()
    assert len(distribution) > 0
    for sentiment in distribution:
        assert 'sentiment' in sentiment
        assert 'count' in sentiment
        assert isinstance(sentiment['count'], int)

def test_get_action_needed_distribution(email_analytics):
    """Test getting action needed distribution."""
    distribution = email_analytics.get_action_needed_distribution()
    assert len(distribution) > 0
    for entry in distribution:
        assert 'needs_action' in entry
        assert 'count' in entry
        assert isinstance(entry['count'], int)

def test_get_project_distribution(email_analytics):
    """Test getting project distribution."""
    distribution = email_analytics.get_project_distribution()
    assert len(distribution) > 0
    for project in distribution:
        assert 'project' in project
        assert 'count' in project
        assert isinstance(project['count'], int)

def test_get_topic_distribution(email_analytics):
    """Test getting topic distribution."""
    distribution = email_analytics.get_topic_distribution()
    assert len(distribution) > 0
    for topic in distribution:
        assert 'topic' in topic
        assert 'count' in topic
        assert isinstance(topic['count'], int)

def test_get_category_distribution(email_analytics):
    """Test getting category distribution."""
    distribution = email_analytics.get_category_distribution()
    assert len(distribution) > 0
    for category in distribution:
        assert 'category' in category
        assert 'count' in category
        assert isinstance(category['count'], int)

def test_get_analysis_by_date(email_analytics):
    """Test getting analysis distribution by date."""
    distribution = email_analytics.get_analysis_by_date()
    assert len(distribution) > 0
    for entry in distribution:
        assert 'date' in entry
        assert 'count' in entry
        assert isinstance(entry['count'], int)

def test_get_detailed_analysis(email_analytics):
    """Test getting detailed analysis for a specific email."""
    # Get a test email ID
    with get_email_session() as session:
        email = session.query(Email).first()
        email_id = email.id

    analysis = email_analytics.get_detailed_analysis(email_id)
    assert analysis is not None
    assert 'summary' in analysis
    assert 'priority_score' in analysis
    assert 'sentiment' in analysis

def test_get_detailed_analysis_not_found(email_analytics):
    """Test getting detailed analysis for a non-existent email."""
    analysis = email_analytics.get_detailed_analysis('nonexistent_id')
    assert analysis is None

def test_get_analysis_with_action_needed(email_analytics):
    """Test getting analyses that require action."""
    analyses = email_analytics.get_analysis_with_action_needed()
    assert isinstance(analyses, list)
    for analysis in analyses:
        assert analysis['action_needed'] is True
        assert len(analysis['action_type']) > 0

def test_get_high_priority_analysis(email_analytics):
    """Test getting high priority analyses."""
    analyses = email_analytics.get_high_priority_analysis()
    assert isinstance(analyses, list)
    for analysis in analyses:
        assert analysis['priority_score'] >= 4

def test_get_analysis_by_sentiment(email_analytics):
    """Test getting analyses by sentiment."""
    sentiments = ['positive', 'negative', 'neutral']
    for sentiment in sentiments:
        analyses = email_analytics.get_analysis_by_sentiment(sentiment)
        assert isinstance(analyses, list)
        for analysis in analyses:
            assert analysis['sentiment'] == sentiment

def test_get_analysis_by_project(email_analytics):
    """Test getting analyses by project."""
    with get_analysis_session() as session:
        project = session.query(EmailAnalysis.project).filter(
            EmailAnalysis.project != ''
        ).first()[0]
    
    analyses = email_analytics.get_analysis_by_project(project)
    assert isinstance(analyses, list)
    for analysis in analyses:
        assert analysis['project'] == project

def test_get_analysis_by_topic(email_analytics):
    """Test getting analyses by topic."""
    with get_analysis_session() as session:
        topic = session.query(EmailAnalysis.topic).filter(
            EmailAnalysis.topic != ''
        ).first()[0]
    
    analyses = email_analytics.get_analysis_by_topic(topic)
    assert isinstance(analyses, list)
    for analysis in analyses:
        assert analysis['topic'] == topic

def test_get_analysis_by_category(email_analytics):
    """Test getting analyses by category."""
    with get_analysis_session() as session:
        category = session.query(EmailAnalysis.category).first()[0][0]
    
    analyses = email_analytics.get_analysis_by_category(category)
    assert isinstance(analyses, list)
    for analysis in analyses:
        assert category in analysis['category']

def test_get_analysis_stats(email_analytics):
    """Test getting overall analysis statistics."""
    stats = email_analytics.get_analysis_stats()
    assert isinstance(stats, dict)
    assert 'total_emails' in stats
    assert 'analyzed_emails' in stats
    assert 'average_priority' in stats
    assert 'action_needed_count' in stats
