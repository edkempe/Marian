"""Test constants for Marian tests."""

from datetime import datetime, timezone

# Test Dates (all in UTC)
TEST_DATES = [
    datetime(2024, 1, 1, tzinfo=timezone.utc),
    datetime(2024, 1, 2, tzinfo=timezone.utc),
    datetime(2024, 1, 3, tzinfo=timezone.utc),
]

# Email Test Data
TEST_EMAIL = {
    "id": "test1",
    "thread_id": "thread1",
    "subject": "Test Subject",
    "from_": "from@test.com",
    "to": "to@test.com",
    "body": "Test content",
}

# Message IDs
TEST_MESSAGE_IDS = {
    "PLAIN": "test_plain",
    "HTML": "test_html",
    "ATTACHMENTS": "test_attachments",
    "MINIMAL": "test_minimal",
    "UNICODE": "test_unicode",
}

# Error Messages
TEST_INVALID_ID = "invalid_id"
TEST_ERROR_PREFIX = "Failed to process email"
API_ERROR_MESSAGE = "API Error"

# Test Content
TEST_PLAIN_TEXT = "Hello, this is a test email"
TEST_HTML_CONTENT = "<html><body><h1>Test</h1><p>Hello World!</p></body></html>"
TEST_UNICODE_TEXT = "Hello, 世界! こんにちは"

# Gmail API Test Data
TEST_LABELS = {
    "INBOX": {"id": "INBOX", "name": "INBOX"},
    "SENT": {"id": "SENT", "name": "SENT"},
    "IMPORTANT": {"id": "IMPORTANT", "name": "IMPORTANT"},
}

TEST_ATTACHMENTS = [{
    "partId": "1",
    "mimeType": "application/pdf",
    "filename": "test.pdf",
    "body": {"attachmentId": "att1"}
}]

# Test Message Structure
TEST_MESSAGE = {
    "id": TEST_MESSAGE_IDS["PLAIN"],
    "threadId": "thread1",
    "labelIds": ["INBOX"],
    "snippet": "Test email snippet",
    "payload": {
        "mimeType": "text/plain",
        "headers": [
            {"name": "Subject", "value": "Test Subject"},
            {"name": "From", "value": "from@test.com"},
            {"name": "To", "value": "to@test.com"},
            {"name": "Date", "value": "Tue, 1 Jan 2024 00:00:00 +0000"}
        ],
        "body": {"data": "VGVzdCBjb250ZW50"}  # Base64 encoded "Test content"
    }
}

# Test Messages Collection
TEST_MESSAGES = {
    "PLAIN": {
        "id": TEST_MESSAGE_IDS["PLAIN"],
        "threadId": "thread1",
        "labelIds": ["INBOX"],
        "snippet": "Plain text email",
        "payload": {
            "mimeType": "text/plain",
            "headers": [
                {"name": "Subject", "value": "Plain Text Email"},
                {"name": "From", "value": "sender@test.com"},
                {"name": "To", "value": "recipient@test.com"},
                {"name": "Date", "value": "Tue, 1 Jan 2024 00:00:00 +0000"}
            ],
            "body": {"data": "UGxhaW4gdGV4dCBjb250ZW50"}  # "Plain text content"
        }
    },
    "HTML": {
        "id": TEST_MESSAGE_IDS["HTML"],
        "threadId": "thread2",
        "labelIds": ["INBOX"],
        "snippet": "HTML email",
        "payload": {
            "mimeType": "text/html",
            "headers": [
                {"name": "Subject", "value": "HTML Email"},
                {"name": "From", "value": "sender@test.com"},
                {"name": "To", "value": "recipient@test.com"},
                {"name": "Date", "value": "Tue, 1 Jan 2024 00:00:00 +0000"}
            ],
            "body": {"data": "PGgxPlRlc3Q8L2gxPjxwPkhUTUwgY29udGVudDwvcD4="}  # "<h1>Test</h1><p>HTML content</p>"
        }
    },
    "ATTACHMENTS": {
        "id": TEST_MESSAGE_IDS["ATTACHMENTS"],
        "threadId": "thread3",
        "labelIds": ["INBOX"],
        "snippet": "Email with attachments",
        "payload": {
            "mimeType": "multipart/mixed",
            "headers": [
                {"name": "Subject", "value": "Email with Attachments"},
                {"name": "From", "value": "sender@test.com"},
                {"name": "To", "value": "recipient@test.com"},
                {"name": "Date", "value": "Tue, 1 Jan 2024 00:00:00 +0000"}
            ],
            "parts": [
                {
                    "partId": "0",
                    "mimeType": "text/plain",
                    "body": {"data": "RW1haWwgd2l0aCBhdHRhY2htZW50cw=="}  # "Email with attachments"
                },
                {
                    "partId": "1",
                    "mimeType": "application/pdf",
                    "filename": "test.pdf",
                    "body": {"attachmentId": "att1"}
                }
            ]
        }
    }
}
