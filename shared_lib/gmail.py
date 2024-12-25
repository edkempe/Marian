#!/usr/bin/env python3
"""
Gmail Library
------------
Centralized module for Gmail API operations including:
- Authentication and service management
- Message operations (send, draft, fetch)
- Label management and synchronization
- Email processing and parsing
"""

import os
import base64
import json
import pickle
import sqlite3
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dateutil import parser
from pytz import timezone
import logging

# Constants
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.labels'
]
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'
DEFAULT_LABEL_DB = 'email_labels.db'
UTC_TZ = timezone('UTC')

logger = logging.getLogger(__name__)

class GmailAPI:
    """Main class for Gmail API operations"""
    
    def __init__(self, label_db_path=DEFAULT_LABEL_DB):
        self.label_db_path = label_db_path
        self.service = self._get_gmail_service()
        
    def _get_gmail_service(self):
        """Get authenticated Gmail API service instance."""
        creds = self._authenticate_gmail()
        return build('gmail', 'v1', credentials=creds)
    
    def _authenticate_gmail(self):
        """Authenticate with Gmail API."""
        try:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"Credentials file '{CREDENTIALS_FILE}' not found")

            creds = None
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("Refreshing expired token...")
                    creds.refresh(Request())
                else:
                    print("Starting new authentication flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                    
                with open(TOKEN_FILE, 'wb') as token:
                    print(f"Saving token to {TOKEN_FILE}")
                    pickle.dump(creds, token)

            return creds

        except Exception as e:
            print(f"Authentication error: {str(e)}")
            raise

    def setup_label_database(self):
        """Create and setup the labels database"""
        conn = sqlite3.connect(self.label_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gmail_labels (
                label_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                message_list_visibility TEXT,
                label_list_visibility TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        return conn

    def sync_labels(self):
        """Sync Gmail labels with local database"""
        conn = self.setup_label_database()
        cursor = conn.cursor()
        
        try:
            # Get all labels from Gmail
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Begin transaction
            cursor.execute('BEGIN TRANSACTION')
            
            # Store each label
            for label in labels:
                cursor.execute('''
                    INSERT OR REPLACE INTO gmail_labels 
                    (label_id, name, type, message_list_visibility, label_list_visibility)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    label['id'],
                    label['name'],
                    label.get('type'),
                    label.get('messageListVisibility'),
                    label.get('labelListVisibility')
                ))
            
            conn.commit()
            print(f"Successfully synced {len(labels)} labels")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error syncing labels: {str(e)}")
            return False
            
        finally:
            conn.close()

    def get_label_name(self, label_id):
        """Get label name from label ID"""
        conn = sqlite3.connect(self.label_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT name FROM gmail_labels WHERE label_id = ?', (label_id,))
            result = cursor.fetchone()
            return result[0] if result else label_id
            
        finally:
            conn.close()

    def get_label_id(self, label_name):
        """Get label ID from label name"""
        conn = sqlite3.connect(self.label_db_path)
        cursor = conn.cursor()
        
        try:
            # Try exact match first
            cursor.execute('SELECT label_id FROM gmail_labels WHERE name = ?', (label_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            # If no exact match, try case-insensitive match
            cursor.execute('SELECT label_id FROM gmail_labels WHERE LOWER(name) = LOWER(?)', (label_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            return None
            
        finally:
            conn.close()

    def process_email(self, msg_id):
        """Process a single email message.
        
        Args:
            msg_id: Gmail message ID (string)
            
        Returns:
            Dict containing email data or None if processing fails
            
        Raises:
            ValueError: If msg_id is not a string or is empty
            RuntimeError: If Gmail API response is missing required fields
        """
        if not isinstance(msg_id, str) or not msg_id.strip():
            raise ValueError("Message ID must be a non-empty string")
            
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()

            # Validate required fields
            if 'id' not in message:
                raise RuntimeError("Gmail API response missing 'id' field")
            if 'threadId' not in message:
                raise RuntimeError("Gmail API response missing 'threadId' field")
            if 'payload' not in message:
                raise RuntimeError("Gmail API response missing 'payload' field")

            payload = message['payload']
            headers = payload.get('headers', [])

            # Extract header fields
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), None)
            from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), None)

            # Get body content
            body = ''
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'body' in part and 'data' in part['body']:
                            try:
                                body = base64.urlsafe_b64decode(part['body']['data']).decode()
                                break
                            except Exception as e:
                                logger.error(f"Error decoding email body: {str(e)}")
            elif 'body' in payload and 'data' in payload['body']:
                try:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode()
                except Exception as e:
                    logger.error(f"Error decoding email body: {str(e)}")

            return {
                'id': message['id'],
                'thread_id': message['threadId'],
                'subject': subject,
                'date': date,
                'sender': from_email,
                'body': body,
                'labels': [self.get_label_name(label_id) for label_id in message.get('labelIds', [])],
                'full_api_response': json.dumps(message)
            }

        except googleapiclient.errors.HttpError as e:
            if e.resp.status == 404:
                logger.error(f"Message {msg_id} not found in Gmail")
            else:
                logger.error(f"Gmail API error for message {msg_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing message {msg_id}: {str(e)}")
            return None

    def send_email(self, to, subject, body, reply_to=None):
        """Send an email"""
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if reply_to:
                message.add_header('In-Reply-To', reply_to)
                message.add_header('References', reply_to)

            msg = MIMEText(body)
            message.attach(msg)

            raw = base64.urlsafe_b64encode(message.as_bytes())
            raw = raw.decode()
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
