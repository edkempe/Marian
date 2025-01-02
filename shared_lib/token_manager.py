"""Token manager for handling OAuth2 tokens."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from shared_lib.constants import CONFIG

class TokenManager:
    """Manages OAuth2 tokens for Gmail API."""

    def __init__(self, token_path: str = "data/tokens/gmail_token.json",
                 credentials_path: str = "data/credentials/gmail_credentials.json"):
        """Initialize token manager.
        
        Args:
            token_path: Path to token file
            credentials_path: Path to credentials file
        """
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
        ]
        self._ensure_paths()

    def _ensure_paths(self) -> None:
        """Ensure token and credentials directories exist."""
        Path(os.path.dirname(self.token_path)).mkdir(parents=True, exist_ok=True)
        Path(os.path.dirname(self.credentials_path)).mkdir(parents=True, exist_ok=True)

    def get_credentials(self) -> Optional[Credentials]:
        """Get valid credentials.
        
        Returns:
            Credentials object if valid credentials exist, None otherwise
        """
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found at {self.credentials_path}"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        return creds

    def is_token_valid(self) -> bool:
        """Check if token is valid.
        
        Returns:
            True if token exists and is valid, False otherwise
        """
        if not os.path.exists(self.token_path):
            return False

        try:
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
            return creds.valid and not creds.expired
        except Exception:
            return False

    def refresh_token(self) -> None:
        """Refresh the token if expired."""
        if not self.is_token_valid():
            self.get_credentials()

    def clear_token(self) -> None:
        """Clear the stored token."""
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
