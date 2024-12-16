# Gives a Gmail label ID from the label name 
# 
 
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import sqlite3
import pickle

def get_gmail_service():
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    return build('gmail', 'v1', credentials=creds)

def get_label_id(label_name):
    service = get_gmail_service()
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        for label in labels:
            if label['name'].lower() == label_name.lower():
                print(f"Found label: {label['name']} with ID: {label['id']}")
                return label['id']
        
        print(f"Label '{label_name}' not found")
        return None
    except Exception as e:
        print(f'Error getting label ID: {e}')
        return None

def main():
    label_name = "Books"  # The label name you want to search for
    label_id = get_label_id(label_name)
    
    if label_id:
        print(f"\nUse this label ID in your get_mail.py script: {label_id}")

if __name__ == '__main__':
    main()