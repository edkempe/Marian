"""Gmail test utilities."""

from contextlib import contextmanager
from typing import List, Optional, Dict, Any
import pytest
import os
import logging
from datetime import datetime, timedelta

from shared_lib.gmail_lib import GmailAPI
from shared_lib.gmail_test_utils import create_test_label, create_test_email
from shared_lib.constants import TEST_TIMEOUT


logger = logging.getLogger(__name__)


class GmailTestTransaction:
    """Context manager for Gmail API test transactions.
    
    Manages test data lifecycle:
    1. Creates test labels and messages
    2. Executes test
    3. Cleans up test data
    """
    
    def __init__(self, gmail_api: GmailAPI, test_labels: List[str] = None):
        """Initialize test transaction.
        
        Args:
            gmail_api: Gmail API client
            test_labels: List of test label names to create
        """
        self.api = gmail_api
        self.service = gmail_api.service
        self.test_labels = test_labels or ["TEST_LABEL"]
        self.created_labels: List[Dict[str, Any]] = []
        self.created_messages: List[Dict[str, Any]] = []
        self.start_time = datetime.utcnow()
    
    def create_message(
        self,
        subject: str = "Test Subject",
        body: str = "Test Body",
        label_ids: List[str] = None,
        from_address: str = None,
        to_addresses: List[str] = None,
    ) -> Dict[str, Any]:
        """Create a test message.
        
        Args:
            subject: Message subject
            body: Message body
            label_ids: List of label IDs to apply
            from_address: Sender email address
            to_addresses: List of recipient email addresses
        
        Returns:
            Created message object
        """
        message = create_test_email(
            self.service,
            subject=subject,
            body=body,
            label_ids=label_ids,
            from_address=from_address,
            to_addresses=to_addresses
        )
        self.created_messages.append(message)
        return message
    
    def __enter__(self) -> "GmailTestTransaction":
        """Set up test environment.
        
        Returns:
            Self for use in with statement
        """
        try:
            # Create test labels
            for label_name in self.test_labels:
                label = create_test_label(self.service, label_name)
                if label:
                    self.created_labels.append(label)
                else:
                    logger.warning(f"Failed to create test label: {label_name}")
            
            return self
        except Exception as e:
            logger.error(f"Error setting up test environment: {e}")
            self.__exit__(type(e), e, e.__traceback__)
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up test environment."""
        cleanup_timeout = self.start_time + timedelta(seconds=TEST_TIMEOUT)
        
        try:
            # Delete test messages
            for msg in self.created_messages:
                try:
                    if datetime.utcnow() > cleanup_timeout:
                        logger.warning("Cleanup timeout reached, stopping message cleanup")
                        break
                    
                    self.api.service.users().messages().delete(
                        userId='me',
                        id=msg['id']
                    ).execute()
                except Exception as e:
                    logger.warning(f"Failed to delete test message {msg['id']}: {e}")
            
            # Delete test labels
            for label in self.created_labels:
                try:
                    if datetime.utcnow() > cleanup_timeout:
                        logger.warning("Cleanup timeout reached, stopping label cleanup")
                        break
                    
                    self.api.service.users().labels().delete(
                        userId='me',
                        id=label['id']
                    ).execute()
                except Exception as e:
                    logger.warning(f"Failed to delete test label {label['id']}: {e}")
        except Exception as e:
            logger.error(f"Error during test cleanup: {e}")
            if not exc_type:  # Only raise if there wasn't already an exception
                raise


@contextmanager
def gmail_test_context(gmail_api: GmailAPI, test_labels: List[str] = None):
    """Context manager for Gmail API testing.
    
    Example:
        ```python
        with gmail_test_context(gmail_api, ['INBOX', 'SENT']) as ctx:
            msg_id = ctx.create_message(
                subject='Test',
                body='Test message',
                label_ids=[ctx.created_labels[0]['id']]
            )
            # Run tests...
        # Test data is automatically cleaned up
        ```
    
    Args:
        gmail_api: Gmail API client
        test_labels: List of test label names to create
    
    Yields:
        GmailTestTransaction instance
    """
    transaction = GmailTestTransaction(gmail_api, test_labels)
    try:
        with transaction as ctx:
            yield ctx
    except Exception as e:
        logger.error(f"Error in gmail_test_context: {e}")
        raise
