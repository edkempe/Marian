#!/usr/bin/env python3

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from gmail_label_id import get_gmail_service, get_label_name
from email.mime.text import MIMEText
import base64
import pickle
import json
from datetime import datetime

def get_emails(service, query='from:me', max_results=200):
    """Fetch emails from Gmail based on query"""
    try:
        # Get the list of messages
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print('No messages found.')
            return []
            
        print(f'Found {len(messages)} messages.')
        
        # Get detailed information for each message
        detailed_messages = []
        for message in messages:
            msg = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            detailed_messages.append(msg)
            
        return detailed_messages
            
    except Exception as e:
        print(f'An error occurred: {e}')
        return []

def parse_email(message):
    """Parse relevant information from email message"""
    headers = message['payload']['headers']
    
    # Extract header fields
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
    date = next((h['value'] for h in headers if h['name'].lower() == 'date'), None)
    from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), None)
    
    # Get labels
    labels = [get_label_name(label_id) for label_id in message.get('labelIds', [])]
    
    # Get snippet
    snippet = message.get('snippet', '')
    
    return {
        'id': message['id'],
        'thread_id': message['threadId'],
        'subject': subject,
        'date': date,
        'from': from_email,
        'labels': labels,
        'snippet': snippet
    }

def save_processed_emails(emails, output_file='processed_emails.json'):
    """Save processed emails to a JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(emails, f, indent=2, ensure_ascii=False)
    print(f'Saved {len(emails)} processed emails to {output_file}')

def main():
    try:
        # Get Gmail service
        service = get_gmail_service()
        
        # Fetch emails
        print('Fetching emails...')
        messages = get_emails(service)
        
        if not messages:
            return
            
        # Process each email
        print('Processing emails...')
        processed_emails = [parse_email(msg) for msg in messages]
        
        # Save results
        save_processed_emails(processed_emails)
        
        # Print summary
        print('\nEmail Processing Summary:')
        print(f'Total emails processed: {len(processed_emails)}')
        
        # Count unique labels
        all_labels = set()
        for email in processed_emails:
            all_labels.update(email['labels'])
        print(f'Unique labels found: {len(all_labels)}')
        print('Labels:', ', '.join(sorted(all_labels)))
        
    except Exception as e:
        print(f'An error occurred in main: {e}')

if __name__ == '__main__':
    main()
