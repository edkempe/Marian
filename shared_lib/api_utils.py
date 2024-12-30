"""Utilities for API testing with real connections and data management."""

import socket
import pytest
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from contextlib import contextmanager
import json
import os
from pathlib import Path

@dataclass
class APITestConfig:
    """Configuration for API testing."""
    service_name: str
    test_endpoint: str  # Endpoint to test connectivity
    timeout: int = 5
    required_env_vars: List[str] = None

def check_api_connectivity(config: APITestConfig) -> bool:
    """Check if we can connect to the API service.
    
    Args:
        config: API test configuration
        
    Returns:
        bool: True if connection successful
    """
    try:
        # First check basic internet connectivity
        socket.create_connection(("8.8.8.8", 53), timeout=config.timeout)
        
        # Then check specific API endpoint
        response = requests.get(
            config.test_endpoint,
            timeout=config.timeout
        )
        return response.status_code == 200
    except (socket.timeout, requests.RequestException):
        return False

@pytest.fixture
def api_available():
    """Fixture to check API availability.
    
    Marks tests as skipped if API is not available.
    """
    def _check(config: APITestConfig):
        if not check_api_connectivity(config):
            pytest.skip(f"{config.service_name} API not available")
    return _check

class TestDataManager:
    """Manages test data for API tests."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.data_dir = Path("tests/test_data") / service_name
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def save_test_response(self, name: str, response: Dict[str, Any]):
        """Save API response for future reference or validation."""
        file_path = self.data_dir / f"{name}.json"
        with open(file_path, 'w') as f:
            json.dump(response, f, indent=2)
            
    def load_test_response(self, name: str) -> Optional[Dict[str, Any]]:
        """Load saved API response."""
        file_path = self.data_dir / f"{name}.json"
        if not file_path.exists():
            return None
        with open(file_path) as f:
            return json.load(f)
            
    def compare_with_saved(self, name: str, current_response: Dict[str, Any]) -> bool:
        """Compare current API response with saved version."""
        saved = self.load_test_response(name)
        if not saved:
            self.save_test_response(name, current_response)
            return True
        return saved == current_response

class GmailTestManager(TestDataManager):
    """Specific test data management for Gmail API."""
    
    GMAIL_CONFIG = APITestConfig(
        service_name="gmail",
        test_endpoint="https://gmail.googleapis.com/gmail/v1/users/me/profile",
        required_env_vars=["GMAIL_TEST_ACCOUNT", "GMAIL_TEST_CREDENTIALS"]
    )
    
    @staticmethod
    def get_test_account() -> Optional[str]:
        """Get test account email from environment."""
        return os.getenv("GMAIL_TEST_ACCOUNT")
    
    @contextmanager
    def test_labels(self, service, prefix: str = "TEST_"):
        """Context manager for temporary test labels.
        
        Creates temporary labels and ensures cleanup.
        
        Args:
            service: Gmail API service
            prefix: Prefix for test labels
        """
        created_labels = []
        try:
            yield created_labels
        finally:
            # Cleanup created labels
            for label in created_labels:
                try:
                    service.users().labels().delete(
                        userId='me',
                        id=label['id']
                    ).execute()
                except Exception as e:
                    print(f"Failed to cleanup label {label['name']}: {e}")

    @contextmanager
    def test_messages(self, service):
        """Context manager for test messages.
        
        Tracks created messages and ensures cleanup.
        """
        created_messages = []
        try:
            yield created_messages
        finally:
            # Archive or delete test messages
            for msg in created_messages:
                try:
                    service.users().messages().trash(
                        userId='me',
                        id=msg['id']
                    ).execute()
                except Exception as e:
                    print(f"Failed to cleanup message {msg['id']}: {e}")

def validate_response_schema(response: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Validate API response against expected schema.
    
    Args:
        response: API response to validate
        schema: Expected schema
        
    Returns:
        List of validation errors, empty if valid
    """
    errors = []
    
    def _validate_dict(data: Dict[str, Any], expected: Dict[str, Any], path: str = ""):
        for key, value_type in expected.items():
            if key not in data:
                errors.append(f"Missing key {path}{key}")
                continue
            
            if isinstance(value_type, dict):
                if not isinstance(data[key], dict):
                    errors.append(f"Expected dict for {path}{key}")
                else:
                    _validate_dict(data[key], value_type, f"{path}{key}.")
            elif not isinstance(data[key], value_type):
                errors.append(
                    f"Wrong type for {path}{key}: expected {value_type.__name__}, "
                    f"got {type(data[key]).__name__}"
                )
    
    _validate_dict(response, schema)
    return errors
