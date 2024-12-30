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
