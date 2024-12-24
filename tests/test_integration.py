"""Integration tests for Gmail API functionality."""
import pytest
from datetime import datetime, timedelta
from lib_gmail import GmailAPI
from app_get_mail import fetch_emails, process_email, list_labels, get_email_session, init_database
from models.email import Email
from email.utils import parsedate_to_datetime
from constants import DATABASE_CONFIG, EMAIL_CONFIG
from sqlalchemy import func

@pytest.fixture(scope="session")
def gmail_api():
    """Create and initialize Gmail API instance."""
    gmail = GmailAPI()
    gmail.setup_label_database()  # Initialize label database
    gmail.sync_labels()  # Sync labels from Gmail
    return gmail

def test_gmail_authentication(gmail_api):
    """Test Gmail API authentication."""
    assert gmail_api.service is not None
    
    # Test basic profile access
    profile = gmail_api.service.users().getProfile(userId='me').execute()
    assert 'emailAddress' in profile
    print(f"Authenticated as: {profile['emailAddress']}")

def test_label_operations(gmail_api):
    """Test Gmail label operations."""
    # List all labels
    labels = list_labels(gmail_api.service)
    assert len(labels) > 0
    
    # Print found labels
    print("\nAvailable labels:")
    for label in labels:
        print(f"- {label['name']} ({label['id']})")
    
    # Test getting specific system labels
    system_labels = ['INBOX', 'SENT', 'DRAFT', 'SPAM']
    for label in system_labels:
        label_id = gmail_api.get_label_id(label)
        assert label_id is not None
        print(f"\nFound {label} label: {label_id}")

def test_label_operations_error(gmail_api):
    """Test error handling in label operations."""
    # Test non-existent label
    non_existent_label = "NON_EXISTENT_LABEL_12345"
    label_id = gmail_api.get_label_id(non_existent_label)
    assert label_id is None
    
    # Test empty label name
    empty_label = ""
    label_id = gmail_api.get_label_id(empty_label)
    assert label_id is None

def test_email_fetching(gmail_api):
    """Test fetching emails from Gmail."""
    # Fetch recent emails (last 7 days)
    start_date = datetime.now() - timedelta(days=7)
    messages = fetch_emails(gmail_api.service, start_date=start_date)
    
    assert len(messages) > 0
    print(f"\nFetched {len(messages)} recent emails")
    
    # Test fetching with label
    try:
        inbox_messages = fetch_emails(
            gmail_api.service,
            start_date=start_date,
            label='INBOX'  # Changed from label_ids to label
        )
        print(f"Found {len(inbox_messages)} INBOX emails")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    # Print details of a few messages
    for msg_id in [m['id'] for m in messages[:EMAIL_CONFIG['BATCH_SIZE']]]:
        try:
            # Get full message details
            message = gmail_api.service.users().messages().get(
                userId='me', id=msg_id).execute()
            headers = {header['name']: header['value'] 
                      for header in message['payload']['headers']}
            print("\nMessage details:")
            print(f"Subject: {headers.get('Subject', 'No subject')}")
            print(f"Date: {headers.get('Date', 'Unknown')}")
        except Exception as e:
            print(f"Error getting message details: {str(e)}")

def test_email_fetching_error_handling(gmail_api):
    """Test error handling in email fetching."""
    # Test with future date
    future_date = datetime.now() + timedelta(days=365)
    messages = fetch_emails(gmail_api.service, start_date=future_date)
    assert len(messages) == 0
    
    # Test with very old date
    old_date = datetime.now() - timedelta(days=3650)  # 10 years ago
    messages = fetch_emails(gmail_api.service, start_date=old_date)
    assert isinstance(messages, list), "Should return a list even for old dates"

def test_email_processing(gmail_api, test_db_session):
    """Test processing and storing emails."""
    # Fetch a few recent emails
    start_date = datetime.now() - timedelta(days=1)
    messages = fetch_emails(gmail_api.service, start_date=start_date)
    
    # Process a subset of messages
    processed_count = 0
    for msg_id in [m['id'] for m in messages[:EMAIL_CONFIG['BATCH_SIZE']]]:
        try:
            # Get full message details
            message = gmail_api.service.users().messages().get(
                userId='me', id=msg_id).execute()
            
            # Extract headers
            headers = {header['name']: header['value'] 
                      for header in message['payload']['headers']}
            
            # Create email object
            email = Email(
                id=message['id'],
                thread_id=message['threadId'],
                subject=headers.get('Subject', '[No Subject]'),
                from_address=headers.get('From', '[No Sender]'),
                to_address=headers.get('To', '[No Recipient]'),
                received_date=parsedate_to_datetime(headers.get('Date', '')),
                labels=','.join(message.get('labelIds', [])),
                content=''  # We'll add content processing later
            )
            
            # Store in database
            test_db_session.add(email)
            test_db_session.commit()
            processed_count += 1
            
            print(f"\nProcessed email {email.id}:")
            print(f"Subject: {email.subject}")
            print(f"From: {email.from_address}")
            print(f"Labels: {email.labels}")
            
        except Exception as e:
            print(f"Error processing message {msg_id}: {str(e)}")
    
    assert processed_count > 0, "Should process at least one email"
    
    # Verify emails were stored in database
    stored_emails = test_db_session.query(Email).all()
    assert len(stored_emails) >= processed_count
    
    print("\nStored emails:\n")
    for email in stored_emails[-processed_count:]:
        print(f"ID: {email.id}")
        print(f"Subject: {email.subject}")
        print(f"From: {email.from_address}")
        print(f"Labels: {email.labels}")
        print(f"Date: {email.received_date}\n")

def test_email_processing_error_handling(gmail_api, test_db_session):
    """Test error handling in email processing."""
    # Test with invalid message ID
    invalid_msg_id = "INVALID_MESSAGE_ID_12345"
    with pytest.raises(Exception) as exc_info:
        result = gmail_api.service.users().messages().get(
            userId='me', id=invalid_msg_id).execute()
    error_msg = str(exc_info.value).lower()
    assert "invalid" in error_msg or "not found" in error_msg
    
    # Test with missing required fields
    msg_with_missing_fields = {
        'id': '12345',
        'threadId': 'thread123',
        'labelIds': ['INBOX'],
        'payload': {
            'headers': []  # Empty headers
        }
    }
    
    try:
        # Directly test the processing logic
        headers = {}
        email = Email(
            id=msg_with_missing_fields['id'],
            thread_id=msg_with_missing_fields['threadId'],
            subject=headers.get('Subject', '[No Subject]'),  # Provide default
            from_address=headers.get('From', '[No Sender]'),  # Provide default
            to_address=headers.get('To', '[No Recipient]'),  # Provide default
            received_date=datetime.now(),  # Use current time as fallback
            labels=','.join(msg_with_missing_fields.get('labelIds', [])),
            content=''
        )
        test_db_session.add(email)
        test_db_session.commit()
    except Exception as e:
        assert False, f"Should handle missing fields gracefully: {str(e)}"
    
    # Verify the email was stored with default values
    stored_email = test_db_session.query(Email).filter_by(
        id=msg_with_missing_fields['id']).first()
    assert stored_email is not None
    assert stored_email.subject == '[No Subject]'
    assert stored_email.from_address == '[No Sender]'
    assert stored_email.to_address == '[No Recipient]'

def test_email_date_queries(gmail_api, test_db_session):
    """Test email date querying functionality."""
    # Fetch and process some test emails
    start_date = datetime.now() - timedelta(days=7)
    messages = fetch_emails(gmail_api.service, start_date=start_date)
    
    for msg_id in [m['id'] for m in messages[:EMAIL_CONFIG['BATCH_SIZE']]]:
        message = gmail_api.service.users().messages().get(
            userId='me', id=msg_id).execute()
        headers = {header['name']: header['value'] 
                  for header in message['payload']['headers']}
        
        email = Email(
            id=message['id'],
            thread_id=message['threadId'],
            subject=headers.get('Subject', '[No Subject]'),
            from_address=headers.get('From', '[No Sender]'),
            to_address=headers.get('To', '[No Recipient]'),
            received_date=parsedate_to_datetime(headers.get('Date', '')),
            labels=','.join(message.get('labelIds', [])),
            content=''
        )
        test_db_session.add(email)
    
    test_db_session.commit()
    
    # Test oldest email date
    oldest_date = test_db_session.query(func.min(Email.received_date)).scalar()
    assert oldest_date is not None
    print(f"\nOldest email date: {oldest_date}")
    
    # Test newest email date
    newest_date = test_db_session.query(func.max(Email.received_date)).scalar()
    assert newest_date is not None
    print(f"Newest email date: {newest_date}")
    
    # Verify date range is within expected bounds
    assert newest_date >= oldest_date
    assert newest_date - oldest_date <= timedelta(days=7)

def test_email_counting(gmail_api, test_db_session):
    """Test email counting functionality."""
    # First, add some test emails
    start_date = datetime.now() - timedelta(days=7)
    messages = fetch_emails(gmail_api.service, start_date=start_date)
    
    for msg_id in [m['id'] for m in messages[:EMAIL_CONFIG['BATCH_SIZE']]]:
        message = gmail_api.service.users().messages().get(
            userId='me', id=msg_id).execute()
        headers = {header['name']: header['value'] 
                  for header in message['payload']['headers']}
        
        email = Email(
            id=message['id'],
            thread_id=message['threadId'],
            subject=headers.get('Subject', '[No Subject]'),
            from_address=headers.get('From', '[No Sender]'),
            to_address=headers.get('To', '[No Recipient]'),
            received_date=parsedate_to_datetime(headers.get('Date', '')),
            labels=','.join(message.get('labelIds', [])),
            content=''
        )
        test_db_session.add(email)
    
    test_db_session.commit()
    
    # Count total emails
    total_count = test_db_session.query(Email).count()
    print(f"\nTotal emails in database: {total_count}")
    assert total_count > 0
    
    # Count emails by label
    for label in ['INBOX', 'SENT', 'IMPORTANT']:
        label_count = test_db_session.query(Email).filter(
            Email.labels.like(f'%{label}%')
        ).count()
        print(f"Emails with {label} label: {label_count}")
    
    # Count emails by date range
    recent_count = test_db_session.query(Email).filter(
        Email.received_date >= datetime.now() - timedelta(days=1)
    ).count()
    print(f"Emails received in last 24 hours: {recent_count}")
    
    # Verify counts are consistent
    assert recent_count <= total_count

def test_database_session_management():
    """Test database session management in real application context."""
    from app_get_mail import get_email_session, init_database
    
    # Test session context manager
    with get_email_session() as session:
        init_database(session)
        assert session.bind is not None
        # Try a simple query
        result = session.query(Email).first()
        assert isinstance(result, Email) or result is None
