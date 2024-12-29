"""Helper functions for Anthropic API integration."""
import os
import logging
import sys
from typing import Optional, Dict, Any, Union
from anthropic import (
    Anthropic, APIError, APIConnectionError, APITimeoutError,
    AuthenticationError, RateLimitError, InternalServerError
)
import pytest
from pytest_mock import MockerFixture, MockFixture
from dotenv import load_dotenv
from .constants import API_CONFIG

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

def get_anthropic_client() -> Anthropic:
    """Get configured Anthropic client.
    
    Returns:
        Anthropic: Configured Anthropic client instance
        
    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set or invalid
        AuthenticationError: If API key authentication fails
        OSError: If environment access fails
        RuntimeError: If client creation fails due to system error
    """
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
    except OSError as e:
        logger.error(f"Failed to access environment variables: {str(e)}")
        raise OSError(f"Failed to access environment variables: {str(e)}")
        
    if not api_key:
        logger.error("ANTHROPIC_API_KEY environment variable not set")
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
    try:
        return Anthropic(api_key=api_key)
    except (ValueError, TypeError) as e:
        # Invalid API key format
        logger.error(f"Invalid Anthropic API key format: {str(e)}")
        raise ValueError(f"Invalid Anthropic API key format: {str(e)}")
    except AuthenticationError as e:
        # Invalid API key
        logger.error(f"Anthropic API key authentication failed: {str(e)}")
        raise AuthenticationError(f"Invalid Anthropic API key: {str(e)}")
    except (OSError, IOError) as e:
        # System I/O errors
        logger.error(f"System I/O error during client creation: {str(e)}")
        raise OSError(f"System I/O error during client creation: {str(e)}")
    except MemoryError as e:
        # Out of memory
        logger.error(f"Insufficient memory for client creation: {str(e)}")
        raise MemoryError(f"Insufficient memory for client creation: {str(e)}")

def test_anthropic_connection(client: Optional[Anthropic] = None) -> bool:
    """Test Anthropic API connection.
    
    Args:
        client: Optional pre-configured Anthropic client
        
    Returns:
        bool: True if connection test succeeds, False otherwise
        
    Raises:
        ValueError: If API configuration is invalid
        OSError: If network or system access fails
    """
    if not API_CONFIG.get('MODEL') or not API_CONFIG.get('MAX_TOKENS'):
        logger.error("Invalid API configuration: MODEL and MAX_TOKENS must be set")
        raise ValueError("Invalid API configuration: MODEL and MAX_TOKENS must be set")
        
    try:
        test_client = client or get_anthropic_client()
        response = test_client.messages.create(
            model=API_CONFIG['MODEL'],
            max_tokens=API_CONFIG['MAX_TOKENS'],
            messages=[{
                "role": "user",
                "content": "Say 'test' if you can hear me"
            }]
        )
        
        try:
            success = "test" in response.content[0].text.lower()
            if not success:
                logger.warning("Anthropic API test returned unexpected response")
            return success
        except (AttributeError, IndexError, TypeError) as e:
            logger.error(f"Invalid response format from Anthropic API: {str(e)}")
            return False
            
    except APIConnectionError as e:
        logger.error(f"Failed to connect to Anthropic API: {str(e)}")
        return False
    except APITimeoutError as e:
        logger.error(f"Anthropic API request timed out: {str(e)}")
        return False
    except RateLimitError as e:
        logger.error(f"Anthropic API rate limit exceeded: {str(e)}")
        return False
    except InternalServerError as e:
        logger.error(f"Anthropic API internal server error: {str(e)}")
        return False
    except APIError as e:
        logger.error(f"Anthropic API error: {str(e)}")
        return False
    except (OSError, IOError) as e:
        logger.error(f"Network or system error: {str(e)}")
        return False
    except MemoryError as e:
        logger.error(f"Insufficient memory during API test: {str(e)}")
        return False

@pytest.fixture
def mock_anthropic_client(mocker: Union[MockerFixture, MockFixture]) -> Anthropic:
    """Create a mock Anthropic client for testing.
    
    Args:
        mocker: pytest-mock fixture
        
    Returns:
        Mock Anthropic client that returns "test response" for all messages
        
    Raises:
        TypeError: If mocker is invalid or mock configuration fails
        AttributeError: If mock attributes cannot be set
        ValueError: If mock validation fails
        RuntimeError: If mock creation fails due to system error
    """
    if not isinstance(mocker, (MockerFixture, MockFixture)):
        logger.error("Invalid mocker provided")
        raise TypeError("mocker must be a pytest MockerFixture")
        
    try:
        mock_client = mocker.Mock(spec=Anthropic)
        mock_messages = mocker.Mock()
        mock_client.messages = mock_messages
        
        def mock_create(**kwargs):
            if not isinstance(kwargs, dict):
                raise ValueError("Invalid mock call arguments")
            mock_response = mocker.Mock()
            mock_response.content = [mocker.Mock(text="test response")]
            return mock_response
            
        mock_messages.create = mock_create
        return mock_client
        
    except AttributeError as e:
        logger.error(f"Failed to create mock attributes: {str(e)}")
        raise AttributeError(f"Failed to create mock attributes: {str(e)}")
    except TypeError as e:
        logger.error(f"Invalid mock configuration: {str(e)}")
        raise TypeError(f"Failed to configure mock: {str(e)}")
    except ValueError as e:
        logger.error(f"Mock validation failed: {str(e)}")
        raise ValueError(f"Mock validation failed: {str(e)}")
    except (OSError, IOError) as e:
        logger.error(f"System I/O error during mock creation: {str(e)}")
        raise RuntimeError(f"System error during mock creation: {str(e)}")

@pytest.fixture
def mock_anthropic():
    """Pytest fixture for mocking Anthropic API.
    
    Returns:
        Mock Anthropic client for testing
        
    Raises:
        ImportError: If required modules cannot be imported
        TypeError: If mock creation fails due to type errors
        AttributeError: If mock attributes cannot be set
        RuntimeError: If mock creation fails due to system error
    """
    try:
        with pytest.mock.patch('anthropic.Anthropic') as mock_client_class:
            mock_client = mock_anthropic_client()
            mock_client_class.return_value = mock_client
            yield mock_client
            
    except ImportError as e:
        logger.error(f"Failed to import Anthropic for mocking: {str(e)}")
        raise ImportError(f"Failed to import required modules: {str(e)}")
    except TypeError as e:
        logger.error(f"Invalid mock configuration: {str(e)}")
        raise TypeError(f"Failed to configure mock: {str(e)}")
    except AttributeError as e:
        logger.error(f"Failed to patch Anthropic module: {str(e)}")
        raise AttributeError(f"Failed to set mock attributes: {str(e)}")
    except (OSError, IOError) as e:
        logger.error(f"System I/O error during mock creation: {str(e)}")
        raise RuntimeError(f"System error during mock creation: {str(e)}")
    except MemoryError as e:
        logger.error(f"Insufficient memory during mock creation: {str(e)}")
        raise RuntimeError(f"System error during mock creation: {str(e)}")
