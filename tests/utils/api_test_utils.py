"""API testing utilities with pagination support."""

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

class MockAPIResponse:
    """Helper class for mocking paginated API responses."""
    
    def __init__(self, service: MagicMock):
        """Initialize with a mock service."""
        self.service = service
        self._pagination_mocked = False
        self._response_mocked = False
    
    def mock_response(self, response_data: Dict[str, Any]) -> 'MockAPIResponse':
        """Mock the initial API response.
        
        Args:
            response_data: The response data to return
            
        Returns:
            self for method chaining
        """
        self.service.execute.return_value = response_data
        self._response_mocked = True
        return self
    
    def mock_pagination(self, next_page: Optional[Dict[str, Any]] = None) -> 'MockAPIResponse':
        """Mock the pagination behavior.
        
        Args:
            next_page: Response data for the next page, or None if no more pages
            
        Returns:
            self for method chaining
        """
        if next_page:
            next_request = MagicMock()
            next_request.execute.return_value = next_page
            self.service.list_next.return_value = next_request
        else:
            self.service.list_next.return_value = None
            
        self._pagination_mocked = True
        return self
    
    def verify_complete(self):
        """Verify that both response and pagination are mocked."""
        if not self._response_mocked:
            raise ValueError("API response not mocked. Call mock_response() first.")
        if not self._pagination_mocked:
            raise ValueError("Pagination not mocked. Call mock_pagination() to prevent hanging tests.")


def mock_gmail_messages(service: MagicMock, messages: List[Dict[str, Any]]) -> MockAPIResponse:
    """Mock Gmail messages API with proper pagination.
    
    Example:
        ```python
        # Mock a single page of results
        mock_gmail_messages(service, [{"id": "msg1"}]).mock_pagination()
        
        # Mock multiple pages
        mock_gmail_messages(service, [{"id": "msg1"}]).mock_pagination({
            "messages": [{"id": "msg2"}]
        })
        ```
    
    Args:
        service: Mock Gmail service
        messages: List of message data to return in first page
        
    Returns:
        MockAPIResponse for further configuration
    """
    response = MockAPIResponse(service.users().messages())
    return response.mock_response({"messages": messages})


def mock_gmail_labels(service: MagicMock, labels: List[Dict[str, Any]]) -> MockAPIResponse:
    """Mock Gmail labels API with proper pagination.
    
    Args:
        service: Mock Gmail service
        labels: List of label data to return
        
    Returns:
        MockAPIResponse for further configuration
    """
    response = MockAPIResponse(service.users().labels())
    return response.mock_response({"labels": labels})
