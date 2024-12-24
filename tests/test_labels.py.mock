"""Tests for Gmail label functionality."""
import pytest
from app_get_mail import get_label_id, list_labels
from tests.test_utils import MockGmail

def test_get_label_id_success():
    """Test successful label ID retrieval."""
    gmail = MockGmail()
    assert get_label_id(gmail, 'INBOX') == 'INBOX'
    assert get_label_id(gmail, 'SENT') == 'SENT'

def test_get_label_id_nonexistent():
    """Test handling of non-existent label."""
    gmail = MockGmail()
    assert get_label_id(gmail, 'NONEXISTENT') is None

def test_get_label_id_empty():
    """Test handling of empty label name."""
    gmail = MockGmail()
    assert get_label_id(gmail, '') is None
    assert get_label_id(gmail, None) is None

def test_list_labels_success():
    """Test successful label listing."""
    gmail = MockGmail()
    labels = list_labels(gmail)
    assert len(labels) == 3
    assert any(label['name'] == 'INBOX' for label in labels)
    assert any(label['name'] == 'SENT' for label in labels)

def test_list_labels_error():
    """Test handling of API error in label listing."""
    gmail = MockGmail()
    gmail.list_labels = lambda: None  # Simulate API error
    labels = list_labels(gmail)
    assert labels == []
