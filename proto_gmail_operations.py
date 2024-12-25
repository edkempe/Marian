import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from shared_lib.gmail_lib import GmailAPI

SCOPES = ['https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.compose']

def get_gmail_service():
    """Get Gmail API service instance."""
    creds = None
    
    # Check if token.pickle exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials are not valid or don't exist, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
    """Create a message for an email."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': raw_message.decode()}

def send_message(service, user_id, message):
    """Send an email message."""
    try:
        message = service.users().messages().send(
            userId=user_id, body=message).execute()
        print(f'Message Id: {message["id"]}')
        return message
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def create_draft(service, user_id, message):
    """Create an email draft."""
    try:
        draft = service.users().drafts().create(
            userId=user_id, body={'message': message}).execute()
        print(f'Draft Id: {draft["id"]}')
        return draft
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def list_drafts(service, user_id):
    """List all drafts."""
    try:
        response = service.users().drafts().list(userId=user_id).execute()
        drafts = response.get('drafts', [])
        if not drafts:
            print('No drafts found.')
        else:
            print('Drafts:')
            for draft in drafts:
                print(f'Draft ID: {draft["id"]}')
        return drafts
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def test_gmail_operations():
    """Test various Gmail operations."""
    gmail = GmailAPI()
    
    # Test sending an email
    to = "test.user@example.com"
    subject = "Test Email with Label"
    message_text = "This is a test email that will have the Jexi_test label."
    
    # Create and send a message
    print("\nTesting sending email:")
    message = gmail.create_message(to, subject, message_text)
    sent_message = gmail.send_message(message)
    
    if sent_message:
        # Create the Jexi_test label
        print("\nCreating Jexi_test label:")
        label = gmail.create_label("Jexi_test")
        
        if label:
            # Add the label to the message we just sent
            print("\nAdding label to message:")
            gmail.add_label_to_message(sent_message['id'], [label['id']])
    
    # Test creating a draft
    draft_subject = "Test Draft Email"
    draft_message_text = "This is a test draft created using the Gmail API."
    draft_message = gmail.create_message(to, draft_subject, draft_message_text)
    print("\nTesting draft creation:")
    gmail.create_draft(draft_message)
    
    # List all drafts
    print("\nListing all drafts:")
    gmail.list_drafts()

if __name__ == '__main__':
    test_gmail_operations()
