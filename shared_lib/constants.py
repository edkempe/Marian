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
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
CACHE_DIR = os.path.join(ROOT_DIR, 'cache')

# Create directories if they don't exist
for dir_path in [DATA_DIR, LOGS_DIR, CACHE_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# Default API model
DEFAULT_MODEL = 'claude-3-haiku-20240307'  # Using haiku model

class APIConfig(TypedDict):
    """Type hints for API configuration."""
    MODEL: str
    TEST_MODEL: str
    MAX_TOKENS: int
    MAX_TOKENS_TEST: int
    TEMPERATURE: float
    REQUIRED_FIELDS: List[str]
    EMAIL_ANALYSIS_PROMPT: str

class DatabaseConfig(TypedDict):
    """Type hints for database configuration."""
    EMAIL_DB_PATH: str
    ANALYSIS_DB_PATH: str
    EMAIL_TABLE: str
    ANALYSIS_TABLE: str
    email: Dict[str, str]
    analysis: Dict[str, str]
    session: Dict[str, str]

class MetricsConfig(TypedDict):
    """Type hints for metrics configuration."""
    PORT: int
    HOST: str
    ENABLED: bool

class LoggingConfig(TypedDict):
    """Type hints for logging configuration."""
    LOG_FILE: str
    MAX_BYTES: int
    BACKUP_COUNT: int
    LOG_FORMAT: str
    LOG_LEVEL: str

class EmailConfig(TypedDict):
    """Type hints for email configuration."""
    COUNT: int
    BATCH_SIZE: int
    MAX_RETRIES: int
    RETRY_DELAY: int
    LABELS: List[str]
    EXCLUDED_LABELS: List[str]

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

# Email Configuration
EMAIL_CONFIG: EmailConfig = {
    'COUNT': 100,  # Number of emails to process at once
    'BATCH_SIZE': 10,  # Number of emails per API batch request
    'MAX_RETRIES': 3,  # Maximum number of retries for failed requests
    'RETRY_DELAY': 5,  # Delay between retries in seconds
    'LABELS': ['INBOX', 'SENT'],  # Labels to process
    'EXCLUDED_LABELS': ['SPAM', 'TRASH']  # Labels to exclude
}

# Database Configuration
DATABASE_CONFIG: DatabaseConfig = {
    'EMAIL_DB_PATH': os.path.join(DATA_DIR, 'db_email_store.db'),
    'ANALYSIS_DB_PATH': os.path.join(DATA_DIR, 'db_email_analysis.db'),
    'EMAIL_TABLE': 'emails',
    'ANALYSIS_TABLE': 'email_analysis',
    'email': {
        'path': os.path.join(DATA_DIR, 'db_email_store.db'),
        'table': 'emails',
        'test_path': ':memory:',
    },
    'analysis': {
        'path': os.path.join(DATA_DIR, 'db_email_analysis.db'),
        'table': 'email_analysis',
        'test_path': ':memory:',
    },
    'session': {
        'timeout': 300,  # Session timeout in seconds
        'retry_count': 3,  # Number of retries for failed connections
        'retry_delay': 5  # Delay between retries in seconds
    }
}

# API Configuration
API_CONFIG: APIConfig = {
    'MODEL': DEFAULT_MODEL,
    'TEST_MODEL': 'claude-3-haiku-20240307',  # Model used in tests
    'MAX_TOKENS': 4000,
    'MAX_TOKENS_TEST': 100,
    'TEMPERATURE': 0.0,  # Zero temperature for consistent outputs
    'REQUIRED_FIELDS': ['model', 'max_tokens', 'messages'],
    'EMAIL_ANALYSIS_PROMPT': '''You are an AI assistant that analyzes emails and returns structured data in JSON format. Your task is to analyze the following email and return a valid JSON object.

IMPORTANT: Your response must be a single, valid JSON object. Do not include any other text, explanations, or formatting.

Required Fields:
- summary (string): 2-3 sentence summary of the email
- category (array of strings): ["work", "personal", "finance", etc]
- priority_score (integer 1-5): urgency/importance score
- priority_reason (string): explanation for priority score
- action_needed (boolean): true if action required
- action_type (array of strings): ["review", "respond", "schedule", etc]
- action_deadline (string): "YYYY-MM-DD" or empty string
- key_points (array of strings): main points from email
- people_mentioned (array of strings): names mentioned
- project (string): project name or empty string
- topic (string): topic or empty string
- sentiment (string): "positive", "negative", or "neutral"
- confidence_score (float 0-1): confidence in analysis

Example Response Format:
{
    "summary": "Brief summary of email content",
    "category": ["work", "important"],
    "priority_score": 4,
    "priority_reason": "Urgent deadline approaching",
    "action_needed": true,
    "action_type": ["respond", "schedule"],
    "action_deadline": "2024-12-31",
    "key_points": ["Point 1", "Point 2"],
    "people_mentioned": ["John Smith", "Jane Doe"],
    "project": "Project Name",
    "topic": "Meeting",
    "sentiment": "positive",
    "confidence_score": 0.95
}
'''
}

# Metrics Configuration
METRICS_CONFIG: MetricsConfig = {
    'PORT': 8000,  # Port for metrics server
    'HOST': 'localhost',  # Host for metrics server
    'ENABLED': True  # Whether to enable metrics collection
}

# Logging Configuration
LOGGING_CONFIG: LoggingConfig = {
    'LOG_FILE': os.path.join(LOGS_DIR, 'marian.log'),
    'MAX_BYTES': 10485760,  # 10MB
    'BACKUP_COUNT': 5,
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'LOG_LEVEL': 'INFO'
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
