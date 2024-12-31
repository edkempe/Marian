"""Email operation constants.

This module defines all email-related constants used throughout the application.
"""

from dataclasses import dataclass
from typing import Dict, List, Set

@dataclass(frozen=True)
class EmailConstants:
    """Email operation constants."""
    
    # Email processing
    MAX_BATCH_SIZE: int = 100
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # seconds
    
    # Email categories
    CATEGORIES: Set[str] = {
        "INBOX",
        "SENT",
        "DRAFT",
        "TRASH",
        "SPAM",
        "IMPORTANT",
        "STARRED"
    }
    
    # Priority levels
    PRIORITY_LEVELS: Dict[str, int] = {
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3
    }
    
    # Email validation
    MAX_SUBJECT_LENGTH: int = 255
    MAX_BODY_LENGTH: int = 100000
    MAX_RECIPIENTS: int = 100
    MAX_ATTACHMENTS: int = 10
    MAX_ATTACHMENT_SIZE: int = 25 * 1024 * 1024  # 25MB
    
    # MIME types
    ALLOWED_MIME_TYPES: Set[str] = {
        "text/plain",
        "text/html",
        "application/pdf",
        "image/jpeg",
        "image/png",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    
    # Analysis settings
    SENTIMENT_THRESHOLD: float = 0.5
    IMPORTANCE_THRESHOLD: float = 0.7
    SPAM_THRESHOLD: float = 0.9
    
    # Email templates
    TEMPLATES: Dict[str, str] = {
        "welcome": "templates/email/welcome.html",
        "reset_password": "templates/email/reset_password.html",
        "notification": "templates/email/notification.html"
    }

# Singleton instance
EMAIL = EmailConstants()
