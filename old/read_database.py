import sqlite3
from datetime import datetime

maxResults = 10  # Adjust as needed

def connect_to_database():
    try:
        conn = sqlite3.connect('db_email_store.db')
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
    body_preview = email['body'][:100] + ('...' if len(email['body']) > 100 else '')
    print(f"Body preview: {body_preview}")

def read_emails(conn, limit=maxResults):
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

def count_emails(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM emails')
    return cursor.fetchone()[0]

def get_date_range(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT MIN(date), MAX(date) FROM emails')
    oldest, newest = cursor.fetchone()
    return oldest, newest

def main():
    conn = connect_to_database()
    if not conn:
        return

    total_emails = count_emails(conn)
    oldest_date, newest_date = get_date_range(conn)

    try:
        print("\nReading recent emails from database...")
        emails = read_emails(conn)
        if not emails:
            print("No emails found in database")
            return

        print(f"\nFound {len(emails)} emails:")
        print(f"Total emails in database: {total_emails}")
        print(f"Date range: {oldest_date} to {newest_date}")

        for email in emails:
            display_email_summary(email)

    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        conn.close()
        print("\nDatabase connection closed")

if __name__ == '__main__':
    main()
