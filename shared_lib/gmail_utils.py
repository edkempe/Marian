"""Gmail API test utilities."""

from unittest.mock import MagicMock

def create_mock_gmail_service():
    """Create a mock Gmail service with common setup.
    
    This sets up a mock Gmail service with the basic chain of calls needed
    for most API operations. The mock is set up but has no return values,
    those should be set by the specific test.
    
    Returns:
        MagicMock: Configured mock Gmail service
    """
    service = MagicMock()
    
    # Set up users().messages() chain
    messages = MagicMock()
    service.users().messages.return_value = messages
    
    # Set up users().labels() chain
    labels = MagicMock()
    service.users().labels.return_value = labels
    
    return service


def setup_mock_messages(service, messages_data):
    """Set up mock messages response with pagination handling.
    
    Args:
        service: Mock Gmail service
        messages_data: List of message dictionaries to return
    """
    list_response = {'messages': messages_data}
    service.users().messages().list().execute.return_value = list_response
    
    # Mock list_next to return None (no more pages)
    service.users().messages().list_next.return_value = None


def setup_mock_labels(service, labels_data):
    """Set up mock labels response.
    
    Args:
        service: Mock Gmail service
        labels_data: List of label dictionaries to return
    """
    list_response = {'labels': labels_data}
    service.users().labels().list().execute.return_value = list_response


def setup_mock_message(service, message_data):
    """Set up mock message get response.
    
    Args:
        service: Mock Gmail service
        message_data: Message data to return
    """
    service.users().messages().get().execute.return_value = message_data


"""Gmail test utilities."""

import json
import os
from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from typing import List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from shared_lib.constants import TESTING_CONFIG
from shared_lib.gmail_lib import GmailAPI


def create_test_label(service, name: str):
    """Create a test label.
    
    Args:
        service: Gmail API service
        name: Label name
        
    Returns:
        Label info dictionary
    """
    try:
        label = {
            'name': name,
            'messageListVisibility': 'show',
            'labelListVisibility': 'labelShow'
        }
        result = service.users().labels().create(
            userId='me',
            body=label
        ).execute()
        return result
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


def create_test_email(service,
                     subject: str = "Test Email",
                     body: str = "Test Body",
                     sender: str = "test@example.com",
                     label_ids: List[str] = None):
    """Create a test email message.
    
    Args:
        service: Gmail API service
        subject: Email subject
        body: Email body
        sender: Sender email
        label_ids: List of label IDs to apply
        
    Returns:
        Message info dictionary
    """
    # Create message
    message = MIMEText(body)
    message['to'] = "me"
    message['from'] = sender
    message['subject'] = subject
    
    # Encode message
    raw = urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    
    try:
        # Create message
        message = service.users().messages().insert(
            userId='me',
            body=body
        ).execute()
        
        # Apply labels if specified
        if label_ids:
            modify_body = {'addLabelIds': label_ids}
            message = service.users().messages().modify(
                userId='me',
                id=message['id'],
                body=modify_body
            ).execute()
        
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None
