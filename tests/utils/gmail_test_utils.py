"""Gmail test utilities."""

from typing import List, Optional
from contextlib import contextmanager

from shared_lib.gmail_lib import GmailAPI
from shared_lib.gmail_utils import create_test_label, create_test_email


class GmailTestTransaction:
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
        # Create test labels
        for label_name in self.test_labels:
            label = create_test_label(self.service, label_name)
            self.created_labels.append(label)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up test data
        api = GmailAPI()
        
        # Delete test messages
        for msg in self.created_messages:
            try:
                api.service.users().messages().delete(
                    userId='me',
                    id=msg['id']
                ).execute()
            except Exception:
                pass
        
        # Delete test labels
        for label in self.created_labels:
            try:
                api.service.users().labels().delete(
                    userId='me',
                    id=label['id']
                ).execute()
            except Exception:
                pass
    
    def create_message(self, subject: str = "Test Email",
                      body: str = "Test Body",
                      sender: str = "test@example.com",
                      label_ids: Optional[List[str]] = None) -> str:
        """Create a test message.
        
        Args:
            subject: Email subject
            body: Email body
            sender: Sender email
            label_ids: List of label IDs to apply
            
        Returns:
            Message ID
        """
        if label_ids is None and self.created_labels:
            label_ids = [self.created_labels[0]['id']]
            
        msg = create_test_email(
            self.service,
            subject=subject,
            body=body,
            sender=sender,
            label_ids=label_ids
        )
        self.created_messages.append(msg)
        return msg['id']


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
    with GmailTestTransaction(api.service, test_labels) as transaction:
        yield transaction
