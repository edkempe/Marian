# reads emails with a given label ID and stores them a db
#

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import sqlite3
import pickle
import base64
import email
from datetime import datetime
import json

def get_gmail_service():
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    return build('gmail', 'v1', credentials=creds)

def init_database():
    conn = sqlite3.connect('email_store.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id TEXT PRIMARY KEY,
                  subject TEXT,
                  sender TEXT,
                  date TEXT,
                  body TEXT,
                  labels TEXT,
                  raw_data TEXT)''')
    conn.commit()
    return conn

def fetch_emails_by_label(label_id):
    service = get_gmail_service()
    try:
        # Get messages with specific label
        results = service.users().messages().list(
            userId='me',
            labelIds=[label_id],
            maxResults=100  # Adjust as needed
        ).execute()
        
        messages = results.get('messages', [])
        return messages
    except Exception as e:
        print(f'An error occurred: {e}')
        return []

def process_email(service, msg_id):
    try:
        # Get the message details
        message = service.users().messages().get(
            userId='me', 
            id=msg_id, 
            format='full'
        ).execute()

        # Extract headers
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

        # Get body
        if 'parts' in message['payload']:
            parts = message['payload']['parts']
            body = ''
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
            'date': date,
            'body': body,
            'labels': ','.join(message['labelIds']),
            'raw_data': json.dumps(message)
        }
    except Exception as e:
        print(f'Error processing message {msg_id}: {e}')
        return None

def main():
    print("Initializing database...")
    conn = init_database()
    service = get_gmail_service()
    
    # You can get label IDs by running list_labels.py
    label_id = 'Label_3766799458700700158'  # Replace with actual label ID
    
    print(f"Fetching emails with label: {label_id}")
    messages = fetch_emails_by_label(label_id)
    
    for msg in messages:
        email_data = process_email(service, msg['id'])
        if email_data:
            try:
                conn.execute('''INSERT OR REPLACE INTO emails
                               (id, subject, sender, date, body, labels, raw_data)
                               VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (email_data['id'], email_data['subject'], 
                            email_data['sender'], email_data['date'],
                            email_data['body'], email_data['labels'],
                            email_data['raw_data']))
                conn.commit()
                print(f"Stored email: {email_data['subject']}")
            except Exception as e:
                print(f"Error storing email: {e}")
    
    conn.close()

if __name__ == '__main__':
    main() 