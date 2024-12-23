"""Gmail email fetching and storage module.

This module provides functionality to:
1. Fetch emails from Gmail API
2. Store emails in a local database
3. Track email labels and their history

Requirements:
- google-api-python-client: For Gmail API access
- python-dateutil: For robust date parsing
- pytz: For timezone handling
- sqlalchemy: For database operations

Usage:
python get_mail.py [--newer] [--older] [--clear] [--label] [--list-labels]
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pytz import timezone
import time
from dateutil import parser
from base64 import urlsafe_b64decode

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from models.base import Base
from models.email import Email
from models.gmail_label import GmailLabel
from lib_gmail import GmailAPI
from database.config import get_email_session, get_analysis_session, init_db

# Configuration
days_to_fetch = 5  # Temporarily set to 5 days to get roughly 50 emails
maxResults = 50  # Set max results to 50
UTC_TZ = timezone('UTC')

def init_database(session: Session = None) -> Session:
    """Initialize the email database schema."""
    # Import models to ensure they are registered with SQLAlchemy
    from models.base import Base
    from models.email import Email
    from models.email_analysis import EmailAnalysis
    from models.gmail_label import GmailLabel
    
    init_db()
    return session

def init_label_database(session: Session = None) -> Session:
    """Initialize the label database schema."""
    # Import models to ensure they are registered with SQLAlchemy
    from models.base import Base
    from models.email import Email
    from models.email_analysis import EmailAnalysis
    from models.gmail_label import GmailLabel
    
    init_db()
    return session

def get_gmail_service():
    """Get an authenticated Gmail service."""
    gmail_api = GmailAPI()
    return gmail_api.get_service()

def clear_database(session: Session = None) -> Session:
    """Clear all data from the email database."""
    with get_email_session() as session:
        session.query(Email).delete()
        session.commit()
    return session

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

def get_email_engine():
    """Get SQLAlchemy engine for email database."""
    return get_email_session().get_bind()

def get_label_engine():
    """Get SQLAlchemy engine for label database."""
    return get_email_session().get_bind()

def get_email_session() -> Session:
    """Get SQLAlchemy session for email database."""
    return get_email_session()

def get_label_session() -> Session:
    """Get SQLAlchemy session for label database."""
    return get_email_session()

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

def process_email(service, msg_id, session):
    """Process a single email message and store it in the database."""
    try:
        # Get the full message details
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        
        # Extract email data
        headers = {header['name']: header['value'] for header in message['payload']['headers']}
        email_data = {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': headers.get('Subject', ''),
            'from_address': headers.get('From', ''),
            'to_address': headers.get('To', ''),
            'received_date': headers.get('Date', ''),
            'content': '',  # TODO: Extract content
            'labels': str(message.get('labelIds', [])),
            'raw_json': str(message)
        }
        
        if hasattr(session, 'merge'):
            # SQLAlchemy session
            email = Email(**email_data)
            session.merge(email)
            session.commit()
        else:
            # SQLite connection
            cursor = session.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO emails (
                    id, thread_id, subject, from_address, to_address,
                    received_date, content, labels, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                email_data['id'],
                email_data['thread_id'],
                email_data['subject'],
                email_data['from_address'],
                email_data['to_address'],
                email_data['received_date'],
                email_data['content'],
                email_data['labels'],
                email_data['raw_json']
            ))
            session.commit()
            
    except Exception as e:
        print(f"Error processing message {msg_id}: {str(e)}")

def get_oldest_email_date(session):
    """Get the date of the oldest email in the database."""
    if hasattr(session, 'query'):
        # SQLAlchemy session
        oldest_email = session.query(Email).order_by(Email.received_date.asc()).first()
        return parser.parse(oldest_email.received_date) if oldest_email else None
    else:
        # SQLite connection
        cursor = session.cursor()
        cursor.execute('SELECT received_date FROM emails ORDER BY received_date ASC LIMIT 1')
        result = cursor.fetchone()
        return parser.parse(result[0]) if result else None

def get_newest_email_date(session):
    """Get the date of the newest email in the database."""
    if hasattr(session, 'query'):
        # SQLAlchemy session
        newest_email = session.query(Email).order_by(Email.received_date.desc()).first()
        return parser.parse(newest_email.received_date) if newest_email else None
    else:
        # SQLite connection
        cursor = session.cursor()
        cursor.execute('SELECT received_date FROM emails ORDER BY received_date DESC LIMIT 1')
        result = cursor.fetchone()
        return parser.parse(result[0]) if result else None

def count_emails(session):
    """Get total number of emails in database."""
    if hasattr(session, 'query'):
        # SQLAlchemy session
        return session.query(Email).count()
    else:
        # SQLite connection
        cursor = session.cursor()
        cursor.execute('SELECT COUNT(*) FROM emails')
        result = cursor.fetchone()
        return result[0] if result else 0

def fetch_older_emails(session, service, label=None):
    """Fetch emails older than the oldest in database."""
    oldest_date = get_oldest_email_date(session)
    if oldest_date:
        return fetch_emails(service, end_date=oldest_date, label=label)
    return []

def fetch_newer_emails(session, service, label=None):
    """Fetch emails newer than the newest in database."""
    newest_date = get_newest_email_date(session)
    if newest_date:
        # Add 1-minute overlap to avoid missing emails
        start_date = newest_date - timedelta(minutes=1)
        return fetch_emails(service, start_date=start_date, label=label)
    return []

def list_labels(service):
    """List all available Gmail labels and store them in the database with history.
    
    Args:
        service: Authenticated Gmail API service instance.
    """
    try:
        # Get all labels
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        # Connect to label database
        session = get_email_session()
        
        # Initialize database if needed
        init_label_database(session)
        
        # Update label history
        current_time = datetime.utcnow()
        
        # Update label history
        for label in labels:
            # Check if label exists
            existing_label = session.query(GmailLabel).filter_by(label_id=label['id']).first()
            if existing_label:
                # Label exists, update last_seen_at
                existing_label.last_seen_at = current_time
                session.commit()
            else:
                # New label, insert it
                new_label = GmailLabel(
                    label_id=label['id'],
                    name=label['name'],
                    type=label.get('type', ''),
                    first_seen_at=current_time,
                    last_seen_at=current_time
                )
                session.add(new_label)
                session.commit()
        
        # Mark labels not seen in this update as deleted
        session.query(GmailLabel).filter(
            GmailLabel.last_seen_at < current_time
        ).update({
            'is_active': False,
            'deleted_at': current_time
        })
        session.commit()
        
        session.close()
        
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
    
    # Get database session
    session = get_email_session()
    
    # Initialize database
    init_database(session)
    
    # Clear database if requested
    if args.clear:
        clear_database(session)
        print("Database cleared")
    
    # Fetch emails based on arguments
    if args.newer:
        messages = fetch_newer_emails(session, service, args.label)
    elif args.older:
        messages = fetch_older_emails(session, service, args.label)
    else:
        # Default: fetch last N days of emails
        end_date = datetime.now(UTC_TZ)
        start_date = end_date - timedelta(days=days_to_fetch)
        messages = fetch_emails(service, start_date, end_date, args.label)
    
    # Process messages
    for msg in messages:
        process_email(service, msg['id'], session)
    
    # Print summary
    total_emails = count_emails(session)
    print(f"\nTotal emails in database: {total_emails}")
    
    session.close()

if __name__ == '__main__':
    main()