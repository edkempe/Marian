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
    from constants import API_CONFIG, DATABASE_CONFIG
    
    model = API_CONFIG['ANTHROPIC_MODEL']
    db_path = DATABASE_CONFIG['EMAIL_DB_FILE']

Note:
    When adding new configuration options:
    1. Add them to the appropriate section
    2. Include clear comments explaining their purpose
    3. Update this docstring if adding a new section
"""

from typing import Dict, List, Union, TypedDict

class APIConfig(TypedDict):
    """Type hints for API configuration."""
    ANTHROPIC_MODEL: str
    TEST_MODEL: str
    MAX_TOKENS: int
    API_TEST_MAX_TOKENS: int  # For testing API connectivity
    TEMPERATURE: float
    REQUIRED_FIELDS: List[str]
    EMAIL_ANALYSIS_PROMPT: str
    ERROR_MESSAGES: Dict[str, str]

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
    DAYS_TO_FETCH: int

# Database Configuration
DATABASE_CONFIG: DatabaseConfig = {
    # Database Files
    'EMAIL_DB_FILE': 'db_email_store.db',
    'ANALYSIS_DB_FILE': 'db_email_analysis.db',
    
    # Database URLs (SQLite)
    'EMAIL_DB_URL': 'sqlite:///db_email_store.db',
    'ANALYSIS_DB_URL': 'sqlite:///db_email_analysis.db',
    
    # Table Names
    'EMAIL_TABLE': 'emails',
    'ANALYSIS_TABLE': 'email_analysis',
}

# API Configuration
API_CONFIG: APIConfig = {
    'ANTHROPIC_MODEL': 'claude-3-haiku-20240307',
    'TEST_MODEL': 'claude-3-haiku-20240307',  # Model used in tests
    'MAX_TOKENS': 4000,
    'API_TEST_MAX_TOKENS': 10,  # Minimal tokens for API connectivity test
    'TEMPERATURE': 0.0,  # Zero temperature for consistent, deterministic outputs
    'REQUIRED_FIELDS': ['model', 'max_tokens', 'messages'],  # Required fields for API calls
    'EMAIL_ANALYSIS_PROMPT': '''Analyze the following email and provide a structured analysis in JSON format. Focus on:
1. Brief summary (2-3 sentences)
2. Category (list: work, personal, finance, etc.)
3. Priority (score 1-5, with reason)
4. Action needed (boolean, with type and deadline if true)
5. Key points (list)
6. People mentioned (list)
7. Links found (list)
8. Project/topic classification (use empty strings if none found)
9. Sentiment (positive/negative/neutral)
10. Confidence score (0-1)

Email:
{email_content}

Respond with ONLY a JSON object containing these fields:
{{
    "summary": "string",
    "category": ["string"],
    "priority_score": int,
    "priority_reason": "string",
    "action_needed": boolean,
    "action_type": ["string"],
    "action_deadline": "YYYY-MM-DD",
    "key_points": ["string"],
    "people_mentioned": ["string"],
    "links_found": ["string"],
    "links_display": ["string"],
    "project": "string",
    "topic": "string",
    "sentiment": "string",
    "confidence_score": float
}}

Note: For project and topic fields, use empty strings ("") if no clear project or topic is found.''',
    'ERROR_MESSAGES': {
        "api_error": "Error calling Anthropic API: {error}",
        "validation_error": "Error validating analysis response: {error}",
        "json_decode_error": "Error decoding JSON response: {error}",
        "database_error": "Error accessing database: {error}"
    }
}

# Logging Configuration
LOGGING_CONFIG: LoggingConfig = {
    'LOG_FILE': 'marian.log',
    'MAX_BYTES': 10485760,  # 10MB
    'BACKUP_COUNT': 5,
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'LOG_LEVEL': 'INFO',
}

# Email Processing Configuration
EMAIL_CONFIG: EmailConfig = {
    'BATCH_SIZE': 100,  # Number of emails to process in one batch
    'MAX_RETRIES': 3,   # Maximum number of retry attempts for failed operations
    'RETRY_DELAY': 5,   # Delay in seconds between retry attempts
    'DAYS_TO_FETCH': 30 # Number of days of emails to fetch by default
}

# Metrics Configuration
METRICS_CONFIG: MetricsConfig = {
    'METRICS_PORT': 8000,
}
