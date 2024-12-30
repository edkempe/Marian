"""Database schema constants.

This module contains constants related to database schema definitions.
These constants can be used by both the shared library and model layers.
"""

# Column size limits
COLUMN_SIZES = {
    # Email-related sizes
    "EMAIL_LABELS": 500,
    "EMAIL_SUBJECT": 500,
    "EMAIL_SENDER": 200,
    "EMAIL_THREAD": 100,
    "EMAIL_TO": 200,
    "EMAIL_ID": 100,
    
    # Analysis-related sizes
    "ANALYSIS_SENTIMENT": 50,
    "ANALYSIS_CATEGORY": 100,
    "ANALYSIS_SUMMARY": 1000,
    
    # Label-related sizes
    "LABEL_ID": 100,
    "LABEL_NAME": 200,
}

# Default values
DEFAULTS = {
    "EMAIL_SUBJECT": "",
    "EMPTY_STRING": "",
    "HAS_ATTACHMENTS": False,
    "API_RESPONSE": "{}",
    "SENTIMENT_DEFAULT": "neutral",
    "CATEGORY_DEFAULT": "uncategorized",
}

# Validation constants
VALID_SENTIMENTS = {"positive", "negative", "neutral", "mixed"}
VALID_PRIORITIES = {"high", "medium", "low"}
MAX_SUMMARY_LENGTH = 1000
