# Get's a credential token for access to Gmail 
# 

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
import json
import pickle

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
]
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'

def authenticate_gmail():
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(f"Credentials file '{CREDENTIALS_FILE}' not found")

        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired token...")
                creds.refresh(Request())
            else:
                print("Starting new authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                
            with open(TOKEN_FILE, 'wb') as token:
                print(f"Saving token to {TOKEN_FILE}")
                pickle.dump(creds, token)

        print("Authentication successful!")
        return creds

    except Exception as e:
        print(f"Authentication error: {str(e)}")
        raise

if __name__ == '__main__':
    authenticate_gmail()