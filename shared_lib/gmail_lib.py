"""Gmail API wrapper for Marian."""

import base64
import json
import logging
import os
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional, Union

from dateutil import parser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytz import timezone
from sqlalchemy import Column, DateTime, Integer, String, create_engine, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from shared_lib.constants import (
    DATA_DIR,
    EMAIL_CONFIG,
    ErrorMessages,
    REGEX_PATTERNS,
)
from shared_lib.schema_constants import COLUMN_SIZES
from shared_lib.exceptions import APIError, AuthenticationError
from shared_lib.token_manager import TokenManager
from .api_version_utils import verify_gmail_version, check_api_changelog
from .api_monitor import track_api_call

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

CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "credentials.json")
DEFAULT_LABEL_DB = os.path.join(DATA_DIR, "email_labels.db")

# Timezone
UTC_TZ = timezone("UTC")

logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()

# Association table for many-to-many relationship between labels and emails
email_labels = Table(
    "email_labels",
    Base.metadata,
    Column("email_id", ForeignKey("email_messages.id"), primary_key=True),
    Column("label_id", ForeignKey("gmail_labels.label_id"), primary_key=True),
)


class GmailLabel(Base):
    """SQLAlchemy model for Gmail labels.
    
    Based on Gmail API Label resource:
    https://developers.google.com/gmail/api/reference/rest/v1/users.labels#Label
    """

    __tablename__ = "gmail_labels"
    label_id = Column(String(COLUMN_SIZES["LABEL_ID"]), primary_key=True)
    name = Column(String(COLUMN_SIZES["LABEL_NAME"]), nullable=False)
    type = Column(String(COLUMN_SIZES["LABEL_TYPE"]))
    message_list_visibility = Column(String(COLUMN_SIZES["LABEL_MESSAGE_VISIBILITY"]), nullable=True)
    label_list_visibility = Column(String(COLUMN_SIZES["LABEL_LIST_VISIBILITY"]), nullable=True)
    color = Column(String(COLUMN_SIZES["LABEL_COLOR"]), nullable=True)
    messages_total = Column(Integer, nullable=True)
    messages_unread = Column(Integer, nullable=True)
    threads_total = Column(Integer, nullable=True)
    threads_unread = Column(Integer, nullable=True)
    last_sync = Column(DateTime, default=datetime.utcnow)

    # Relationships
    emails = relationship("EmailMessage", secondary=email_labels, back_populates="labels")

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
            "color": self.color,
            "messages_total": self.messages_total,
            "messages_unread": self.messages_unread,
            "threads_total": self.threads_total,
            "threads_unread": self.threads_unread,
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
            color=gmail_label.get("color"),
            messages_total=gmail_label.get("messagesTotal"),
            messages_unread=gmail_label.get("messagesUnread"),
            threads_total=gmail_label.get("threadsTotal"),
            threads_unread=gmail_label.get("threadsUnread"),
            last_sync=datetime.utcnow(),
        )


class GmailAPI:
    """Main class for Gmail API operations."""

    def __init__(self, label_db_path: str = DEFAULT_LABEL_DB):
        """Initialize Gmail API wrapper.
        
        Args:
            label_db_path: Path to SQLite database for label storage
            
        Raises:
            ValueError: If API version is incompatible
            RuntimeError: If required features are not available
        """
        self.label_db_path = label_db_path
        self.engine = create_engine(f"sqlite:///{label_db_path}")
        self.Session = sessionmaker(bind=self.engine)
        self.service = self._get_gmail_service()
        
        # Verify API version and features
        if error := verify_gmail_version(self.service):
            raise ValueError(f"Gmail API version error: {error}")
            
        # Check for API updates
        if warning := check_api_changelog('gmail'):
            logger.warning(f"Gmail API update: {warning}")

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
            # Try loading existing token
            creds = TokenManager.load_token()
            if creds and creds.valid:
                return creds
                
            # Create new token if none exists or is invalid
            return TokenManager.create_token(SCOPES)
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError(ErrorMessages["API_ERROR"]) from e

    @track_api_call('gmail')
    def get_service(self):
        """Get Gmail service instance."""
        if not self.service:
            self.service = self._get_gmail_service()
        return self.service

    @track_api_call('gmail')
    def list_messages(self, query: str = None, max_results: int = 100) -> List[Dict]:
        """List Gmail messages."""
        results = self.service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        return [{"id": msg["id"], "threadId": msg["threadId"]} for msg in messages]

    @track_api_call('gmail')
    def get_message(self, message_id: str, format: str = 'full') -> Dict:
        """Get a Gmail message by ID."""
        message = self.service.users().messages().get(userId="me", id=message_id, format=format).execute()
        return message

    @track_api_call('gmail')
    def list_labels(self) -> List[Dict]:
        """List all labels in the user's mailbox.
        
        Returns:
            list: List of label dictionaries, or empty list if error
            
        Raises:
            APIError: If Gmail API request fails
        """
        try:
            results = self.service.users().labels().list(userId='me').execute()
            return results.get('labels', [])
        except HttpError as error:
            logger.error(f'Failed to list labels: {error}')
            raise APIError(f'Failed to list labels: {error}')

    def setup_label_database(self):
        """Create and setup the labels database"""
        Base.metadata.create_all(self.engine)
        return self.Session()

    def sync_labels(self):
        """Sync Gmail labels with local database"""
        session = self.Session()

        try:
            # Get all labels from Gmail
            results = self.list_labels()
            labels = [GmailLabel.from_gmail_dict(label) for label in results]

            # Store each label
            for label in labels:
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
            message = self.get_message(msg_id)

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

    def get_oldest_email_date(self) -> Optional[datetime]:
        """Get the date of the oldest email in the database.
        
        Returns:
            datetime: Date of oldest email, or None if no emails
        """
        with self.Session() as session:
            from models.email import EmailMessage
            result = session.query(EmailMessage.date).order_by(EmailMessage.date.asc()).first()
            return result[0] if result else None

    def get_newest_email_date(self) -> Optional[datetime]:
        """Get the date of the newest email in the database.
        
        Returns:
            datetime: Date of newest email, or None if no emails
        """
        with self.Session() as session:
            from models.email import EmailMessage
            result = session.query(EmailMessage.date).order_by(EmailMessage.date.desc()).first()
            return result[0] if result else None

    def count_emails(self) -> int:
        """Get total number of emails in the database.
        
        Returns:
            int: Total number of emails
        """
        with self.Session() as session:
            from models.email import EmailMessage
            return session.query(EmailMessage).count()
