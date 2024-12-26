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

# Shared Constants
DATA_DIR = 'data'
DEFAULT_MODEL = 'claude-3-haiku-20240307'

class APIConfig(TypedDict):
    """Type hints for API configuration."""
    MODEL: str  # Default model for all API calls
    TEST_MODEL: str  # Model used in tests
    MAX_TOKENS: int
    MAX_TOKENS_TEST: int  # For testing API connectivity
    TEMPERATURE: float
    REQUIRED_FIELDS: List[str]
    EMAIL_ANALYSIS_PROMPT: str

class DatabaseConfig(TypedDict):
    """Type hints for database configuration."""
    EMAIL_DB_PATH: str
    ANALYSIS_DB_PATH: str
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
    BATCH_SIZE: int
    MAX_RETRIES: int
    RETRY_DELAY: int
    DAYS_TO_FETCH: int
    RATE_LIMIT: Dict[str, Union[int, float]]

class CatalogConfig(TypedDict):
    """Type hints for catalog configuration."""
    DB_PATH: str
    CHAT_LOG: str
    MATCH_THRESHOLD: float  # Threshold for semantic matching (0-1)
    POTENTIAL_MATCH_THRESHOLD: float  # Threshold for potential matches (0-1)
    TAG_MATCH_THRESHOLD: float  # Threshold for tag matching (0-1)
    RESULTS_PER_PAGE: int
    RELATIONSHIP_TYPES: List[str]
    TABLES: Dict[str, str]
    ENABLE_SEMANTIC: bool  # Toggle for semantic matching
    ERROR_MESSAGES: Dict[str, str]

class ErrorMessages(TypedDict):
    """Type hints for error message templates."""
    API_ERROR: str
    DATABASE_ERROR: str
    VALIDATION_ERROR: str
    JSON_DECODE_ERROR: str
    SEMANTIC_ERROR: str
    DUPLICATE_ERROR: str
    TAG_ERROR: str
    RELATIONSHIP_ERROR: str

# Database Configuration
DATABASE_CONFIG: DatabaseConfig = {
    'EMAIL_DB_PATH': os.path.join(DATA_DIR, 'db_email_store.db'),
    'ANALYSIS_DB_PATH': os.path.join(DATA_DIR, 'db_email_analysis.db'),
    'EMAIL_TABLE': 'emails',
    'ANALYSIS_TABLE': 'email_analysis',
}

# API Configuration
API_CONFIG: APIConfig = {
    'MODEL': DEFAULT_MODEL,
    'TEST_MODEL': DEFAULT_MODEL,
    'MAX_TOKENS': 4000,
    'MAX_TOKENS_TEST': 10,
    'TEMPERATURE': 0.0,  # Zero temperature for consistent outputs
    'REQUIRED_FIELDS': ['model', 'max_tokens', 'messages'],
    'EMAIL_ANALYSIS_PROMPT': '''Analyze the following email and provide a structured analysis in JSON format. Focus on:
1. Brief summary (2-3 sentences)
2. Category (list: work, personal, finance, etc.)
3. Priority (score 1-5, with reason)
4. Action needed (boolean, with type and deadline if true)
5. Key points (list)
6. People mentioned (list)
7. Project/topic classification
8. Sentiment (positive/negative/neutral)
9. Confidence score (0-1)

Email:
{email_content}

Respond with ONLY a JSON object containing these fields:
{
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
}'''
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
    'COUNT': 100,
    'BATCH_SIZE': 15,
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 5,
    'DAYS_TO_FETCH': 7,
    'RATE_LIMIT': {
        'REQUESTS_PER_MINUTE': 45,
        'PAUSE_SECONDS': 20
    }
}

# Error Messages
ERROR_MESSAGES: ErrorMessages = {
    'API_ERROR': 'Error calling Anthropic API: {error}',
    'DATABASE_ERROR': 'Error accessing database: {error}',
    'VALIDATION_ERROR': 'Error validating response: {error}',
    'JSON_DECODE_ERROR': 'Error decoding JSON response: {error}',
    'SEMANTIC_ERROR': 'Error in semantic analysis: {error}',
    'DUPLICATE_ERROR': 'Item with similar title already exists: {title}',
    'TAG_ERROR': 'Error managing tags: {error}',
    'RELATIONSHIP_ERROR': 'Error managing relationships: {error}'
}

# Catalog Configuration
CATALOG_CONFIG: CatalogConfig = {
    'DB_PATH': os.path.join(DATA_DIR, 'db_catalog.db'),
    'CHAT_LOG': 'chat_logs.jsonl',
    'MATCH_THRESHOLD': 0.85,  # High threshold for near-identical content
    'POTENTIAL_MATCH_THRESHOLD': 0.70,  # Moderate threshold for semantically related content
    'TAG_MATCH_THRESHOLD': 0.75,  # Threshold for tag matching
    'RESULTS_PER_PAGE': 10,
    'RELATIONSHIP_TYPES': [
        'contains',
        'references',
        'implements',
        'extends',
        'uses',
        'related_to'
    ],
    'TABLES': {
        'ITEMS': 'catalog_items',
        'RELATIONSHIPS': 'catalog_relationships',
        'TAGS': 'catalog_tags',
        'ITEM_TAGS': 'catalog_item_tags',
        'CHAT_HISTORY': 'chat_history'
    },
    'ENABLE_SEMANTIC': True,
    'ERROR_MESSAGES': {
        'DUPLICATE_ERROR': "Similar item already exists with title '{title}'",
        'POTENTIAL_MATCH_WARNING': "Found potentially similar items:\n{matches}\nUse force=True to add anyway.",
        'INVALID_TITLE': "Title cannot be empty",
        'INVALID_RELATIONSHIP': "Invalid relationship type. Must be one of: {valid_types}",
        'ITEM_NOT_FOUND': "Item not found: {title}",
        'ARCHIVED_ACCESS': "Cannot modify archived item: {title}",
        'SEMANTIC_MATCH_DETAILS': "Similarity score: {score:.2f}\nReason: {reason}"
    },
}

# Metrics Configuration
METRICS_CONFIG: MetricsConfig = {
    'METRICS_PORT': 8000
}
