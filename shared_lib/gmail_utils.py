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
