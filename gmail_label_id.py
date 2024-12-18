#!/usr/bin/env python3

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import sqlite3
import pickle

def get_gmail_service():
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    return build('gmail', 'v1', credentials=creds)

def setup_label_database(db_path='email_labels.db'):
    """Create and setup the labels database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create labels table if it doesn't exist
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

def sync_gmail_labels(db_path='email_labels.db'):
    """Sync Gmail labels with local database"""
    service = get_gmail_service()
    conn = setup_label_database(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all labels from Gmail
        results = service.users().labels().list(userId='me').execute()
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
                label.get('type', 'user'),
                label.get('messageListVisibility', 'show'),
                label.get('labelListVisibility', 'labelShow')
            ))
        
        # Commit transaction
        conn.commit()
        print(f"Successfully synced {len(labels)} labels")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f'Error syncing labels: {e}')
        return False
    finally:
        conn.close()

def get_label_name(label_id, db_path='email_labels.db'):
    """Get label name from label ID"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT name FROM gmail_labels WHERE label_id = ?', (label_id,))
        result = cursor.fetchone()
        return result[0] if result else label_id
    except Exception as e:
        print(f'Error getting label name: {e}')
        return label_id
    finally:
        conn.close()

def get_label_id(label_name, db_path='email_labels.db'):
    """Get label ID from label name"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT label_id FROM gmail_labels WHERE name = ?', (label_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
            
        # If not found in database, try Gmail API
        service = get_gmail_service()
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        for label in labels:
            if label['name'].lower() == label_name.lower():
                return label['id']
        
        print(f"Label '{label_name}' not found")
        return None
    except Exception as e:
        print(f'Error getting label ID: {e}')
        return None
    finally:
        conn.close()

def main():
    # Sync labels first
    if sync_gmail_labels():
        print("\nLabel sync completed successfully")
    else:
        print("\nLabel sync failed")

if __name__ == '__main__':
    main()