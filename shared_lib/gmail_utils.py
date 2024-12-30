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
    
    # Set up the service chain
    users = MagicMock()
    messages = MagicMock()
    labels = MagicMock()
    list_request = MagicMock()
    
    service.users.return_value = users
    users.messages.return_value = messages
    users.labels.return_value = labels
    messages.list.return_value = list_request
    labels.list.return_value = list_request
    
    return service

def setup_mock_messages(service, messages_data):
    """Set up mock messages response.
    
    Args:
        service: Mock Gmail service
        messages_data: List of message dictionaries to return
    """
    service.users().messages().list().execute.return_value = {
        "messages": messages_data
    }

def setup_mock_labels(service, labels_data):
    """Set up mock labels response.
    
    Args:
        service: Mock Gmail service
        labels_data: List of label dictionaries to return
    """
    service.users().labels().list().execute.return_value = {
        "labels": labels_data
    }

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
from typing import Dict, List, Optional
from contextlib import contextmanager
from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from shared_lib.constants import TEST_CONFIG
from shared_lib.gmail_lib import GmailAPI

class TestTransaction:
    """Context manager for Gmail API test transactions.
    
    Manages test data lifecycle:
    1. Creates test labels and messages
    2. Executes test
    3. Cleans up test data
    """
    
    def __init__(self, gmail_service, test_labels: List[str] = None):
        self.service = gmail_service
        self.test_labels = test_labels or ["TEST_LABEL"]
        self.created_labels = []
        self.created_messages = []
        
    def __enter__(self):
        """Set up test environment."""
        try:
            # Create test labels
            for label in self.test_labels:
                label_info = create_test_label(self.service, label)
                self.created_labels.append(label_info)
                
            return self
            
        except Exception as e:
            self.cleanup()
            raise RuntimeError(f"Failed to setup test environment: {str(e)}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up test environment."""
        self.cleanup()
        
    def cleanup(self):
        """Remove all test data."""
        # Delete test messages
        for msg_id in self.created_messages:
            try:
                self.service.users().messages().delete(
                    userId='me',
                    id=msg_id
                ).execute()
            except HttpError:
                pass  # Ignore errors during cleanup
                
        # Delete test labels
        for label in self.created_labels:
            try:
                self.service.users().labels().delete(
                    userId='me',
                    id=label['id']
                ).execute()
            except HttpError:
                pass  # Ignore errors during cleanup
                
    def create_message(self, subject: str = "Test Email", 
                      body: str = "Test Body",
                      sender: str = "test@example.com",
                      label_ids: List[str] = None) -> str:
        """Create a test message with optional labels.
        
        Args:
            subject: Email subject
            body: Email body
            sender: Sender email
            label_ids: List of label IDs to apply
            
        Returns:
            Message ID
        """
        msg = create_test_email(
            self.service,
            subject=subject,
            body=body,
            sender=sender,
            label_ids=label_ids or [label['id'] for label in self.created_labels]
        )
        self.created_messages.append(msg['id'])
        return msg['id']

def create_test_label(service, name: str) -> Dict:
    """Create a test label.
    
    Args:
        service: Gmail API service
        name: Label name
        
    Returns:
        Label info dictionary
    """
    label_object = {
        'name': f"TEST_{name}",
        'messageListVisibility': 'show',
        'labelListVisibility': 'labelShow'
    }
    
    try:
        result = service.users().labels().create(
            userId='me',
            body=label_object
        ).execute()
        return result
    except HttpError as error:
        raise RuntimeError(f"Failed to create test label: {str(error)}")

def create_test_email(service,
                     subject: str = "Test Email",
                     body: str = "Test Body",
                     sender: str = "test@example.com",
                     label_ids: List[str] = None) -> Dict:
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
    message = {
        'raw': f"""From: {sender}
Subject: {subject}
To: me@example.com
Content-Type: text/plain; charset="UTF-8"

{body}"""
    }
    
    try:
        # Create message
        result = service.users().messages().insert(
            userId='me',
            body=message
        ).execute()
        
        # Apply labels if specified
        if label_ids:
            service.users().messages().modify(
                userId='me',
                id=result['id'],
                body={'addLabelIds': label_ids}
            ).execute()
            
        return result
    except HttpError as error:
        raise RuntimeError(f"Failed to create test email: {str(error)}")

@contextmanager
def gmail_test_context(test_labels: List[str] = None):
    """Context manager for Gmail API testing.
    
    Example:
        ```python
        with gmail_test_context(['INBOX', 'SENT']) as ctx:
            msg_id = ctx.create_message(
                subject='Test',
                body='Test message',
                label_ids=[ctx.created_labels[0]['id']]
            )
            # Run tests...
        # Test data is automatically cleaned up
        ```
    """
    api = GmailAPI()
    service = api.get_service()
    
    with TestTransaction(service, test_labels) as transaction:
        yield transaction
