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
    
    # Create emails table with updated schema
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id TEXT PRIMARY KEY,
                  thread_id TEXT,
                  subject TEXT,
                  from_address TEXT,
                  to_address TEXT,
                  received_date TEXT,
                  content TEXT,
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
                  is_active BOOLEAN DEFAULT 1,
                  first_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  deleted_at DATETIME)''')
    
    conn.commit()
    return conn

def get_gmail_service():
    """Get an authenticated Gmail service using lib_gmail."""
    gmail_api = GmailAPI()
    return gmail_api.get_service()

def clear_database(conn=None):
    """Clear all data from the email database."""
    if conn is None:
        conn = get_email_db()
    c = conn.cursor()
    c.execute('DELETE FROM emails')
    conn.commit()
    return conn

def get_label_id(service, label_name):
    """Get the ID of a label by its name."""
    try:
        labels = list_labels(service)
        for label in labels:
            if label['name'] == label_name:
                return label['id']
        print(f"Label not found: {label_name}")
        return None
    except Exception as e:
        print(f"Error getting label ID: {str(e)}")
        return None

def fetch_emails(service, start_date=None, end_date=None, label=None):
    """Fetch emails from Gmail API.
    
    Args:
        service: Gmail API service instance
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        label: Optional label to filter by
    
    Returns:
        List of email messages
    """
    try:
        # Build query
        query = []
        if start_date:
            query.append(f'after:{int(start_date.timestamp())}')
        if end_date:
            query.append(f'before:{int(end_date.timestamp())}')
        if label:
            label_id = get_label_id(service, label)
            if not label_id:
                return []
        
        query_str = ' '.join(query)
        print(f"Fetching emails with query: {query_str}")
        
        # Get messages
        request = service.users().messages().list(
            userId='me',
            q=query_str,
            maxResults=maxResults,
            labelIds=[label_id] if label else None
        )
        
        messages = []
        while request:
            response = request.execute()
            if 'messages' in response:
                messages.extend(response['messages'])
            request = service.users().messages().list_next(request, response)
            
            if len(messages) >= maxResults:
                break
        
        return messages
    except Exception as e:
        print(f"Error fetching emails: {str(e)}")
        return []

def process_email(service, msg_id, conn):
    """Process a single email message and store in database.
    
    Args:
        service: Gmail API service instance
        msg_id: ID of message to process
        conn: Database connection
    
    Returns:
        Dictionary containing processed email data
    """
    try:
        # Get full message
        msg = service.users().messages().get(userId='me', id=msg_id).execute()
        
        # Extract headers
        headers = {header['name']: header['value'] 
                  for header in msg['payload']['headers']}
        
        # Get body content
        if 'body' in msg['payload']:
            body = msg['payload']['body'].get('data', '')
            if body:
                body = base64.urlsafe_b64decode(body).decode('utf-8')
        else:
            body = ''
        
        # Process date
        date_str = headers.get('Date', '')
        if date_str:
            date = parser.parse(date_str)
            if date.tzinfo is None:
                date = UTC_TZ.localize(date)
            date = date.astimezone(UTC_TZ)
        else:
            date = datetime.now(UTC_TZ)
        
        # Store in database
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO emails (
                id, thread_id, subject, from_address, to_address, received_date,
                content, labels, has_attachments, full_api_response
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            msg_id,
            msg['threadId'],
            headers.get('Subject', ''),
            headers.get('From', ''),
            headers.get('To', ''),
            date.isoformat(),
            body,
            ','.join(msg.get('labelIds', [])),
            bool(msg.get('payload', {}).get('parts', [])),
            json.dumps(msg)
        ))
        conn.commit()
        
        return {
            'id': msg_id,
            'thread_id': msg['threadId'],
            'subject': headers.get('Subject', ''),
            'from_address': headers.get('From', ''),
            'to_address': headers.get('To', ''),
            'received_date': date.isoformat(),
            'content': body,
            'labels': msg.get('labelIds', []),
            'has_attachments': bool(msg.get('payload', {}).get('parts', [])),
        }
    except Exception as e:
        print(f"Error processing message {msg_id}: {str(e)}")
        return None

def get_oldest_email_date(conn):
    """Get the date of the oldest email in the database."""
    c = conn.cursor()
    c.execute('SELECT MIN(received_date) FROM emails')
    date_str = c.fetchone()[0]
    return parser.parse(date_str) if date_str else None

def get_newest_email_date(conn):
    """Get the date of the newest email in the database."""
    c = conn.cursor()
    c.execute('SELECT MAX(received_date) FROM emails')
    date_str = c.fetchone()[0]
    return parser.parse(date_str) if date_str else None

def fetch_older_emails(conn, service, label=None):
    """Fetch emails older than the oldest in database."""
    oldest_date = get_oldest_email_date(conn)
    if oldest_date:
        return fetch_emails(service, end_date=oldest_date, label=label)
    return []

def fetch_newer_emails(conn, service, label=None):
    """Fetch emails newer than the newest in database."""
    newest_date = get_newest_email_date(conn)
    if newest_date:
        # Add 1-minute overlap to avoid missing emails
        start_date = newest_date - timedelta(minutes=1)
        return fetch_emails(service, start_date=start_date, label=label)
    return []

def count_emails(conn):
    """Get total number of emails in database."""
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM emails')
    return c.fetchone()[0]

def list_labels(service):
    """List all available Gmail labels and store them in the database with history.
    
    Args:
        service: Gmail API service instance
    
    Returns:
        List of label dictionaries
    """
    try:
        # Get current time in UTC
        current_time = datetime.utcnow().isoformat()
        
        # Get all labels from Gmail API
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        # Connect to label database
        conn = get_label_db()
        cursor = conn.cursor()
        
        # Initialize database if needed
        init_label_database(conn)
        
        # Update label history
        for label in labels:
            # Check if label exists
            cursor.execute('''
                SELECT id, is_active, deleted_at 
                FROM gmail_labels 
                WHERE label_id = ?
            ''', (label['id'],))
            result = cursor.fetchone()
            
            if result:
                # Label exists, update last_seen_at
                label_id, is_active, deleted_at = result
                if not is_active:
                    # Reactivate label if it was deleted
                    cursor.execute('''
                        UPDATE gmail_labels 
                        SET is_active = 1, 
                            deleted_at = NULL,
                            last_seen_at = ?
                        WHERE id = ?
                    ''', (current_time, label_id))
                else:
                    # Just update last_seen_at
                    cursor.execute('''
                        UPDATE gmail_labels 
                        SET last_seen_at = ?
                        WHERE id = ?
                    ''', (current_time, label_id))
            else:
                # New label, insert it
                cursor.execute('''
                    INSERT INTO gmail_labels (
                        label_id, name, type, 
                        first_seen_at, last_seen_at
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    label['id'], 
                    label['name'],
                    label.get('type', ''),
                    current_time,
                    current_time
                ))
        
        # Mark labels not seen in this update as deleted
        cursor.execute('''
            UPDATE gmail_labels 
            SET is_active = 0, 
                deleted_at = ? 
            WHERE last_seen_at < ? 
            AND is_active = 1
        ''', (current_time, current_time))
        
        conn.commit()
        conn.close()
        
        return labels
    except Exception as e:
        print(f"Error listing labels: {str(e)}")
        return []

def main():
    """Main function to fetch emails."""
    parser = argparse.ArgumentParser(description='Fetch emails from Gmail')
    parser.add_argument('--newer', action='store_true',
                      help='Fetch emails newer than most recent in database')
    parser.add_argument('--older', action='store_true',
                      help='Fetch emails older than oldest in database')
    parser.add_argument('--clear', action='store_true',
                      help='Clear database before fetching')
    parser.add_argument('--label',
                      help='Filter emails by label')
    parser.add_argument('--list-labels', action='store_true',
                      help='List all available labels')
    args = parser.parse_args()
    
    # Get Gmail service
    service = get_gmail_service()
    if not service:
        print("Failed to get Gmail service")
        return
    
    # List labels if requested
    if args.list_labels:
        labels = list_labels(service)
        print("\nAvailable labels:")
        for label in labels:
            print(f"- {label['name']} ({label['id']})")
        return
    
    # Get database connection
    conn = get_email_db()
    
    # Initialize database
    init_database(conn)
    
    # Clear database if requested
    if args.clear:
        clear_database(conn)
        print("Database cleared")
    
    # Fetch emails based on arguments
    if args.newer:
        messages = fetch_newer_emails(conn, service, args.label)
    elif args.older:
        messages = fetch_older_emails(conn, service, args.label)
    else:
        # Default: fetch last N days of emails
        end_date = datetime.now(UTC_TZ)
        start_date = end_date - timedelta(days=days_to_fetch)
        messages = fetch_emails(service, start_date, end_date, args.label)
    
    # Process messages
    for msg in messages:
        process_email(service, msg['id'], conn)
    
    # Print summary
    total_emails = count_emails(conn)
    print(f"\nTotal emails in database: {total_emails}")
    
    conn.close()

if __name__ == '__main__':
    main()