"""Tests for email reporting functionality."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from ..app_email_reports import EmailAnalytics
from ..models.email_analysis import EmailAnalysis
from ..models.email import Email

@pytest.fixture
def mock_email_db():
    """Create an in-memory SQLite database for email testing."""
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id TEXT PRIMARY KEY,
                  subject TEXT,
                  sender TEXT,
                  date TEXT,
                  body TEXT,
                  labels TEXT,
                  raw_data TEXT)''')
    
    # Insert test data
    test_data = [
        ('1', 'Test Subject 1', 'sender1@test.com', '2024-12-19 10:00:00', 'Test body 1', 'INBOX,IMPORTANT', 'raw1'),
        ('2', 'Test Subject 2', 'sender2@test.com', '2024-12-19 11:00:00', 'Test body 2', 'INBOX,UNREAD', 'raw2'),
        ('3', 'Test Subject 3', 'sender1@test.com', '2024-12-19 12:00:00', 'Test body 3', 'INBOX,SENT', 'raw3')
    ]
    c.executemany('INSERT INTO emails VALUES (?, ?, ?, ?, ?, ?, ?)', test_data)
    conn.commit()
    return conn

@pytest.fixture
def mock_label_db():
    """Create an in-memory SQLite database for label testing."""
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS gmail_labels
                 (label_id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  type TEXT,
                  message_list_visibility TEXT,
                  label_list_visibility TEXT,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Insert test data
    test_data = [
        ('INBOX', 'Inbox', 'system', 'show', 'show', '2024-12-19'),
        ('IMPORTANT', 'Important', 'system', 'show', 'show', '2024-12-19'),
        ('UNREAD', 'Unread', 'system', 'show', 'show', '2024-12-19'),
        ('SENT', 'Sent', 'system', 'show', 'show', '2024-12-19')
    ]
    c.executemany('INSERT INTO gmail_labels VALUES (?, ?, ?, ?, ?, ?)', test_data)
    conn.commit()
    return conn

@pytest.fixture
def mock_analysis_db():
    """Create an in-memory SQLite database for analysis testing."""
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS email_analysis
                 (email_id TEXT PRIMARY KEY,
                  analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  summary TEXT,
                  category TEXT,
                  priority_score INTEGER,
                  priority_reason TEXT,
                  action_needed BOOLEAN,
                  action_type TEXT,
                  action_deadline TEXT,
                  key_points TEXT,
                  people_mentioned TEXT,
                  links_found TEXT,
                  project TEXT,
                  topic TEXT,
                  ref_docs TEXT,
                  sentiment TEXT,
                  confidence_score REAL,
                  raw_analysis TEXT)''')
    
    # Insert test data
    test_data = [
        ('1', '2024-12-19', 'Summary 1', '["work"]', 3, 'reason1', 1, '["review"]', '2024-12-20',
         '["point1"]', '["person1"]', '[]', 'project1', 'topic1', 'ref1', 'positive', 0.9, 'raw1'),
        ('2', '2024-12-19', 'Summary 2', '["personal"]', 2, 'reason2', 0, '[]', '',
         '["point2"]', '[]', '[]', 'project2', 'topic2', 'ref2', 'neutral', 0.8, 'raw2')
    ]
    c.executemany('''INSERT INTO email_analysis VALUES
                     (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', test_data)
    conn.commit()
    return conn

@pytest.fixture
def analytics(mock_email_db, mock_label_db, mock_analysis_db):
    """Create EmailAnalytics instance with test databases."""
    with patch('sqlite3.connect') as mock_connect:
        def side_effect(path):
            if 'db_email_store.db' in str(path) or 'db_email_store.db' in str(path).split('/')[-1]:
                return mock_email_db
            elif 'email_labels.db' in str(path) or 'email_labels.db' in str(path).split('/')[-1]:
                return mock_label_db
            elif 'email_analysis.db' in str(path) or 'email_analysis.db' in str(path).split('/')[-1]:
                return mock_analysis_db
            return sqlite3.connect(':memory:')
        
        mock_connect.side_effect = side_effect
        return EmailAnalytics()

def test_get_total_emails(analytics):
    """Test getting total email count."""
    assert analytics.get_total_emails() == 3

def test_get_top_senders(analytics):
    """Test getting top email senders."""
    top_senders = analytics.get_top_senders()
    assert len(top_senders) == 2
    assert ('sender1@test.com', 2) in top_senders
    assert ('sender2@test.com', 1) in top_senders

def test_get_email_by_date(analytics):
    """Test getting email distribution by date."""
    date_dist = analytics.get_email_by_date()
    assert len(date_dist) == 1  # All emails are from the same date
    assert date_dist[0][1] == 3  # Total emails for that date

def test_get_label_distribution(analytics):
    """Test getting label distribution."""
    label_dist = analytics.get_label_distribution()
    assert len(label_dist) >= 4  # We have at least 4 different labels
    assert label_dist['INBOX'] == 3  # All emails have INBOX label
    assert label_dist['IMPORTANT'] == 1
    assert label_dist['UNREAD'] == 1
    assert label_dist['SENT'] == 1

def test_get_anthropic_analysis(analytics):
    """Test getting AI analysis results."""
    analysis = analytics.get_anthropic_analysis()
    assert len(analysis) == 2
    
    # Check first analysis
    assert analysis[0]['email_id'] == '1'
    assert analysis[0]['summary'] == 'Summary 1'
    assert analysis[0]['sentiment'] == 'positive'
    assert analysis[0]['confidence_score'] == 0.9
    
    # Check second analysis
    assert analysis[1]['email_id'] == '2'
    assert analysis[1]['summary'] == 'Summary 2'
    assert analysis[1]['sentiment'] == 'neutral'
    assert analysis[1]['confidence_score'] == 0.8

def test_get_confidence_distribution(analytics):
    """Test getting confidence score distribution."""
    conf_dist = analytics.get_confidence_distribution()
    assert len(conf_dist) > 0
    # Should have entries for confidence ranges 0.8-0.89 and 0.9-1.0
    ranges = [row[0] for row in conf_dist]
    assert '0.8-0.89' in ranges
    assert '0.9-1.0' in ranges

def test_get_priority_distribution(analytics):
    """Test getting priority score distribution."""
    priority_dist = analytics.get_priority_distribution()
    assert len(priority_dist) > 0
    assert priority_dist['High (3)'] == 1  # One high priority email
    assert priority_dist['Medium (2)'] == 1  # One medium priority email

def test_get_sentiment_distribution(analytics):
    """Test getting sentiment distribution."""
    sentiment_dist = analytics.get_sentiment_distribution()
    assert len(sentiment_dist) > 0
    assert sentiment_dist['positive'] == 1  # One positive sentiment
    assert sentiment_dist['neutral'] == 1  # One neutral sentiment

def test_get_action_needed_distribution(analytics):
    """Test getting action needed distribution."""
    action_dist = analytics.get_action_needed_distribution()
    assert len(action_dist) == 2  # Should have both True and False
    assert action_dist[True] == 1  # One email needs action
    assert action_dist[False] == 1  # One email doesn't need action

def test_get_project_distribution(analytics):
    """Test getting project distribution."""
    project_dist = analytics.get_project_distribution()
    assert len(project_dist) == 2
    assert 'project1' in project_dist
    assert 'project2' in project_dist
    assert project_dist['project1'] == 1
    assert project_dist['project2'] == 1

def test_get_topic_distribution(analytics):
    """Test getting topic distribution."""
    topic_dist = analytics.get_topic_distribution()
    assert len(topic_dist) == 2
    assert 'topic1' in topic_dist
    assert 'topic2' in topic_dist
    assert topic_dist['topic1'] == 1
    assert topic_dist['topic2'] == 1

def test_get_category_distribution(analytics):
    """Test getting category distribution."""
    category_dist = analytics.get_category_distribution()
    assert len(category_dist) == 2
    assert 'work' in category_dist
    assert 'personal' in category_dist
    assert category_dist['work'] == 1
    assert category_dist['personal'] == 1

def test_get_analysis_by_date(analytics):
    """Test getting analysis distribution by date."""
    date_dist = analytics.get_analysis_by_date()
    assert len(date_dist) == 1  # All analyses are from the same date
    assert date_dist[0][1] == 2  # Total analyses for that date

def test_get_detailed_analysis(analytics):
    """Test getting detailed analysis for a specific email."""
    analysis = analytics.get_detailed_analysis('1')
    assert analysis is not None
    assert analysis['email_id'] == '1'
    assert analysis['summary'] == 'Summary 1'
    assert analysis['category'] == ['work']
    assert analysis['priority']['score'] == 3
    assert analysis['priority']['reason'] == 'reason1'
    assert analysis['action']['needed'] is True
    assert analysis['action']['type'] == ['review']
    assert analysis['action']['deadline'] == '2024-12-20'
    assert analysis['key_points'] == ['point1']
    assert analysis['people_mentioned'] == ['person1']
    assert analysis['sentiment'] == 'positive'
    assert analysis['confidence_score'] == 0.9

def test_get_detailed_analysis_not_found(analytics):
    """Test getting detailed analysis for a non-existent email."""
    analysis = analytics.get_detailed_analysis('999')
    assert analysis is None

def test_get_analysis_with_action_needed(analytics):
    """Test getting analyses that require action."""
    analyses = analytics.get_analysis_with_action_needed()
    assert len(analyses) == 1
    assert analyses[0]['email_id'] == '1'
    assert analyses[0]['action']['needed'] is True
    assert analyses[0]['action']['type'] == ['review']

def test_get_high_priority_analysis(analytics):
    """Test getting high priority analyses."""
    analyses = analytics.get_high_priority_analysis()
    assert len(analyses) == 1
    assert analyses[0]['email_id'] == '1'
    assert analyses[0]['priority']['score'] == 3

def test_get_analysis_by_sentiment(analytics):
    """Test getting analyses by sentiment."""
    positive = analytics.get_analysis_by_sentiment('positive')
    neutral = analytics.get_analysis_by_sentiment('neutral')
    
    assert len(positive) == 1
    assert len(neutral) == 1
    assert positive[0]['email_id'] == '1'
    assert neutral[0]['email_id'] == '2'

def test_get_analysis_by_project(analytics):
    """Test getting analyses by project."""
    project1 = analytics.get_analysis_by_project('project1')
    project2 = analytics.get_analysis_by_project('project2')
    
    assert len(project1) == 1
    assert len(project2) == 1
    assert project1[0]['email_id'] == '1'
    assert project2[0]['email_id'] == '2'

def test_get_analysis_by_topic(analytics):
    """Test getting analyses by topic."""
    topic1 = analytics.get_analysis_by_topic('topic1')
    topic2 = analytics.get_analysis_by_topic('topic2')
    
    assert len(topic1) == 1
    assert len(topic2) == 1
    assert topic1[0]['email_id'] == '1'
    assert topic2[0]['email_id'] == '2'

def test_get_analysis_by_category(analytics):
    """Test getting analyses by category."""
    work = analytics.get_analysis_by_category('work')
    personal = analytics.get_analysis_by_category('personal')
    
    assert len(work) == 1
    assert len(personal) == 1
    assert work[0]['email_id'] == '1'
    assert personal[0]['email_id'] == '2'

def test_get_analysis_stats(analytics):
    """Test getting overall analysis statistics."""
    stats = analytics.get_analysis_stats()
    assert stats['total_analyzed'] == 2
    assert stats['avg_confidence'] == 0.85  # (0.9 + 0.8) / 2
    assert stats['action_needed_count'] == 1
    assert stats['high_priority_count'] == 1
    assert stats['sentiment_counts']['positive'] == 1
    assert stats['sentiment_counts']['neutral'] == 1
