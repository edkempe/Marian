"""Validation constants and rules.

This module defines validation rules and error messages used across the application.
"""

from dataclasses import dataclass, field
from typing import Dict, Pattern
import re

@dataclass(frozen=True)
class ValidationRules:
    """Validation rules for various data types."""

    # String validation
    MIN_STRING_LENGTH: int = 1
    MAX_STRING_LENGTH: int = 1000
    EMAIL_PATTERN: Pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    URL_PATTERN: Pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$", re.IGNORECASE)
    
    # API ID patterns
    GMAIL_MESSAGE_ID_PATTERN: Pattern = re.compile(r"^[A-Za-z0-9-_]{16,}$")
    GMAIL_THREAD_ID_PATTERN: Pattern = re.compile(r"^[A-Za-z0-9-_]{16,}$")
    GMAIL_LABEL_ID_PATTERN: Pattern = re.compile(r"^[A-Za-z0-9-_]+$")
    ANALYSIS_ID_PATTERN: Pattern = re.compile(r"^analysis_[A-Za-z0-9]+$")
    
    # Numeric validation
    MIN_INTEGER: int = -2**31
    MAX_INTEGER: int = 2**31 - 1
    MIN_FLOAT: float = -1e308
    MAX_FLOAT: float = 1e308
    
    # Score ranges
    MIN_PRIORITY_SCORE: int = 1
    MAX_PRIORITY_SCORE: int = 5
    MIN_CONFIDENCE_SCORE: float = 0.0
    MAX_CONFIDENCE_SCORE: float = 1.0
    
    # Array limits
    MAX_LABEL_IDS: int = 100
    MAX_CATEGORIES: int = 10
    MAX_KEY_POINTS: int = 20
    MAX_ACTION_ITEMS: int = 10
    
    # Date and time formats
    DATE_FORMAT: str = "%Y-%m-%d"
    TIME_FORMAT: str = "%H:%M:%S"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    TIMEZONE_FORMAT: str = "%z"

    # File validation
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_EXTENSIONS: set[str] = field(default_factory=lambda: {
        # Documents
        "txt", "md", "pdf", "doc", "docx",
        # Images
        "jpg", "jpeg", "png", "gif",
        # Data
        "csv", "json", "xml", "yaml", "yml",
        # Code
        "py", "js", "html", "css"
    })


@dataclass(frozen=True)
class ValidationErrors:
    """Validation error messages."""
    
    # General errors
    REQUIRED_FIELD: str = "Field '{field}' is required"
    INVALID_TYPE: str = "Field '{field}' must be of type {expected_type}"
    INVALID_LENGTH: str = "Field '{field}' length must be between {min_length} and {max_length}"
    INVALID_VALUE: str = "Field '{field}' has invalid value: {value}"
    
    # API validation errors
    INVALID_API_RESPONSE: str = "Invalid API response format: {details}"
    MISSING_REQUIRED_FIELD: str = "Required field '{field}' missing in API response"
    INVALID_FIELD_TYPE: str = "Field '{field}' in API response has invalid type"
    FIELD_CONSTRAINT_VIOLATION: str = "Field '{field}' violates API constraints: {details}"
    
    # Gmail API specific errors
    INVALID_MESSAGE_ID: str = "Invalid Gmail message ID format"
    INVALID_THREAD_ID: str = "Invalid Gmail thread ID format"
    INVALID_LABEL_ID: str = "Invalid Gmail label ID format"
    TOO_MANY_LABELS: str = f"Number of labels exceeds maximum ({ValidationRules.MAX_LABEL_IDS})"
    
    # Analysis specific errors
    INVALID_ANALYSIS_ID: str = "Invalid analysis ID format"
    INVALID_PRIORITY_SCORE: str = f"Priority score must be between {ValidationRules.MIN_PRIORITY_SCORE} and {ValidationRules.MAX_PRIORITY_SCORE}"
    INVALID_CONFIDENCE_SCORE: str = f"Confidence score must be between {ValidationRules.MIN_CONFIDENCE_SCORE} and {ValidationRules.MAX_CONFIDENCE_SCORE}"
    INVALID_SENTIMENT: str = "Invalid sentiment value"
    TOO_MANY_CATEGORIES: str = f"Number of categories exceeds maximum ({ValidationRules.MAX_CATEGORIES})"
    TOO_MANY_KEY_POINTS: str = f"Number of key points exceeds maximum ({ValidationRules.MAX_KEY_POINTS})"
    TOO_MANY_ACTION_ITEMS: str = f"Number of action items exceeds maximum ({ValidationRules.MAX_ACTION_ITEMS})"


# Singleton instances
RULES = ValidationRules()
VALIDATION_ERRORS = ValidationErrors()
