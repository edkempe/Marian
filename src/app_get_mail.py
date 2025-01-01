"""Gmail email fetching and storage module.

This module provides functionality to:
1. Fetch emails from Gmail API
2. Store emails in a local database
3. Track email labels and their history

Requirements:
- google-api-python-client: For Gmail API access
- python-dateutil: For robust date parsing
- pytz: For timezone handling
- sqlalchemy: For database operations

Usage:
python get_mail.py [--newer] [--older] [--clear] [--label] [--list-labels]
"""

import argparse
import json
import logging
import os
import sys
import time
from base64 import urlsafe_b64decode
from datetime import datetime, timedelta, timezone

import pytz
from dateutil import parser
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import Base
from models.db_init import init_db
from models.email import EmailMessage
from models.gmail_label import GmailLabel
from shared_lib.constants import DATABASE_CONFIG, EMAIL_CONFIG
from shared_lib.database_session_util import (
    get_analysis_session,
    get_email_session,
)
from shared_lib.gmail_lib import GmailAPI

# Configuration
UTC_TZ = pytz.UTC


def init_database(session: Session) -> Session:
    """Initialize the email database schema.

    Args:
        session: SQLAlchemy session to use for database operations

    Returns:
        Session: The initialized database session
    """
    if not hasattr(session, "bind") or session.bind is None:
        engine = create_engine(DATABASE_CONFIG["email"]["url"])
        session.configure(bind=engine)
        Base.metadata.create_all(engine)
    return session


def init_label_database(session: Session) -> Session:
    """Initialize the label database schema.

    Args:
        session: SQLAlchemy session to use for database operations

    Returns:
        Session: The initialized database session
    """
    if not hasattr(session, "bind") or session.bind is None:
        engine = create_engine(DATABASE_CONFIG["EMAIL_DB_URL"])
        session.bind = engine
    Base.metadata.create_all(session.bind)
    return session


def get_gmail_service():
    """Get an authenticated Gmail service."""
    return GmailAPI().service


def clear_database(session: Session) -> None:
    """Clear all data from the email database.

    Args:
        session: SQLAlchemy session to use for database operations
    """
    session.query(EmailMessage).delete()
    session.commit()


def get_label_id(service, label_name):
    """Get the ID of a label by its name.

    Args:
        service: Gmail API service instance
        label_name: Name of the label to find

    Returns:
        str: Label ID if found, None otherwise
    """
    if not label_name:
        return None

    try:
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        for label in labels:
            if label.get("name") == label_name:
                return label["id"]
        return None
    except Exception as error:
        print(f"Failed to get label ID: {error}")
        return None


def fetch_emails(service, start_date=None, end_date=None, label=None, max_results=None):
    """Fetch emails from Gmail API.

    Args:
        service: Gmail API service instance
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        label: Optional label to filter by
        max_results: Maximum number of results to return

    Returns:
        List of email messages
    """
    try:
        query = []
        if start_date:
            query.append(f'after:{start_date.strftime("%Y/%m/%d")}')
        if end_date:
            query.append(f'before:{end_date.strftime("%Y/%m/%d")}')

        # Get label ID if label name provided
        label_id = None
        if label:
            label_id = get_label_id(service, label)
            if not label_id:
                print(f'Label "{label}" not found')
                return []

        # Build the request
        request_params = {
            "userId": "me",
            "q": " ".join(query) if query else "",
            "maxResults": min(max_results, 500) if max_results else 500,
        }

        if label_id:
            request_params["labelIds"] = [label_id]

        request = service.users().messages().list(**request_params)

        messages = []
        while request:
            response = request.execute()
            if "messages" in response:
                messages.extend(response["messages"])

                # Stop if we've reached max_results
                if max_results and len(messages) >= max_results:
                    messages = messages[:max_results]
                    break

            # Get next page of results
            request = (
                service.users()
                .messages()
                .list_next(previous_request=request, previous_response=response)
            )

        return messages
    except Exception as error:
        print(f"An error occurred: {error}")
        return []


def get_message_body(message):
    """Extract email body from message payload.
    
    Args:
        message: Gmail API message object
        
    Returns:
        str: Email body text
    """
    if not message.get("payload"):
        return ""
        
    def get_text_parts(part, text_parts=None):
        if text_parts is None:
            text_parts = []
            
        if part.get("mimeType", "").startswith("text/plain"):
            if "data" in part.get("body", {}):
                text = urlsafe_b64decode(part["body"]["data"]).decode()
                text_parts.append(text)
        
        for subpart in part.get("parts", []):
            get_text_parts(subpart, text_parts)
            
        return text_parts
        
    text_parts = get_text_parts(message["payload"])
    return "\n".join(text_parts)


def parse_email_date(date_str):
    """Parse email date with error handling.
    
    Args:
        date_str: Date string from email header
        
    Returns:
        datetime: Parsed date or current UTC time if parsing fails
    """
    try:
        return parser.parse(date_str)
    except (ValueError, TypeError) as e:
        logging.warning(f"Failed to parse date '{date_str}': {e}")
        return datetime.now(timezone.utc)


def process_email(service, msg_id, session):
    """Process a single email message and store it in the database.

    Args:
        service: Gmail API service instance
        msg_id: ID of the message to process
        session: SQLAlchemy session to use for database operations
        
    Raises:
        ValueError: If msg_id is invalid
        RuntimeError: If email processing fails
    """
    try:
        # Get the email message
        message = (
            service.users()
            .messages()
            .get(userId=EMAIL_CONFIG["USER_ID"], id=msg_id, format="full")
            .execute()
        )

        # Create case-insensitive header lookup while preserving original values
        headers_lookup = {}
        for header in message["payload"]["headers"]:
            headers_lookup[header["name"].lower()] = header["value"]

        # Get email data
        email_data = {
            "id": message["id"],
            "threadId": message["threadId"],
            "subject": headers_lookup.get("subject", EMAIL_CONFIG["DEFAULT_SUBJECT"]),
            "from_": headers_lookup.get("from", EMAIL_CONFIG["EMPTY_STRING"]),
            "to": headers_lookup.get("to", EMAIL_CONFIG["EMPTY_STRING"]),
            "cc": headers_lookup.get("cc", EMAIL_CONFIG["EMPTY_STRING"]),
            "bcc": headers_lookup.get("bcc", EMAIL_CONFIG["EMPTY_STRING"]),
            "date": parse_email_date(headers_lookup.get("date")),
            "body": get_message_body(message),
            "labelIds": ",".join(message.get("labelIds", [])),
            "has_attachments": bool(message.get("payload", {}).get("parts", [])),
            "full_api_response": json.dumps(message),
        }

        # Validate required fields
        if not email_data["id"]:
            raise ValueError("Email ID is required")

        email = EmailMessage(**email_data)
        session.merge(email)
        session.commit()

        logging.info(
            f"Processed email {msg_id}: subject='{email_data['subject']}' from='{email_data['from_']}'"
        )

    except Exception as e:
        logging.error(f"Failed to process email {msg_id}: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to process email {msg_id}: {str(e)}") from e


def get_oldest_email_date(session):
    """Get the date of the oldest email in the database."""
    oldest_email = session.query(EmailMessage).order_by(EmailMessage.received_date.asc()).first()
    return parser.parse(oldest_email.received_date) if oldest_email else None


def get_newest_email_date(session):
    """Get the date of the newest email in the database."""
    newest_email = session.query(EmailMessage).order_by(EmailMessage.received_date.desc()).first()
    return parser.parse(newest_email.received_date) if newest_email else None


def count_emails(session):
    """Get total number of emails in database."""
    return session.query(EmailMessage).count()


def fetch_older_emails(session, service, label=None):
    """Fetch emails older than the oldest in database."""
    oldest_date = get_oldest_email_date(session)
    if oldest_date:
        return fetch_emails(service, end_date=oldest_date, label=label)
    return []


def fetch_newer_emails(session, service, label=None):
    """Fetch emails newer than the newest in database."""
    newest_date = get_newest_email_date(session)
    if newest_date:
        # Add 1-minute overlap to avoid missing emails
        start_date = newest_date - timedelta(minutes=1)
        return fetch_emails(service, start_date=start_date, label=label)
    return []


def list_labels(service):
    """List all available Gmail labels.

    Args:
        service: Authenticated Gmail API service instance

    Returns:
        list: List of label dictionaries with 'id' and 'name' keys
    """
    try:
        results = service.users().labels().list(userId="me").execute()
        return results.get("labels", [])
    except Exception as error:
        print(f"Failed to list labels: {error}")
        return []


def main():
    """Main function to fetch emails."""
    parser = argparse.ArgumentParser(description="Fetch emails from Gmail")
    parser.add_argument(
        "--newer",
        action="store_true",
        help="Fetch emails newer than most recent in database",
    )
    parser.add_argument(
        "--older",
        action="store_true",
        help="Fetch emails older than oldest in database",
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear database before fetching"
    )
    parser.add_argument("--label", help="Filter emails by label")
    parser.add_argument(
        "--list-labels", action="store_true", help="List all available labels"
    )
    parser.add_argument(
        "--max-results", type=int, help="Maximum number of results to return"
    )
    args = parser.parse_args()

    # Get Gmail service
    service = get_gmail_service()
    if not service:
        print("Failed to get Gmail service")
        return

    # List labels if requested
    if args.list_labels:
        labels = list_labels(service)
        print("\nAvailable labels:")
        for label in labels:
            print(f"- {label['name']} ({label['id']})")
        return

    # Get database session
    with get_email_session() as session:
        # Initialize database
        init_db(session)

        # Clear database if requested
        if args.clear:
            clear_database(session)
            print("Database cleared")

        # Fetch emails based on arguments
        if args.newer:
            messages = fetch_newer_emails(session, service, args.label)
        elif args.older:
            messages = fetch_older_emails(session, service, args.label)
        else:
            # Default: fetch last N days of emails
            end_date = datetime.now(UTC_TZ)
            start_date = end_date - timedelta(days=EMAIL_CONFIG["DAYS_TO_FETCH"])
            messages = fetch_emails(
                service, start_date, end_date, args.label, args.max_results
            )

        # Process messages
        for msg in messages:
            process_email(service, msg["id"], session)

        # Print summary
        total_emails = count_emails(session)
        print(f"\nTotal emails in database: {total_emails}")


if __name__ == "__main__":
    main()
