"""Tests for Gmail label functionality."""
import pytest
from unittest.mock import MagicMock, patch
from app_get_mail import get_label_id, list_labels

@pytest.fixture
def mock_service():
    """Simple mock Gmail service for label tests."""
    service = MagicMock()
    
    # Mock the labels response
    service.users.return_value.labels.return_value.list.return_value.execute.return_value = {
        'labels': [
            {'id': 'INBOX', 'name': 'INBOX'},
            {'id': 'SENT', 'name': 'SENT'},
            {'id': 'IMPORTANT', 'name': 'IMPORTANT'}
        ]
    }
    
    return service

@pytest.mark.parametrize('label_name,expected_id', [
    ('INBOX', 'INBOX'),
    ('SENT', 'SENT'),
    ('IMPORTANT', 'IMPORTANT'),
    ('NONEXISTENT', None),
    ('', None),
    (None, None),
])
def test_get_label_id(mock_service, label_name, expected_id):
    """Test label ID retrieval with various inputs."""
    assert get_label_id(mock_service, label_name) == expected_id

def test_get_label_id_error(mock_service):
    """Test handling of API errors in label ID retrieval."""
    mock_service.users.return_value.labels.return_value.list.return_value.execute.side_effect = Exception('API Error')
    assert get_label_id(mock_service, 'INBOX') is None

def test_list_labels(mock_service):
    """Test listing Gmail labels."""
    labels = list_labels(mock_service)
    assert len(labels) == 3
    assert any(label['name'] == 'INBOX' for label in labels)
    assert any(label['name'] == 'SENT' for label in labels)
    assert any(label['name'] == 'IMPORTANT' for label in labels)

def test_list_labels_error(mock_service):
    """Test handling of API errors in label listing."""
    mock_service.users.return_value.labels.return_value.list.return_value.execute.side_effect = Exception('API Error')
    assert list_labels(mock_service) == []
