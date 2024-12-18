import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

class GmailAPI:
    def __init__(self):
        self.service = self._get_gmail_service()
        self.user_id = 'me'

    def _get_gmail_service(self):
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
                    'credentials.json', 
                    ['https://www.googleapis.com/auth/gmail.modify',
                     'https://www.googleapis.com/auth/gmail.compose',
                     'https://www.googleapis.com/auth/gmail.labels'])
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def create_message(self, to, subject, message_text):
        """Create a message for an email."""
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject

        msg = MIMEText(message_text)
        message.attach(msg)

        raw_message = base64.urlsafe_b64encode(message.as_bytes())
        return {'raw': raw_message.decode()}

    def send_message(self, message):
        """Send an email message."""
        try:
            message = self.service.users().messages().send(
                userId=self.user_id, body=message).execute()
            print(f'Message Id: {message["id"]}')
            return message
        except Exception as e:
            print(f'An error occurred: {e}')
            return None

    def create_draft(self, message):
        """Create an email draft."""
        try:
            draft = self.service.users().drafts().create(
                userId=self.user_id, body={'message': message}).execute()
            print(f'Draft Id: {draft["id"]}')
            return draft
        except Exception as e:
            print(f'An error occurred: {e}')
            return None

    def list_drafts(self):
        """List all drafts."""
        try:
            response = self.service.users().drafts().list(userId=self.user_id).execute()
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

    def create_label(self, label_name):
        """Create a new label."""
        try:
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            label = self.service.users().labels().create(
                userId=self.user_id, body=label_object).execute()
            print(f'Label created: {label["name"]} (ID: {label["id"]})')
            return label
        except Exception as e:
            print(f'An error occurred: {e}')
            return None

    def add_label_to_message(self, message_id, label_ids):
        """Add one or more labels to a message."""
        try:
            message = self.service.users().messages().modify(
                userId=self.user_id,
                id=message_id,
                body={'addLabelIds': label_ids}
            ).execute()
            print(f'Labels added to message: {message["id"]}')
            return message
        except Exception as e:
            print(f'An error occurred: {e}')
            return None

    def get_label_id(self, label_name):
        """Get label ID by name."""
        try:
            results = self.service.users().labels().list(userId=self.user_id).execute()
            labels = results.get('labels', [])
            for label in labels:
                if label['name'] == label_name:
                    return label['id']
            return None
        except Exception as e:
            print(f'An error occurred: {e}')
            return None
