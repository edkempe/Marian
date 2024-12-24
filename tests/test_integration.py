"""Integration tests for Gmail API functionality."""
import pytest
from datetime import datetime, timedelta
from lib_gmail import GmailAPI
from app_get_mail import fetch_emails, process_email, list_labels
from models.email import Email
from email.utils import parsedate_to_datetime

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

def test_email_fetching(gmail_api):
    """Test fetching emails from Gmail."""
    # Fetch recent emails (last 7 days)
    start_date = datetime.now() - timedelta(days=7)
    messages = fetch_emails(gmail_api.service, start_date=start_date)
    
    assert len(messages) > 0
    print(f"\nFetched {len(messages)} recent emails")
    
    # Test fetching with label filter
    inbox_messages = fetch_emails(gmail_api.service, label='INBOX', 
                                start_date=start_date)
    print(f"Found {len(inbox_messages)} INBOX emails")
    
    # Get details of first email
    if inbox_messages:
        first_msg = inbox_messages[0]
        msg_details = gmail_api.service.users().messages().get(
            userId='me', id=first_msg['id']).execute()
        
        headers = {h['name']: h['value'] for h in msg_details['payload']['headers']}
        print("\nMost recent email:")
        print(f"From: {headers.get('From', 'Unknown')}")
        print(f"Subject: {headers.get('Subject', 'No subject')}")
        print(f"Date: {headers.get('Date', 'Unknown')}")

def test_email_processing(gmail_api, test_db_session):
    """Test processing and storing emails."""
    # Fetch a few recent emails
    messages = fetch_emails(gmail_api.service, 
                          start_date=datetime.now() - timedelta(days=1))
    
    if not messages:
        pytest.skip("No recent emails found for testing")
    
    # Process first 3 emails
    processed = 0
    for msg in messages[:3]:
        try:
            # Get full message details
            full_msg = gmail_api.service.users().messages().get(
                userId='me', id=msg['id']).execute()
            
            # Create email object
            headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}
            email = Email(
                id=full_msg['id'],
                thread_id=full_msg['threadId'],
                subject=headers.get('Subject', ''),
                from_address=headers.get('From', ''),
                to_address=headers.get('To', ''),
                received_date=parsedate_to_datetime(headers.get('Date', '')),
                labels=','.join(full_msg.get('labelIds', [])),
                content=''  # We'll add content processing later
            )
            
            # Store in database
            test_db_session.add(email)
            test_db_session.commit()
            processed += 1
            
            print(f"\nProcessed email {email.id}:")
            print(f"Subject: {email.subject}")
            print(f"From: {email.from_address}")
            print(f"Labels: {email.labels}")
            
        except Exception as e:
            print(f"Error processing message {msg['id']}: {str(e)}")
    
    # Verify storage
    stored_emails = test_db_session.query(Email).all()
    assert len(stored_emails) == processed
    
    # Print processed emails
    print("\nStored emails:")
    for email in stored_emails:
        print(f"\nID: {email.id}")
        print(f"Subject: {email.subject}")
        print(f"From: {email.from_address}")
        print(f"Labels: {email.labels}")
        print(f"Date: {email.received_date}")
