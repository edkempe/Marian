"""
Gmail Email Fetcher
------------------
This script fetches emails from Gmail and stores them in a SQLite database.

Key Features:
- Fetches emails in batches with configurable time windows
- Stores emails with full content and metadata
- Supports incremental fetching (newer/older emails)
- Handles timezone conversion properly
- Prevents duplicate storage
- Displays dates in Mountain Time

Dependencies:
- google-auth-oauthlib: For Gmail API authentication
- google-api-python-client: For Gmail API access
- python-dateutil: For robust date parsing
- pytz: For timezone handling

Usage:
python get_mail.py [--newer] [--older] [--clear] [--label] [--list-labels]
  --newer: Fetch emails newer than the most recent in database
  --older: Fetch emails older than the oldest in database
  --clear: Clear the database before fetching
  --label: Filter emails by label
  --list-labels: List all available labels

Notes:
- Uses lib_gmail.py for Gmail API authentication
- Uses Unix timestamps for Gmail API queries for reliable date filtering
- Keeps a 1-minute overlap window when fetching newer emails
- Stores dates in UTC but displays in Mountain Time
- Default fetch window is 30 days when starting with empty database
- Label history is stored in a separate database (db_label_history.db)

Date: December 2024
"""

import sqlite3
import base64
import email
from datetime import datetime, timedelta
import json
import argparse
from pytz import timezone
import time
from dateutil import parser
from lib_gmail import GmailAPI

days_to_fetch = 5  # Temporarily set to 5 days to get roughly 50 emails
maxResults = 50  # Set max results to 50
MOUNTAIN_TZ = timezone('US/Mountain')
UTC_TZ = timezone('UTC')

def get_email_db():
    """Get connection to email database."""
    return sqlite3.connect('db_email_store.db')

def get_label_db():
    """Get connection to label history database."""
    return sqlite3.connect('db_label_history.db')

def init_database(conn=None):
    """Initialize the email database.
    
    Args:
        conn: Optional SQLite connection. If not provided, uses default connection.
    """
    if conn is None:
        conn = get_email_db()
    c = conn.cursor()
    
    # Create emails table
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id TEXT PRIMARY KEY,
                  thread_id TEXT,
                  subject TEXT,
                  sender TEXT,
                  date TEXT,
                  body TEXT,
                  labels TEXT,  
                  has_attachments BOOLEAN DEFAULT 0,
                  full_api_response TEXT)''')
    
    conn.commit()
    return conn

def init_label_database(conn=None):
    """Initialize the label history database.
    
    Args:
        conn: Optional SQLite connection. If not provided, uses default connection.
    """
    if conn is None:
        conn = get_label_db()
    c = conn.cursor()
    
    # Create gmail_labels table
    c.execute('''CREATE TABLE IF NOT EXISTS gmail_labels
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  label_id TEXT NOT NULL,  
                  name TEXT NOT NULL,  
                  type TEXT,  
                  message_list_visibility TEXT,
                  label_list_visibility TEXT,
                  is_active BOOLEAN DEFAULT 1,
                  first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  deleted_at TIMESTAMP)''')
    
    conn.commit()
    return conn

def get_gmail_service():
    """Get an authenticated Gmail service using lib_gmail."""
    gmail_api = GmailAPI()
    return gmail_api.service

def clear_database(conn):
    confirmation = input("Are you sure you want to clear the database? This action cannot be undone. (y/n): ")
    if confirmation.lower() == 'y':
        cursor = conn.cursor()
        cursor.execute('DELETE FROM emails')
        conn.commit()
        print("Database cleared successfully")
    else:
        print("Database clearing cancelled")

def get_label_id(service, label_name):
    """Get the ID of a label by its name."""
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        for label in labels:
            if label['name'].lower() == label_name.lower():
                return label['id']
        return None
    except Exception as e:
        print('Error getting label ID: {}'.format(e))
        return None

def fetch_emails(service, start_date=None, end_date=None, label=None):
    """Fetch emails from Gmail API."""
    try:
        # Base query
        query = ''
        
        # Add date filters if provided
        if start_date:
            timestamp = int(start_date.timestamp())
            query += 'after:{} '.format(timestamp)
        if end_date:
            timestamp = int(end_date.timestamp())
            query += 'before:{} '.format(timestamp)
            
        # Add label filter if provided
        if label:
            label_id = get_label_id(service, label)
            if label_id:
                query += 'label:{} '.format(label_id)
            else:
                print('Label not found: {}'.format(label))
                return []
        
        print('Fetching emails with query: {}'.format(query))
        messages = []
        next_page_token = None
        
        while True:
            results = service.users().messages().list(
                userId='me',
                q=query.strip(),
                maxResults=maxResults,
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
        print('An error occurred while fetching emails: {}'.format(e))
        return []

def process_email(service, msg_id, conn):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM emails WHERE id = ?', (msg_id,))
        if cursor.fetchone():
            return None

        message = service.users().messages().get(
            userId='me',
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
            print('Error parsing date for message {}'.format(msg_id))
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
            'thread_id': message['threadId'],  
            'subject': subject,
            'sender': sender,
            'date': formatted_date,
            'body': body,
            'labels': ','.join(message['labelIds']),
            'full_api_response': json.dumps(message)
        }
    except Exception as e:
        print('Error processing message {}: {}'.format(msg_id, e))
        return None

def get_oldest_email_date(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT MIN(date) FROM emails')
    oldest_date = cursor.fetchone()[0]
    if oldest_date:
        return parser.parse(oldest_date).replace(tzinfo=UTC_TZ)
    return None

def get_newest_email_date(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(date) FROM emails')
    newest_date = cursor.fetchone()[0]
    if newest_date:
        return parser.parse(newest_date).replace(tzinfo=UTC_TZ)
    return None

def fetch_older_emails(conn, service, label=None):
    oldest_date = get_oldest_email_date(conn)
    if oldest_date:
        messages = fetch_emails(service, end_date=oldest_date, label=label)
        return messages
    return []

def fetch_newer_emails(conn, service, label=None):
    newest_date = get_newest_email_date(conn)
    if newest_date:
        # Add 1-minute overlap to avoid missing emails
        start_date = newest_date - timedelta(minutes=1)
        messages = fetch_emails(service, start_date=start_date, label=label)
        return messages
    return []

def count_emails(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM emails')
    return cursor.fetchone()[0]

def list_labels(service):
    """List all available Gmail labels and store them in the database with history."""
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        # Store labels in database
        conn = get_label_db()
        c = conn.cursor()
        
        # Get current timestamp
        current_time = datetime.utcnow().isoformat()
        
        # Mark all existing active labels as potentially inactive
        # We'll re-activate ones we still see
        c.execute('''UPDATE gmail_labels 
                    SET is_active = 0, 
                        deleted_at = ? 
                    WHERE is_active = 1''', (current_time,))
        
        # Process current labels
        for label in labels:
            # Check if this exact label configuration exists
            c.execute('''SELECT id, is_active, deleted_at 
                        FROM gmail_labels 
                        WHERE label_id = ? 
                        AND name = ? 
                        AND type = ? 
                        AND message_list_visibility = ? 
                        AND label_list_visibility = ?''',
                     (label['id'],
                      label['name'],
                      label.get('type', ''),
                      label.get('messageListVisibility', ''),
                      label.get('labelListVisibility', '')))
            
            existing = c.fetchone()
            
            if existing:
                # This exact configuration exists, just update timestamps
                c.execute('''UPDATE gmail_labels 
                           SET is_active = 1,
                               last_seen_at = ?,
                               deleted_at = NULL
                           WHERE id = ?''',
                        (current_time, existing[0]))
            else:
                # Insert new record
                c.execute('''INSERT INTO gmail_labels 
                           (label_id, name, type, 
                            message_list_visibility, label_list_visibility,
                            first_seen_at, last_seen_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (label['id'],
                         label['name'],
                         label.get('type', ''),
                         label.get('messageListVisibility', ''),
                         label.get('labelListVisibility', ''),
                         current_time,
                         current_time))
        
        conn.commit()
        
        # Print current labels with their history
        print("\nAvailable labels:")
        c.execute('''SELECT label_id, name, first_seen_at, 
                           CASE WHEN is_active = 1 
                                THEN 'Active' 
                                ELSE 'Inactive (removed ' || deleted_at || ')' 
                           END as status
                    FROM gmail_labels
                    ORDER BY name, first_seen_at DESC''')
        
        for row in c.fetchall():
            print(f"- {row[1]} (ID: {row[0]}, {row[3]}, First seen: {row[2]})")
        
        conn.close()
        return labels
    except Exception as e:
        print('Error listing labels: {}'.format(e))
        return []

def main():
    """Main function to fetch emails."""
    parser = argparse.ArgumentParser(description='Fetch emails from Gmail')
    parser.add_argument('--newer', action='store_true',
                       help='Fetch emails newer than most recent in database')
    parser.add_argument('--older', action='store_true',
                       help='Fetch emails older than oldest in database')
    parser.add_argument('--clear', action='store_true',
                       help='Clear the database before fetching')
    parser.add_argument('--label', type=str,
                       help='Filter emails by label')
    parser.add_argument('--list-labels', action='store_true',
                       help='List all available labels')
    args = parser.parse_args()
    
    # Get Gmail API service
    service = get_gmail_service()
    
    # Initialize databases
    conn = init_database()
    label_conn = init_label_database()
    
    if args.clear:
        clear_database(conn)
    
    if args.list_labels:
        list_labels(service)
        return
    
    label_id = None
    if args.label:
        label_id = get_label_id(service, args.label)
        if not label_id:
            print(f"Label '{args.label}' not found")
            return
    
    if args.newer:
        messages = fetch_newer_emails(conn, service, label_id)
    elif args.older:
        messages = fetch_older_emails(conn, service, label_id)
    else:
        # Default: fetch emails from last N days
        end_date = datetime.now(MOUNTAIN_TZ)
        start_date = end_date - timedelta(days=days_to_fetch)
        messages = fetch_emails(service, start_date, end_date, label_id)
    
    print("Processing {} messages...".format(len(messages) if messages else 0))

    for msg in messages:
        email_data = process_email(service, msg['id'], conn)
        if email_data:
            try:
                conn.execute('''INSERT OR IGNORE INTO emails
                                (id, thread_id, subject, sender, date, body, labels, has_attachments, full_api_response)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (email_data['id'], email_data.get('thread_id', ''),  
                              email_data['subject'], email_data['sender'],
                              email_data['date'], email_data['body'],
                              email_data['labels'], False, email_data['full_api_response']))
                conn.commit()

                # Display in Mountain Time
                utc_date = datetime.strptime(email_data['date'], '%Y-%m-%d %H:%M:%S %z')
                display_date = utc_date.astimezone(MOUNTAIN_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')
                print("Stored email: {} - {}".format(display_date, email_data['subject']))
                
            except Exception as e:
                print("Error storing email: {}".format(e))

    final_count = count_emails(conn)
    print("Final email count: {}".format(final_count))
    conn.close()
    label_conn.close()

if __name__ == '__main__':
    main()