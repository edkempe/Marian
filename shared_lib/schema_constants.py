"""Schema-related constants used across the codebase.

This module contains all schema-related constants like column sizes,
default values, and validation rules. It serves as a single source
of truth for these values.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

# Column sizes
COLUMN_SIZES = {
    # Email model
    "EMAIL_ID": 100,
    "EMAIL_THREAD_ID": 100,
    "EMAIL_MESSAGE_ID": 100,
    "EMAIL_SUBJECT": 500,
    "EMAIL_FROM": 255,
    "EMAIL_TO": 255,
    "EMAIL_CC": 255,
    "EMAIL_BCC": 255,
    "EMAIL_LABELS": 500,
    
    # Analysis model
    "ANALYSIS_SENTIMENT": 20,
    "ANALYSIS_CATEGORY": 50,
    "ANALYSIS_SUMMARY": 1000,
    "ANALYSIS_PRIORITY": 20,
    
    # Label model
    "LABEL_ID": 100,
    "LABEL_NAME": 255,
    "LABEL_TYPE": 20,
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
