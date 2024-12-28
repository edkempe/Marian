"""Tests for email fetching functionality."""
import pytest
from datetime import datetime, timedelta
from models.email import Email
from app_get_mail import (
    init_database, get_label_id, fetch_emails,
    process_email, get_oldest_email_date,
    get_newest_email_date, count_emails,
    list_labels
)
from shared_lib.gmail_lib import GmailAPI
from shared_lib.database_session_util import get_email_session
from shared_lib.constants import DATABASE_CONFIG, API_CONFIG

@pytest.fixture
def gmail_service():
    """Get real Gmail service."""
    return GmailAPI()._get_gmail_service()

@pytest.fixture
def db_session():
    """Create a test database session."""
    with get_email_session(testing=True) as session:
        init_database(session)
        
        # Clear any existing data
        session.query(Email).delete()
        session.commit()
        
        yield session

def test_init_database(db_session):
    """Test database initialization."""
    # Verify emails table exists and has correct schema
    email = Email(
        id='test1',
        threadId='thread1',
        subject='Test Subject',
        from_='from@test.com',
        to='to@test.com',
        body='Test content',
        received_date=datetime.utcnow(),
    )
    email.label_list = ['INBOX']
    db_session.add(email)
    db_session.commit()
    
    # Verify we can query the email
    result = db_session.query(Email).filter_by(id='test1').first()
    assert result is not None
    assert result.subject == 'Test Subject'
    assert result.label_list == ['INBOX']

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

def test_process_email(gmail_service, db_session):
    """Test email processing and storage."""
    # First fetch an email
    messages = fetch_emails(gmail_service, max_results=1)
    assert len(messages) > 0
    
    # Process the email
    msg_id = messages[0]['id']
    process_email(gmail_service, msg_id, db_session)
    
    # Verify email was stored
    result = db_session.query(Email).filter_by(id=msg_id).first()
    assert result is not None

def test_get_oldest_email_date(db_session):
    """Test getting oldest email date."""
    # Add test emails with different dates
    emails = [
        Email(
            id=f'test{i}',
            threadId=f'thread{i}',
            received_date=datetime.utcnow() + timedelta(days=i)
        ) for i in range(3)
    ]
    db_session.add_all(emails)
    db_session.commit()
    
    oldest_date = get_oldest_email_date(db_session)
    assert oldest_date is not None
    assert oldest_date == emails[0].received_date

def test_get_newest_email_date(db_session):
    """Test getting newest email date."""
    # Add test emails with different dates
    emails = [
        Email(
            id=f'test{i}',
            threadId=f'thread{i}',
            received_date=datetime.utcnow() + timedelta(days=i)
        ) for i in range(3)
    ]
    db_session.add_all(emails)
    db_session.commit()
    
    newest_date = get_newest_email_date(db_session)
    assert newest_date is not None
    assert newest_date == emails[-1].received_date

def test_count_emails(db_session):
    """Test email counting."""
    # Add test emails
    emails = [
        Email(
            id=f'test{i}',
            threadId=f'thread{i}',
            received_date=datetime.utcnow()
        ) for i in range(3)
    ]
    db_session.add_all(emails)
    db_session.commit()
    
    count = count_emails(db_session)
    assert count == 3

def test_list_labels(gmail_service):
    """Test listing Gmail labels."""
    labels = list_labels(gmail_service)
    assert len(labels) > 0
    assert all('id' in label and 'name' in label for label in labels)
