"""Gmail API wrapper for Marian."""

import base64
import json
import logging
import os
import pickle
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional, Union

from dateutil import parser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytz import timezone
from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from shared_lib.constants import (
    COLUMN_SIZES,
    DATA_DIR,
    EMAIL_CONFIG,
    ErrorMessages,
    REGEX_PATTERNS,
)
from shared_lib.exceptions import APIError, AuthenticationError

# Constants
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.labels",
]

# File paths
CONFIG_DIR = os.path.join(os.path.dirname(DATA_DIR), "config")
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

TOKEN_FILE = os.path.join(CONFIG_DIR, "token.pickle")
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "credentials.json")
DEFAULT_LABEL_DB = os.path.join(DATA_DIR, "email_labels.db")

# Timezone
UTC_TZ = timezone("UTC")

logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()


class GmailLabel(Base):
    """SQLAlchemy model for Gmail labels"""

    __tablename__ = "gmail_labels"
    label_id = Column(String(COLUMN_SIZES["EMAIL_LABELS"]), primary_key=True)
    name = Column(String(COLUMN_SIZES["EMAIL_LABELS"]), nullable=False)
    type = Column(String(COLUMN_SIZES["EMAIL_LABELS"]))
    message_list_visibility = Column(String(COLUMN_SIZES["EMAIL_LABELS"]))
    label_list_visibility = Column(String(COLUMN_SIZES["EMAIL_LABELS"]))
    last_sync = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of label."""
        return f"<GmailLabel {self.name}>"

    def to_dict(self) -> Dict[str, Union[str, datetime]]:
        """Convert label to dictionary format."""
        return {
            "label_id": self.label_id,
            "name": self.name,
            "type": self.type,
            "message_list_visibility": self.message_list_visibility,
            "label_list_visibility": self.label_list_visibility,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
        }

    @classmethod
    def from_gmail_dict(cls, gmail_label: Dict) -> "GmailLabel":
        """Create label from Gmail API response."""
        return cls(
            label_id=gmail_label["id"],
            name=gmail_label["name"],
            type=gmail_label.get("type"),
            message_list_visibility=gmail_label.get("messageListVisibility"),
            label_list_visibility=gmail_label.get("labelListVisibility"),
            last_sync=datetime.utcnow(),
        )


class GmailAPI:
    """Main class for Gmail API operations."""

    def __init__(self, label_db_path: str = DEFAULT_LABEL_DB):
        """Initialize Gmail API wrapper.
        
        Args:
            label_db_path: Path to SQLite database for label storage
        """
        self.label_db_path = label_db_path
        self.engine = create_engine(f"sqlite:///{label_db_path}")
        self.Session = sessionmaker(bind=self.engine)
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """Get authenticated Gmail API service instance."""
        creds = self._authenticate_gmail()
        return build("gmail", "v1", credentials=creds)

    def _authenticate_gmail(self) -> Credentials:
        """Authenticate with Gmail API.
        
        Returns:
            Google OAuth2 credentials
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Credentials file '{CREDENTIALS_FILE}' not found"
                )

            creds = None
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "rb") as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired token...")
                    creds.refresh(Request())
                else:
                    logger.info("Starting new authentication flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                with open(TOKEN_FILE, "wb") as token:
                    logger.info(f"Saving token to {TOKEN_FILE}")
                    pickle.dump(creds, token)

            return creds

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError(ErrorMessages["API_ERROR"]) from e

    def setup_label_database(self):
        """Create and setup the labels database"""
        Base.metadata.create_all(self.engine)
        return self.Session()

    def sync_labels(self):
        """Sync Gmail labels with local database"""
        session = self.Session()

        try:
            # Get all labels from Gmail
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            # Store each label
            for label_data in labels:
                label = GmailLabel.from_gmail_dict(label_data)
                session.merge(label)

            session.commit()
            print(f"Successfully synced {len(labels)} labels")
            return True

        except Exception as e:
            session.rollback()
            print(f"Error syncing labels: {str(e)}")
            return False

        finally:
            session.close()

    def get_label_name(self, label_id):
        """Get label name from label ID"""
        session = self.Session()

        try:
            label = session.query(GmailLabel).filter_by(label_id=label_id).first()
            return label.name if label else label_id

        finally:
            session.close()

    def get_label_id(self, label_name):
        """Get label ID from label name"""
        session = self.Session()

        try:
            label = session.query(GmailLabel).filter_by(name=label_name).first()
            return label.label_id if label else None

        finally:
            session.close()

    def process_email(self, msg_id):
        """Process a single email message.

        Args:
            msg_id: Gmail message ID (string)

        Returns:
            Dict containing email data or None if processing fails

        Raises:
            ValueError: If msg_id is not a string or is empty
            RuntimeError: If Gmail API response is missing required fields
        """
        if not isinstance(msg_id, str) or not msg_id.strip():
            raise ValueError("Message ID must be a non-empty string")

        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )

            # Validate required fields
            if "id" not in message:
                raise RuntimeError("Gmail API response missing 'id' field")
            if "threadId" not in message:
                raise RuntimeError("Gmail API response missing 'threadId' field")
            if "payload" not in message:
                raise RuntimeError("Gmail API response missing 'payload' field")

            payload = message["payload"]
            headers = payload.get("headers", [])

            # Extract header fields
            subject = next(
                (h["value"] for h in headers if h["name"].lower() == "subject"),
                "No Subject",
            )
            date = next(
                (h["value"] for h in headers if h["name"].lower() == "date"), None
            )
            from_email = next(
                (h["value"] for h in headers if h["name"].lower() == "from"), None
            )

            # Get body content
            body = ""
            if "parts" in payload:
                for part in payload["parts"]:
                    if part["mimeType"] == "text/plain":
                        if "body" in part and "data" in part["body"]:
                            try:
                                body = base64.urlsafe_b64decode(
                                    part["body"]["data"]
                                ).decode()
                                break
                            except Exception as e:
                                logger.error(f"Error decoding email body: {str(e)}")
            elif "body" in payload and "data" in payload["body"]:
                try:
                    body = base64.urlsafe_b64decode(payload["body"]["data"]).decode()
                except Exception as e:
                    logger.error(f"Error decoding email body: {str(e)}")

            return {
                "id": message["id"],
                "threadId": message["threadId"],
                "subject": subject,
                "date": date,
                "sender": from_email,
                "body": body,
                "labels": [
                    self.get_label_name(label_id)
                    for label_id in message.get("labelIds", [])
                ],
                "full_api_response": json.dumps(message),
            }

        except HttpError as e:
            if e.resp.status == 404:
                logger.error(f"Message {msg_id} not found in Gmail")
            else:
                logger.error(f"Gmail API error for message {msg_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing message {msg_id}: {str(e)}")
            return None

    def send_email(self, to, subject, body, reply_to=None):
        """Send an email"""
        try:
            message = MIMEMultipart()
            message["to"] = to
            message["subject"] = subject

            if reply_to:
                message.add_header("In-Reply-To", reply_to)
                message.add_header("References", reply_to)

            msg = MIMEText(body)
            message.attach(msg)

            raw = base64.urlsafe_b64encode(message.as_bytes())
            raw = raw.decode()

            self.service.users().messages().send(
                userId="me", body={"raw": raw}
            ).execute()

            return True

        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
