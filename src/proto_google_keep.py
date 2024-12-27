from __future__ import print_function
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle

# Update scopes to include both Drive and Keep access
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/keep.readonly'
]

def get_credentials():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def test_google_drive_notes():
    try:
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)

        # Search for Google Keep notes in Drive
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.keep-note'",
            pageSize=10,
            fields="nextPageToken, files(id, name, createdTime, modifiedTime)"
        ).execute()
        items = results.get('files', [])

        if not items:
            print('No Keep notes found.')
            return

        print("\nFound {0} Keep notes:".format(len(items)))
        print("-" * 50)
        
        for item in items:
            print("Title: {0}".format(item['name']))
            print("ID: {0}".format(item['id']))
            print("Created: {0}".format(item['createdTime']))
            print("Modified: {0}".format(item['modifiedTime']))
            print("-" * 50)

    except Exception as e:
        print("Error occurred: {0}".format(str(e)))

if __name__ == "__main__":
    test_google_drive_notes()
