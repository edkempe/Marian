"""Global constants for the Marian project.

This module contains all configuration settings and constants used throughout the
Marian project. Settings are organized by component to maintain clarity.

Configuration Sections:
    - DATABASE: Database paths and connection settings
    - API: API settings for external services
    - SEMANTIC: Settings for semantic matching and analysis
    - SEARCH: Search and pagination settings
    - TABLES: Database table names
    - RELATIONSHIPS: Valid relationship types
    - LOGGING: Log file settings and formats
    - ERROR_MESSAGES: Standard error message templates
    - CATALOG: Catalog-specific settings
"""

from typing import Dict, List, Union, TypedDict, Any
import os

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
    COUNT: int
    BATCH_SIZE: int          # For rate limiting
    MAX_RETRIES: int
    RETRY_DELAY: int
    DAYS_TO_FETCH: int
    RATE_LIMIT: Dict[str, Union[int, float]]

class CatalogConfig(TypedDict):
    """Type hints for catalog configuration."""
    DB_FILE: str
    DB_URL: str
    CHAT_LOG: str
    ANTHROPIC_MODEL: str
    MAX_TOKENS: int
    TEMPERATURE: float
    SEMANTIC_THRESHOLD: float
    SIMILARITY_THRESHOLD: float
    RESULTS_PER_PAGE: int
    RELATIONSHIP_TYPES: List[str]
    TABLES: Dict[str, str]
    ERROR_MESSAGES: Dict[str, str]
    ENABLE_SEMANTIC: bool  # New field for semantic checking toggle

# Database Configuration
DATABASE_CONFIG: DatabaseConfig = {
    # Database Files
    'EMAIL_DB_FILE': 'data/db_email_store.db',
    'ANALYSIS_DB_FILE': 'data/db_email_analysis.db',
    
    # Database URLs (SQLite)
    'EMAIL_DB_URL': 'sqlite:///data/db_email_store.db',
    'ANALYSIS_DB_URL': 'sqlite:///data/db_email_analysis.db',
    
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
7. Project/topic classification (use empty strings if none found)
8. Sentiment (positive/negative/neutral)
9. Confidence score (0-1)

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
    'COUNT': 100,            # Number of emails to process in one run
    'BATCH_SIZE': 15,        # Number of emails to process before pausing
    'MAX_RETRIES': 3,        # Maximum number of retry attempts for failed operations
    'RETRY_DELAY': 5,        # Delay in seconds between retry attempts
    'DAYS_TO_FETCH': 7,     # Number of days of emails to fetch by default
    'RATE_LIMIT': {
        'REQUESTS_PER_MINUTE': 45,  # Keep slightly under 50 RPM limit
        'PAUSE_SECONDS': 20         # Pause duration to maintain rate limit
    }
}

# Catalog Configuration
CATALOG_CONFIG: CatalogConfig = {
    # Database Settings
    'DB_FILE': 'data/db_catalog.db',
    'DB_URL': 'sqlite:///data/db_catalog.db',
    'CHAT_LOG': 'chat_logs.jsonl',
    
    # API Settings
    'ANTHROPIC_MODEL': 'claude-2',
    'MAX_TOKENS': 1000,
    'TEMPERATURE': 0.7,
    
    # Semantic Settings
    'SEMANTIC_THRESHOLD': 0.85,
    'SIMILARITY_THRESHOLD': 0.75,
    'RESULTS_PER_PAGE': 10,
    
    # Valid Relationship Types
    'RELATIONSHIP_TYPES': [
        'contains',
        'references',
        'implements',
        'extends',
        'uses',
        'related_to'
    ],
    
    # Table Names
    'TABLES': {
        'ITEMS': 'catalog_items',
        'RELATIONSHIPS': 'catalog_relationships',
        'TAGS': 'catalog_tags',
        'ITEM_TAGS': 'catalog_item_tags',
        'CHAT_HISTORY': 'chat_history'
    },
    
    # Error Messages
    'ERROR_MESSAGES': {
        'semantic_error': 'Error in semantic analysis: {error}',
        'database_error': 'Error accessing database: {error}',
        'duplicate_error': 'Item with similar title already exists: {title}',
        'tag_error': 'Error managing tags: {error}',
        'relationship_error': 'Error managing relationships: {error}'
    },
    'ENABLE_SEMANTIC': True  # New field for semantic checking toggle
}

# Metrics Configuration
METRICS_CONFIG: MetricsConfig = {
    'METRICS_PORT': 8000,
}
