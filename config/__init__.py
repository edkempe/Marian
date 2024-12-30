"""Configuration module for Marian.

This module provides configuration settings for various components:
- Email: Settings for Gmail API and email processing
- Catalog: Settings for the catalog system
- Database: Database connection settings
"""

from pathlib import Path

# Email configuration
EMAIL_CONFIG = {
    "BATCH_SIZE": 10,
    "COUNT": 100,
    "LABELS": ["INBOX", "SENT"],
    "EXCLUDED_LABELS": ["SPAM", "TRASH"],
}

# Catalog configuration
CATALOG_CONFIG = {
    "ENABLE_SEMANTIC": True,
    "DB_PATH": str(Path(__file__).parent.parent / "data" / "db_catalog.db"),
    "CHAT_LOG": "chat_logs.jsonl",
    "ERROR_MESSAGES": {
        "API_ERROR": "Failed to get API response: {}",
        "DATABASE_ERROR": "Database error: {}",
        "JSON_DECODE_ERROR": "Failed to decode JSON: {}",
        "DUPLICATE_ERROR": "Duplicate entry: {}",
    },
}
