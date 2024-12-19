#!/usr/bin/env python3
"""
Gmail Library
------------
Centralized module for Gmail API operations including:
- Authentication and service management
- Message operations (send, draft, fetch)
- Label management
- Email processing and parsing
"""

import os
import base64
import json
import pickle
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dateutil import parser
from pytz import timezone

# Constants
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.labels'
]
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'
UTC_TZ = timezone('UTC')

class GmailAPI:
    def __init__(self):
        """Initialize Gmail API client."""
        self.service = self._get_gmail_service()
        self.user_id = 'me'

    def _get_gmail_service(self):
        """Get authenticated Gmail API service instance."""
        creds = None
        
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired token...")
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(f"Credentials file '{CREDENTIALS_FILE}' not found")
                
                print("Starting new authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(TOKEN_FILE, 'wb') as token:
                print(f"Saving token to {TOKEN_FILE}")
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def fetch_emails(self, start_date=None, end_date=None, label=None, max_results=50):
        """
        Fetch emails from Gmail with optional date range and label filters.
        
        Args:
            start_date: Optional start date for fetching emails
            end_date: Optional end date for fetching emails
            label: Optional label to filter emails
            max_results: Maximum number of results to return (default: 50)
        
        Returns:
            List of message objects
        """
        try:
            query = ''
            if start_date:
                timestamp = int(start_date.timestamp())
                query += f'after:{timestamp} '

            if end_date:
                timestamp = int(end_date.timestamp())
                query += f'before:{timestamp} '

            if label:
                query += f'label:{label}'

            print(f"Using query: {query}")
            messages = []
            next_page_token = None
            
            while True:
                results = self.service.users().messages().list(
                    userId=self.user_id,
                    q=query.strip(),
                    maxResults=max_results,
                    pageToken=next_page_token
                ).execute()
                
                if 'messages' in results:
                    messages.extend(results['messages'])
                    next_page_token = results.get('nextPageToken')
                    if not next_page_token:
                        break
                else:
                    break

            return messages
        except Exception as e:
            print(f'An error occurred while fetching emails: {e}')
            return []

    def process_email(self, msg_id):
        """
        Process a single email message and extract its contents.
        
        Args:
            msg_id: The ID of the message to process
        
        Returns:
            Dict containing email data or None if error
        """
        try:
            message = self.service.users().messages().get(
                userId=self.user_id,
                id=msg_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

            try:
                date_obj = parser.parse(date_str)
                if not date_obj.tzinfo:
                    date_obj = date_obj.replace(tzinfo=UTC_TZ)
                date_utc = date_obj.astimezone(UTC_TZ)
                formatted_date = date_utc.strftime('%Y-%m-%d %H:%M:%S %z')
            except ValueError:
                print(f"Error parsing date for message {msg_id}")
                return None

            body = ''
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(part['body']['data']).decode()
                        break
            else:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode()

            return {
                'id': msg_id,
                'subject': subject,
                'sender': sender,
                'date': formatted_date,
                'body': body,
                'labels': message.get('labelIds', []),
                'raw_data': message
            }
        except Exception as e:
            print(f'Error processing message {msg_id}: {e}')
            return None

    def create_message(self, to, subject, message_text):
        """Create an email message."""
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

    def get_label_id(self, label_name):
        """Get label ID by name."""
        try:
            results = self.service.users().labels().list(userId=self.user_id).execute()
            labels = results.get('labels', [])
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    return label['id']
            return None
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
