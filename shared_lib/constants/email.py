"""Email operation constants.

This module defines all email-related constants used throughout the application.
"""

from dataclasses import dataclass, field
from typing import Dict, Set, Any

@dataclass(frozen=True)
class EmailConstants:
    """Email operation constants."""
    
    # Batch Processing
    MAX_BATCH_SIZE: int = 100
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5
    
    # Email Categories
    CATEGORIES: Set[str] = field(default_factory=lambda: {
        "INBOX",
        "SENT",
        "DRAFT",
        "TRASH",
        "SPAM",
        "IMPORTANT",
        "STARRED"
    })
    
    # Priority Levels
    PRIORITY_LEVELS: Dict[str, int] = field(default_factory=lambda: {
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3
    })
    
    # Size Limits
    MAX_SUBJECT_LENGTH: int = 255
    MAX_BODY_LENGTH: int = 100000
    MAX_RECIPIENTS: int = 100
    MAX_ATTACHMENTS: int = 10
    MAX_ATTACHMENT_SIZE: int = 25 * 1024 * 1024  # 25MB
    
    # Configuration
    CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "batch_size": 50,
        "max_retries": 3,
        "retry_delay": 5,
        "timeout": 30,
        "max_connections": 10,
    })
    
    # Email Processing
    VALID_SENTIMENTS: Set[str] = field(default_factory=lambda: {
        "positive",
        "negative",
        "neutral",
        "mixed"
    })
    
    # Email Formats
    ALLOWED_FORMATS: Set[str] = field(default_factory=lambda: {
        "text/plain",
        "text/html",
        "text/markdown",
        "text/rtf"
    })
    
    # MIME types
    ALLOWED_MIME_TYPES: Set[str] = field(default_factory=lambda: {
        "text/plain",
        "text/html",
        "application/pdf",
        "image/jpeg",
        "image/png",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    })
    
    # Analysis settings
    SENTIMENT_THRESHOLD: float = 0.5
    IMPORTANCE_THRESHOLD: float = 0.7
    SPAM_THRESHOLD: float = 0.9
    
    # Email templates
    TEMPLATES: Dict[str, str] = field(default_factory=lambda: {
        "welcome": "templates/email/welcome.html",
        "reset_password": "templates/email/reset_password.html",
        "notification": "templates/email/notification.html"
    })

    def __getitem__(self, key: str) -> Any:
        """Make the class subscriptable."""
        return getattr(self, key)

# Singleton instance
EMAIL = EmailConstants()
