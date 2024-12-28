"""Helper functions for Anthropic API integration."""
import os
from typing import Optional, Dict, Any
from anthropic import Anthropic
import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from .constants import API_CONFIG

# Load environment variables from .env file
load_dotenv()

def get_anthropic_client() -> Anthropic:
    """Get configured Anthropic client."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return Anthropic(api_key=api_key)

def test_anthropic_connection(client: Optional[Anthropic] = None) -> bool:
    """Test Anthropic API connection."""
    try:
        test_client = client or get_anthropic_client()
        # Simple completion to test connection
        response = test_client.messages.create(
            model=API_CONFIG['MODEL'],
            max_tokens=API_CONFIG['MAX_TOKENS'],
            messages=[{
                "role": "user",
                "content": "Say 'test' if you can hear me"
            }]
        )
        return "test" in response.content[0].text.lower()
    except Exception as e:
        print(f"Anthropic API test failed: {str(e)}")
        return False

def mock_anthropic_client() -> MagicMock:
    """Create a mock Anthropic client for testing."""
    mock_client = MagicMock()
    mock_messages = MagicMock()
    mock_client.messages = mock_messages
    
    def mock_create(**kwargs):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="test response")]
        return mock_response
        
    mock_messages.create = mock_create
    return mock_client

@pytest.fixture
def mock_anthropic():
    """Pytest fixture for mocking Anthropic API."""
    with patch('anthropic.Anthropic') as mock_client_class:
        mock_client = mock_anthropic_client()
        mock_client_class.return_value = mock_client
        yield mock_client
