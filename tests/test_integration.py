"""Integration tests for Gmail API functionality."""
import pytest
from datetime import datetime, timedelta
from lib_gmail import GmailAPI
from app_get_mail import fetch_emails, process_email, list_labels
from models.email import Email

def test_gmail_authentication():
    """Test Gmail API authentication."""
    gmail = GmailAPI()
    assert gmail.service is not None
    
    # Test basic profile access
    profile = gmail.service.users().getProfile(userId='me').execute()
    assert 'emailAddress' in profile
    print(f"Authenticated as: {profile['emailAddress']}")

def test_label_operations():
    """Test Gmail label operations."""
    gmail = GmailAPI()
    
    # List all labels
    labels = list_labels(gmail.service)
    assert len(labels) > 0
    
    # Print found labels
    print("\nAvailable labels:")
    for label in labels:
        print(f"- {label['name']} ({label['id']})")
    
    # Test getting specific system labels
    system_labels = ['INBOX', 'SENT', 'DRAFT', 'SPAM']
    for label in system_labels:
        label_id = gmail.get_label_id(label)
        assert label_id is not None
        print(f"\nFound {label} label: {label_id}")

def test_email_fetching():
    """Test fetching emails from Gmail."""
    gmail = GmailAPI()
    
    # Fetch recent emails (last 7 days)
    start_date = datetime.now() - timedelta(days=7)
    messages = fetch_emails(gmail.service, start_date=start_date)
    
    assert len(messages) > 0
    print(f"\nFetched {len(messages)} recent emails")
    
    # Test fetching with label filter
    inbox_messages = fetch_emails(gmail.service, label='INBOX', 
                                start_date=start_date)
    print(f"Found {len(inbox_messages)} INBOX emails")
    
    # Get details of first email
    if inbox_messages:
        first_msg = inbox_messages[0]
        msg_details = gmail.service.users().messages().get(
            userId='me', id=first_msg['id']).execute()
        
        headers = {h['name']: h['value'] for h in msg_details['payload']['headers']}
        print("\nMost recent email:")
        print(f"From: {headers.get('From', 'Unknown')}")
        print(f"Subject: {headers.get('Subject', 'No subject')}")
        print(f"Date: {headers.get('Date', 'Unknown')}")

def test_email_processing(test_db_session):
    """Test processing and storing emails."""
    gmail = GmailAPI()
    
    # Fetch a few recent emails
    messages = fetch_emails(gmail.service, 
                          start_date=datetime.now() - timedelta(days=1))
    
    if not messages:
        pytest.skip("No recent emails found for testing")
    
    # Process first 3 emails
    for msg in messages[:3]:
        process_email(gmail.service, msg['id'], test_db_session)
    
    # Verify storage
    stored_emails = test_db_session.query(Email).all()
    assert len(stored_emails) > 0
    
    # Print processed emails
    print("\nProcessed emails:")
    for email in stored_emails:
        print(f"\nID: {email.id}")
        print(f"Subject: {email.subject}")
        print(f"From: {email.from_address}")
        print(f"Labels: {email.labels}")
        print(f"Date: {email.received_date}")
