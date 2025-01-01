"""Gmail API test utilities."""

from unittest.mock import MagicMock
from typing import Dict, List, Optional
from googleapiclient.errors import HttpError

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

def setup_mock_messages(service: MagicMock, messages_data: List[Dict]):
    """Set up mock messages response with pagination handling.
    
    Args:
        service: Mock Gmail service
        messages_data: List of message dictionaries to return
    """
    messages = service.users().messages.return_value
    messages.list().execute.return_value = {
        'messages': messages_data,
        'nextPageToken': None
    }

def setup_mock_labels(service: MagicMock, labels_data: List[Dict]):
    """Set up mock labels response.
    
    Args:
        service: Mock Gmail service
        labels_data: List of label dictionaries to return
    """
    labels = service.users().labels.return_value
    labels.list().execute.return_value = {'labels': labels_data}

def setup_mock_message(service: MagicMock, message_data: Dict):
    """Set up mock message get response.
    
    Args:
        service: Mock Gmail service
        message_data: Message data to return
    """
    messages = service.users().messages.return_value
    messages.get().execute.return_value = message_data

def create_test_label(service: MagicMock, name: str) -> Dict:
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
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
        created = service.users().labels().create(userId='me', body=label).execute()
        return created
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def create_test_email(service: MagicMock,
                     subject: str = "Test Email",
                     body: str = "Test Body",
                     sender: str = "test@example.com",
                     label_ids: Optional[List[str]] = None) -> Dict:
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
    try:
        message = MIMEMultipart()
        message['to'] = "user@example.com"
        message['from'] = sender
        message['subject'] = subject

        msg = MIMEText(body)
        message.attach(msg)
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        return service.users().messages().send(
            userId='me',
            body={'raw': raw, 'labelIds': label_ids or []}
        ).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None
