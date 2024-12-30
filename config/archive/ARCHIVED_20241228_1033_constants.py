"""Central configuration file for Marian project constants.

This module serves as the single source of truth for all configuration settings
used throughout the Marian project. All components should import their settings
from here rather than defining their own values.

Configuration Sections:
    - API_CONFIG: Settings for Claude API (model, tokens, temperature)
    - DATABASE_CONFIG: Database paths, URLs, and table names
    - LOGGING_CONFIG: Log file settings and formats
    - EMAIL_CONFIG: Email processing parameters
    - METRICS_CONFIG: Prometheus metrics settings

Usage:
    from config.constants import API_CONFIG, DATABASE_CONFIG

    model = API_CONFIG['ANTHROPIC_MODEL']
    db_path = DATABASE_CONFIG['EMAIL_DB_FILE']

Note:
    When adding new configuration options:
    1. Add them to the appropriate section
    2. Include clear comments explaining their purpose
    3. Update this docstring if adding a new section
"""

from typing import Dict, List, TypedDict, Union


class APIConfig(TypedDict):
    """Type hints for API configuration."""

    ANTHROPIC_MODEL: str
    TEST_MODEL: str
    MAX_TOKENS: int
    TEMPERATURE: float
    REQUIRED_FIELDS: List[str]


class DatabaseConfig(TypedDict):
    """Type hints for database configuration."""

    EMAIL_DB_FILE: str
    ANALYSIS_DB_FILE: str
    EMAIL_DB_URL: str
    ANALYSIS_DB_URL: str
    EMAIL_TABLE: str
    ANALYSIS_TABLE: str


class MetricsConfig(TypedDict):
    """Type hints for metrics configuration."""

    METRICS_PORT: int


class LoggingConfig(TypedDict):
    """Type hints for logging configuration."""

    LOG_FILE: str
    MAX_BYTES: int
    BACKUP_COUNT: int
    LOG_FORMAT: str
    LOG_LEVEL: str


class EmailConfig(TypedDict):
    """Type hints for email processing configuration."""

    BATCH_SIZE: int
    MAX_RETRIES: int
    RETRY_DELAY: int


# Database Configuration
DATABASE_CONFIG: DatabaseConfig = {
    # Database Files
    "EMAIL_DB_FILE": "data/db_email_store.db",
    "ANALYSIS_DB_FILE": "data/db_email_analysis.db",
    # Database URLs (SQLite)
    "EMAIL_DB_URL": "sqlite:///data/db_email_store.db",
    "ANALYSIS_DB_URL": "sqlite:///data/db_email_analysis.db",
    # Table Names
    "EMAIL_TABLE": "emails",
    "ANALYSIS_TABLE": "email_analysis",
}

# API Configuration
API_CONFIG: APIConfig = {
    "ANTHROPIC_MODEL": "claude-3-opus-20240229",
    "TEST_MODEL": "claude-3-haiku-20240307",  # Model used in tests
    "MAX_TOKENS": 4000,
    "TEMPERATURE": 0.0,  # Zero temperature for consistent, deterministic outputs
    "REQUIRED_FIELDS": [
        "model",
        "max_tokens",
        "messages",
    ],  # Required fields for API calls
}

# Logging Configuration
LOGGING_CONFIG: LoggingConfig = {
    "LOG_FILE": "marian.log",
    "MAX_BYTES": 10485760,  # 10MB
    "BACKUP_COUNT": 5,
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "LOG_LEVEL": "INFO",
}

# Email Processing Configuration
EMAIL_CONFIG: EmailConfig = {
    "BATCH_SIZE": 5,
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 5,  # seconds
}

# Metrics Configuration
METRICS_CONFIG: MetricsConfig = {
    "METRICS_PORT": 8000,
}
