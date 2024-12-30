"""Test utilities and mock objects."""

import json
from datetime import datetime
from unittest.mock import MagicMock


class MockResponse:
    """Simple mock response object."""

    def __init__(self, data):
        self.data = data

    def execute(self):
        return self.data


class MockGmailUsers:
    """Mock Gmail users endpoint."""

    def __init__(self, gmail):
        self.gmail = gmail

    def labels(self):
        return MockGmailLabels(self.gmail)

    def messages(self):
        return MockGmailMessages(self.gmail)


class MockGmailLabels:
    """Mock Gmail labels endpoint."""

    def __init__(self, gmail):
        self.gmail = gmail

    def list(self, userId=None):
        return MockResponse({"labels": list(self.gmail.labels.values())})

    def get(self, userId=None, id=None):
        return MockResponse(self.gmail.labels.get(id))


class MockGmailMessages:
    """Mock Gmail messages endpoint."""

    def __init__(self, gmail):
        self.gmail = gmail

    def list(self, userId=None, q=None, labelIds=None):
        messages = [
            {"id": id, "threadId": msg["threadId"]}
            for id, msg in self.gmail.messages.items()
        ]
        return MockResponse({"messages": messages})

    def get(self, userId=None, id=None):
        return MockResponse(self.gmail.messages.get(id))


class MockGmail:
    """Simplified Gmail API mock."""

    def __init__(self):
        self.labels = {
            "INBOX": {"id": "INBOX", "name": "INBOX"},
            "SENT": {"id": "SENT", "name": "SENT"},
            "IMPORTANT": {"id": "IMPORTANT", "name": "IMPORTANT"},
        }

        self.messages = {
            "msg1": {
                "id": "msg1",
                "threadId": "thread1",
                "labelIds": ["INBOX"],
                "payload": {
                    "headers": [
                        {"name": "From", "value": "sender1@example.com"},
                        {"name": "To", "value": "recipient1@example.com"},
                        {"name": "Subject", "value": "Test Email 1"},
                        {"name": "Date", "value": "2024-01-01T00:00:00Z"},
                    ],
                    "body": {"data": "VGVzdCBjb250ZW50IDE="},
                },
            },
            "msg2": {
                "id": "msg2",
                "threadId": "thread2",
                "labelIds": ["SENT"],
                "payload": {
                    "headers": [
                        {"name": "From", "value": "sender2@example.com"},
                        {"name": "To", "value": "recipient2@example.com"},
                        {"name": "Subject", "value": "Test Email 2"},
                        {"name": "Date", "value": "2024-01-02T00:00:00Z"},
                    ],
                    "body": {"data": "VGVzdCBjb250ZW50IDI="},
                },
            },
        }

    def users(self):
        return MockGmailUsers(self)


class MockAnalyzer:
    """Simplified email analyzer mock."""

    def __init__(self):
        self.analyses = {
            "meeting": {
                "summary": "Meeting scheduled for tomorrow",
                "category": "calendar",
                "sentiment": "neutral",
                "action_items": ["Attend meeting tomorrow"],
                "key_points": ["Meeting scheduled"],
            },
            "review": {
                "summary": "Document review request",
                "category": "review",
                "sentiment": "neutral",
                "action_items": ["Review document"],
                "key_points": ["Review needed"],
            },
        }

    def analyze(self, content):
        """Return mock analysis based on content."""
        if "meeting" in content.lower():
            return self.analyses["meeting"]
        return self.analyses["review"]


def create_test_email(id="test1", subject="Test Subject", content="Test content"):
    """Create a test email object."""
    return {
        "id": id,
        "thread_id": f"thread_{id}",
        "subject": subject,
        "from_address": "sender@example.com",
        "to_address": "recipient@example.com",
        "content": content,
        "received_date": datetime.utcnow(),
    }
