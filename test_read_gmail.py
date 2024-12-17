#  uses token.json rather than token.pickle
# 

import os.path
import sys
import os

# Add the local library folder to sys.path
sys.path.append(os.path.abspath("./lib"))

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def read_email(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        
        payload = message['payload']
        headers = payload['headers']
        
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        sender = next(header['value'] for header in headers if header['name'] == 'From')
        
        parts = payload.get('parts', [])
        body = ''
        
        if 'body' in payload:
            body = payload['body'].get('data', '')
        elif parts:
            part = parts[0]
            body = part['body'].get('data', '')
        
        if body:
            body = base64.urlsafe_b64decode(body).decode('utf-8')
        
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        
    except HttpError as error:
        print(f'An error occurred: {error}')

def main():
    creds = get_credentials()
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Get the most recent email
        results = service.users().messages().list(userId='me', maxResults=1).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print('No messages found.')
            return
        
        msg_id = messages[0]['id']
        read_email(service, 'me', msg_id)
        
    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()