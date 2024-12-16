# Print emails from database
# 

import sqlite3
from datetime import datetime
import json

def connect_to_database():
    try:
        conn = sqlite3.connect('email_store.db')
        print("Successfully connected to database")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def display_email_summary(email):
    print("\n" + "="*50)
    print(f"Subject: {email['subject']}")
    print(f"From: {email['sender']}")
    print(f"Date: {email['date']}")
    print(f"Labels: {email['labels']}")
    print("-"*50)
    # Show first 100 characters of body with ellipsis if truncated
    body_preview = email['body'][:100] + ('...' if len(email['body']) > 100 else '')
    print(f"Body preview: {body_preview}")

def read_emails(conn, limit=10):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, subject, sender, date, body, labels, raw_data 
            FROM emails 
            ORDER BY date DESC 
            LIMIT ?''', (limit,))
        
        emails = []
        for row in cursor.fetchall():
            email = {
                'id': row[0],
                'subject': row[1],
                'sender': row[2],
                'date': row[3],
                'body': row[4],
                'labels': row[5],
                'raw_data': row[6]
            }
            emails.append(email)
        
        return emails
    except Exception as e:
        print(f"Error reading emails: {e}")
        return []

def main():
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        print("\nReading recent emails from database...")
        emails = read_emails(conn)
        
        if not emails:
            print("No emails found in database")
            return
        
        print(f"\nFound {len(emails)} emails:")
        for email in emails:
            display_email_summary(email)
            
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        conn.close()
        print("\nDatabase connection closed")

if __name__ == '__main__':
    main()