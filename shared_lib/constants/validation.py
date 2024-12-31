"""Validation constants and rules.

This module defines validation rules and error messages used across the application.
"""

from dataclasses import dataclass
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
    
    # Numeric validation
    MIN_INTEGER: int = -2**31
    MAX_INTEGER: int = 2**31 - 1
    MIN_FLOAT: float = -1e308
    MAX_FLOAT: float = 1e308
    
    # Date and time formats
    DATE_FORMAT: str = "%Y-%m-%d"
    TIME_FORMAT: str = "%H:%M:%S"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    TIMEZONE_FORMAT: str = "%z"

    # File validation
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_EXTENSIONS: set[str] = {
        # Documents
        "txt", "md", "pdf", "doc", "docx",
        # Images
        "jpg", "jpeg", "png", "gif",
        # Data
        "csv", "json", "xml",
        # Code
        "py", "js", "html", "css"
    }

@dataclass(frozen=True)
class ErrorMessages:
    """Standard error messages for validation failures."""
    
    MESSAGES: Dict[str, str] = {
        # General errors
        "required": "This field is required.",
        "invalid": "Invalid value provided.",
        "not_found": "Resource not found.",
        
        # String errors
        "min_length": "Value must be at least {min_length} characters long.",
        "max_length": "Value cannot exceed {max_length} characters.",
        "email": "Invalid email address format.",
        "url": "Invalid URL format.",
        
        # Numeric errors
        "min_value": "Value must be greater than or equal to {min_value}.",
        "max_value": "Value must be less than or equal to {max_value}.",
        "not_number": "Value must be a number.",
        
        # Date/time errors
        "invalid_date": "Invalid date format. Use YYYY-MM-DD.",
        "invalid_time": "Invalid time format. Use HH:MM:SS.",
        "invalid_datetime": "Invalid datetime format. Use YYYY-MM-DD HH:MM:SS.",
        
        # File errors
        "file_too_large": "File size cannot exceed {max_size} bytes.",
        "invalid_extension": "File extension not allowed.",
        
        # Database errors
        "unique": "This value already exists.",
        "foreign_key": "Referenced resource does not exist.",
        
        # Authentication errors
        "invalid_credentials": "Invalid username or password.",
        "expired_token": "Authentication token has expired.",
        "insufficient_permissions": "Insufficient permissions for this action."
    }

# Singleton instances
RULES = ValidationRules()
ERRORS = ErrorMessages()
