"""Tests for API version utilities."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from shared_lib.api_version_utils import (
    verify_api_compatibility,
    verify_required_features,
    check_api_status,
    monitor_api_versions,
    APIVersionError,
    APIFeatureError
)

def test_verify_api_compatibility():
    """Test API compatibility verification."""
    service = MagicMock()
    
    # Test valid API
    assert verify_api_compatibility('gmail', service) is None
    
    # Test unknown API
    with pytest.raises(ValueError, match="Unknown API"):
        verify_api_compatibility('unknown_api', service)
        
    # Test deprecated API
    with pytest.patch('shared_lib.api_version_utils.load_api_versions') as mock_load:
        mock_load.return_value = {
            'test_api': {
                'deprecation_date': (
                    datetime.now() - timedelta(days=1)
                ).strftime('%Y-%m-%d')
            }
        }
        error = verify_api_compatibility('test_api', service)
        assert "deprecated" in error

def test_verify_required_features():
    """Test feature verification."""
    service = MagicMock()
    
    # Test all features available
    service.users.messages.list = lambda: None
    service.users.labels.create = lambda: None
    
    missing = verify_required_features('gmail', service)
    assert not missing
    
    # Test missing feature
    delattr(service.users.messages, 'list')
    missing = verify_required_features('gmail', service)
    assert 'users.messages.list' in missing

def test_check_api_status():
    """Test API status checking."""
    # Test valid status
    with pytest.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        assert check_api_status('gmail') is None
        
    # Test failed status check
    with pytest.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        warning = check_api_status('gmail')
        assert "failed" in warning

def test_monitor_api_versions():
    """Test API version monitoring."""
    with pytest.patch('shared_lib.api_version_utils.load_api_versions') as mock_load:
        mock_load.return_value = {
            'test_api': {
                'last_verified': (
                    datetime.now() - timedelta(days=31)
                ).strftime('%Y-%m-%d')
            }
        }
        
        issues = monitor_api_versions()
        assert 'test_api' in issues
        assert any('Not verified' in issue for issue in issues['test_api'])
