"""Schema-related constants used across the codebase.

This module contains all schema-related constants like column sizes,
default values, and validation rules. It serves as a single source
of truth for these values.

Constants:
    COLUMN_SIZES: Dictionary defining maximum lengths for database columns
    EMAIL_DEFAULTS: Default values for email-related fields
    LABEL_DEFAULTS: Default values for label-related fields
    ANALYSIS_DEFAULTS: Default values for analysis-related fields
    VALIDATION_RULES: Rules for validating field values
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

# Column sizes - maximum lengths for database columns
COLUMN_SIZES = {
    # Email model
    "EMAIL_ID": 100,  # Primary key, UUID4 string
    "EMAIL_THREAD_ID": 100,  # Gmail thread ID
    "EMAIL_MESSAGE_ID": 100,  # Gmail message ID
    "EMAIL_SUBJECT": 500,  # Email subject line
    "EMAIL_FROM": 255,  # Sender email address
    "EMAIL_TO": 255,  # Recipient email addresses
    "EMAIL_CC": 255,  # CC email addresses
    "EMAIL_BCC": 255,  # BCC email addresses
    "EMAIL_LABELS": 500,  # Gmail labels (comma-separated)
    
    # Analysis model
    "ANALYSIS_SENTIMENT": 20,  # Sentiment classification
    "ANALYSIS_CATEGORY": 50,  # Email category
    "ANALYSIS_SUMMARY": 1000,  # Email summary
    "ANALYSIS_PRIORITY": 20,  # Priority level
    
    # Label model
    "LABEL_ID": 100,  # Gmail label ID
    "LABEL_NAME": 255,  # Label display name
    "LABEL_TYPE": 20,  # Label type (system/user)
}

# Default values
@dataclass
class EmailDefaults:
    """Default values for email fields."""
    subject: str = ""
    body: Optional[str] = None
    snippet: Optional[str] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    cc_address: Optional[str] = None
    bcc_address: Optional[str] = None
    has_attachments: bool = False
    is_read: bool = False
    is_important: bool = False
    api_response: str = "{}"

@dataclass
class AnalysisDefaults:
    """Default values for analysis fields."""
    sentiment: str = "neutral"
    category: str = "uncategorized"
    summary: Optional[str] = None
    priority: str = "low"

@dataclass
class LabelDefaults:
    """Default values for label fields."""
    name: str = ""
    type: str = "user"
    message_list_visibility: str = "show"
    label_list_visibility: str = "labelShow"
    is_system: bool = False

# Validation rules
VALIDATION_RULES = {
    "EMAIL": {
        "subject": {
            "max_length": COLUMN_SIZES["EMAIL_SUBJECT"],
            "required": True,
        },
        "labels": {
            "max_length": COLUMN_SIZES["EMAIL_LABELS"],
            "valid_values": ["INBOX", "SENT", "DRAFT", "SPAM", "TRASH", "IMPORTANT", "STARRED"],
        },
    },
    "ANALYSIS": {
        "sentiment": {
            "max_length": COLUMN_SIZES["ANALYSIS_SENTIMENT"],
            "valid_values": ["positive", "negative", "neutral", "mixed"],
        },
        "category": {
            "max_length": COLUMN_SIZES["ANALYSIS_CATEGORY"],
            "valid_values": ["work", "personal", "finance", "social", "support", "uncategorized"],
        },
        "priority": {
            "max_length": COLUMN_SIZES["ANALYSIS_PRIORITY"],
            "valid_values": ["high", "medium", "low"],
        },
    },
    "LABEL": {
        "type": {
            "max_length": COLUMN_SIZES["LABEL_TYPE"],
            "valid_values": ["system", "user"],
        },
        "message_list_visibility": {
            "valid_values": ["show", "hide"],
        },
        "label_list_visibility": {
            "valid_values": ["labelShow", "labelHide"],
        },
    },
}
