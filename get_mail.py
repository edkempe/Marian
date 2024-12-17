from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import sqlite3
import pickle
import base64
import email
from datetime import datetime, timedelta
import json
import argparse
from pytz import timezone
import time
from dateutil import parser

days_to_fetch = 1  # Number of days to fetch emails
maxResults = 500  # Gmail API limit is 500

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

def clear_database(conn):
    confirmation = input("Are you sure you want to clear the database? This action cannot be undone. (y/n): ")
    if confirmation.lower() == 'y':
        cursor = conn.cursor()
        cursor.execute('DELETE FROM emails')
        conn.commit()
        print("Database cleared successfully")
    else:
        print("Database clearing cancelled")

def fetch_emails(start_date=None, end_date=None):
    service = get_gmail_service()
    try:
        query = ''
        if start_date:
            start_timestamp = int(time.mktime(start_date.astimezone(timezone('UTC')).timetuple()))
            query += f'after:{start_timestamp} '
        if end_date:
            end_timestamp = int(time.mktime(end_date.astimezone(timezone('UTC')).timetuple()))
            query += f'before:{end_timestamp}'
        messages = []
        next_page_token = None
        while True:
            results = service.users().messages().list(
                userId='me',
                q=query.strip(),
                maxResults=maxResults,
                pageToken=next_page_token
            ).execute()
            messages.extend(results.get('messages', []))
            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break
        return messages
    except Exception as e:
        print(f'An error occurred: {e}')
        return []

def process_email(service, msg_id, conn):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM emails WHERE id = ?', (msg_id,))
        if cursor.fetchone():
            print(f"Duplicate email found, skipping: {msg_id}")
            return None

        message = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

        try:
            date_obj = parser.parse(date)
        except ValueError:
            print(f"Error parsing date for message {msg_id}: {date}")
            date_obj = datetime.now(timezone('UTC'))

        # Store in UTC
        date_utc = date_obj.astimezone(timezone('UTC'))
        formatted_date = date_utc.strftime('%Y-%m-%d %H:%M:%S %z')

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
            'date': formatted_date,
            'body': body,
            'labels': ','.join(message['labelIds']),
            'raw_data': json.dumps(message)
        }
    except Exception as e:
        print(f'Error processing message {msg_id}: {e}')
        return None

def get_oldest_email_date(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT MIN(date) FROM emails')
    oldest_date = cursor.fetchone()[0]
    if oldest_date:
        return parser.parse(oldest_date).replace(tzinfo=timezone('UTC'))
    return None

def get_newest_email_date(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(date) FROM emails')
    newest_date = cursor.fetchone()[0]
    if newest_date:
        return parser.parse(newest_date).replace(tzinfo=timezone('UTC'))
    return None

def fetch_older_emails(conn):
    oldest_date = get_oldest_email_date(conn)
    if oldest_date:
        end_date = oldest_date - timedelta(seconds=1)
        start_date = end_date - timedelta(days=days_to_fetch)
        return fetch_emails(start_date, end_date)
    return []

def fetch_newer_emails(conn):
    newest_date = get_newest_email_date(conn)
    if newest_date:
        start_date = newest_date + timedelta(seconds=1)
        end_date = datetime.now(timezone('UTC'))
        return fetch_emails(start_date, end_date)
    return []

def count_emails(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM emails')
    return cursor.fetchone()[0]

def main():
    parser = argparse.ArgumentParser(description='Fetch emails from Gmail')
    parser.add_argument('--older', action='store_true', help='Fetch older emails')
    parser.add_argument('--newer', action='store_true', help='Fetch newer emails')
    parser.add_argument('--clear', action='store_true', help='Clear the database before fetching')
    args = parser.parse_args()

    print("Initializing database...")
    conn = init_database()
    service = get_gmail_service()

    if args.clear:
        clear_database(conn)

    total_emails = count_emails(conn)
    
    if total_emails == 0:
        print(f"Database is empty. Fetching last {days_to_fetch} days of emails.")
        end_date = datetime.now(timezone('UTC'))
        start_date = end_date - timedelta(days=days_to_fetch)
        messages = fetch_emails(start_date, end_date)
    elif args.older:
        messages = fetch_older_emails(conn)
    elif args.newer:
        messages = fetch_newer_emails(conn)
    else:
        messages = fetch_newer_emails(conn)

    for msg in messages:
        email_data = process_email(service, msg['id'], conn)
        if email_data:
            try:
                conn.execute('''INSERT OR IGNORE INTO emails
                (id, subject, sender, date, body, labels, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (email_data['id'], email_data['subject'],
                email_data['sender'], email_data['date'],
                email_data['body'], email_data['labels'],
                email_data['raw_data']))
                conn.commit()
                
                # Convert UTC date to Mountain Time for display
                utc_date = datetime.strptime(email_data['date'], '%Y-%m-%d %H:%M:%S %z')
                mountain_tz = timezone('US/Mountain')
                display_date = utc_date.astimezone(mountain_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
                
                print(f"Stored email: {display_date} - {email_data['subject']}")
            except Exception as e:
                print(f"Error storing email: {e}")

    conn.close()

if __name__ == '__main__':
    main()
