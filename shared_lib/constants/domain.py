"""Domain-specific constants."""

# Email Analysis
MAX_EMAIL_SIZE = 10 * 1024 * 1024  # 10MB
MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25MB
MAX_EMAILS_PER_REQUEST = 100

# Email Categories
CATEGORIES = [
    "INBOX",
    "SENT",
    "DRAFT",
    "TRASH",
    "SPAM",
    "IMPORTANT",
    "STARRED",
]

# Priority Levels
PRIORITY = {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
}
