"""Utilities for email testing."""

from base64 import urlsafe_b64encode
from datetime import datetime, timezone
from typing import Dict, List, Optional

from models.email import EmailMessage
from tests.utils.test_constants import TEST_EMAIL

def create_test_email(
    id: str = TEST_EMAIL["id"],
    thread_id: str = TEST_EMAIL["thread_id"],
    subject: str = TEST_EMAIL["subject"],
    from_: str = TEST_EMAIL["from_"],
    to: str = TEST_EMAIL["to"],
    body: str = TEST_EMAIL["body"],
    date: datetime = None,
    label_ids: str = "",
    has_attachments: bool = False,
    api_response: str = "",
) -> EmailMessage:
    """Create a test EmailMessage model instance.
    
    Args:
        id: Email ID
        thread_id: Thread ID
        subject: Email subject
        from_: Sender email
        to: Recipient email
        body: Email body content
        date: Email date (defaults to current UTC time)
        label_ids: Comma-separated list of label IDs
        has_attachments: Whether email has attachments
        api_response: Full Gmail API response JSON
        
    Returns:
        EmailMessage model instance
    """
    if date is None:
        date = datetime.now(timezone.utc)
        
    return EmailMessage(
        id=id,
        thread_id=thread_id,
        subject=subject,
        from_=from_,
        to=to,
        body=body,
        date=date,
        label_ids=label_ids,
        has_attachments=has_attachments,
        full_api_response=api_response,
    )

def create_test_message(
    msg_id: str,
    subject: str = "Test Subject",
    from_addr: str = "test@example.com",
    to_addr: str = "recipient@example.com",
    body_text: Optional[str] = None,
    body_html: Optional[str] = None,
    attachments: Optional[List[Dict]] = None,
    label_ids: Optional[List[str]] = None,
) -> Dict:
    """Create a test Gmail API message.
    
    Args:
        msg_id: Message ID
        subject: Email subject
        from_addr: Sender email
        to_addr: Recipient email
        body_text: Plain text body content
        body_html: HTML body content
        attachments: List of attachment metadata
        label_ids: List of Gmail label IDs
        
    Returns:
        Dict representing a Gmail API message
    """
    headers = [
        {"name": "Subject", "value": subject},
        {"name": "From", "value": from_addr},
        {"name": "To", "value": to_addr},
    ]
    
    parts = []
    if body_text:
        parts.append({
            "mimeType": "text/plain",
            "body": {"data": urlsafe_b64encode(body_text.encode()).decode()}
        })
    if body_html:
        parts.append({
            "mimeType": "text/html",
            "body": {"data": urlsafe_b64encode(body_html.encode()).decode()}
        })
    if attachments:
        parts.extend(attachments)
        
    message = {
        "id": msg_id,
        "threadId": f"thread_{msg_id}",
        "labelIds": label_ids or [],
        "payload": {
            "headers": headers,
            "mimeType": "multipart/alternative" if len(parts) > 1 else parts[0]["mimeType"],
            "parts": parts if len(parts) > 1 else None,
            "body": None if len(parts) > 1 else parts[0]["body"],
        }
    }
    
    return message
