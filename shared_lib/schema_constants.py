"""Schema-related constants used across the codebase.

This module contains all schema-related constants like column sizes,
default values, and validation rules. It serves as a single source
of truth for these values.

Following ADR-0019 (API-First Schema Design), these constants exactly
match the external API specifications.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

# Column sizes - maximum lengths for database columns
COLUMN_SIZES = {
    # Gmail API Message fields
    "MESSAGE_ID": 100,  # Gmail message ID
    "THREAD_ID": 100,  # Gmail thread ID
    "LABEL_ID": 100,  # Gmail label ID
    "SNIPPET": 1000,  # Message snippet
    "HISTORY_ID": 20,  # Gmail history ID
    
    # Email fields from message payload
    "SUBJECT": 500,  # Email subject line
    "EMAIL_ADDRESS": 255,  # Email address (from/to/cc/bcc)
    "MIME_TYPE": 100,  # MIME type
    "FILENAME": 255,  # Attachment filename
    "ATTACHMENT_ID": 100,  # Attachment ID
    
    # Anthropic API Analysis fields
    "ANALYSIS_ID": 100,  # Analysis ID (pattern: analysis_[A-Za-z0-9]+)
    "SUMMARY": 1000,  # Email summary
    "CATEGORY": 50,  # Email category
    "KEY_POINT": 200,  # Single key point
    "ACTION_DESCRIPTION": 500,  # Action item description
    "MODEL_VERSION": 50,  # Claude model version
}

# Maximum array lengths
MAX_LENGTHS = {
    "TO_ADDRESSES": 100,
    "CC_ADDRESSES": 50,
    "BCC_ADDRESSES": 50,
    "LABEL_IDS": 100,
    "CATEGORIES": 10,
    "KEY_POINTS": 20,
    "ACTION_ITEMS": 10,
    "MESSAGE_PARTS": 50,
    "HEADERS": 100
}

# Value constraints from API specs
VALUE_RANGES = {
    "PRIORITY_SCORE": {
        "min": 1,
        "max": 5,
        "description": "Computed priority score (1-5)"
    },
    "CONFIDENCE_SCORE": {
        "min": 0.0,
        "max": 1.0,
        "description": "Confidence in analysis (0.0-1.0)"
    }
}

# Enumerated values from API specs
ENUMS = {
    "SENTIMENT": [
        "positive",
        "negative",
        "neutral",
        "mixed"
    ],
    "PRIORITY": [
        "high",
        "medium",
        "low"
    ],
    "ACTION_STATUS": [
        "pending",
        "in_progress",
        "completed"
    ]
}

# Regular expression patterns from API specs
PATTERNS = {
    "ANALYSIS_ID": r"^analysis_[A-Za-z0-9]+$",
    "MODEL_VERSION": r"^claude-3-opus-[0-9]{8}$"
}

@dataclass
class MessageDefaults:
    """Default values for Gmail Message fields."""
    
    id: Optional[str] = None
    threadId: Optional[str] = None
    labelIds: list = None
    snippet: Optional[str] = None
    historyId: Optional[str] = None
    sizeEstimate: Optional[int] = None
    raw: Optional[str] = None
    payload: dict = None
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.labelIds is None:
            self.labelIds = []
        if self.payload is None:
            self.payload = {}


@dataclass
class AnalysisDefaults:
    """Default values for Anthropic Analysis fields."""
    
    id: Optional[str] = None
    email_id: Optional[str] = None
    summary: Optional[str] = None
    sentiment: str = "neutral"
    categories: list = None
    key_points: list = None
    action_items: list = None
    priority_score: Optional[int] = None
    confidence_score: Optional[float] = None
    metadata: dict = None
    model_version: Optional[str] = None
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.categories is None:
            self.categories = []
        if self.key_points is None:
            self.key_points = []
        if self.action_items is None:
            self.action_items = []
        if self.metadata is None:
            self.metadata = {}
