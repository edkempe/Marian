"""Constants used in tests."""

# Email test data
TEST_EMAIL_SUBJECT = "Test Email Subject"
TEST_EMAIL_BODY = "This is a test email body."
TEST_EMAIL_SENDER = "test@example.com"
TEST_EMAIL_RECIPIENT = "recipient@example.com"
TEST_EMAIL_CC = "cc@example.com"
TEST_EMAIL_BCC = "bcc@example.com"
TEST_IMPORTANT_EMAIL_BODY = "This is an important work email that requires review by tomorrow."

# Analysis test data
TEST_ANALYSIS_SUMMARY = "Test analysis summary"
TEST_ANALYSIS_CATEGORY = ["WORK", "IMPORTANT"]
TEST_MIN_PRIORITY = 4  # Minimum expected priority for important work emails

# Gmail label test data
TEST_LABEL_NAME = "Test Label"
TEST_LABEL_TYPE = "user"

# Test API responses
TEST_GMAIL_API_RESPONSE = {
    "id": "test_id",
    "threadId": "test_thread",
    "labelIds": ["INBOX", "UNREAD"],
    "snippet": "Test email snippet...",
}

# Test configuration
TEST_MODE = True  # Flag for running components in test mode
