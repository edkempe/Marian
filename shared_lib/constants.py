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
    - EMAIL: Email processing parameters
    - METRICS: Prometheus metrics settings
    - SESSION: Session management settings

Usage:
    from shared_lib.constants import API_CONFIG, DATABASE_CONFIG
    
    model = API_CONFIG['MODEL']
    db_path = DATABASE_CONFIG['EMAIL_DB_PATH']
"""

from typing import Dict, List, Union, TypedDict, Any
import os

# Shared Constants
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
DOCS_DIR = os.path.join(ROOT_DIR, 'docs')
SESSION_LOGS_DIR = os.path.join(DOCS_DIR, 'session_logs')
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
CACHE_DIR = os.path.join(ROOT_DIR, 'cache')

# Create directories if they don't exist
for dir_path in [DATA_DIR, DOCS_DIR, SESSION_LOGS_DIR, LOGS_DIR, CACHE_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

class APIConfig(TypedDict):
    """Type hints for API configuration."""
    MODEL: str
    TEST_MODEL: str
    MAX_TOKENS: int
    MAX_TOKENS_TEST: int
    TEMPERATURE: float
    REQUIRED_FIELDS: List[str]
    EMAIL_ANALYSIS_PROMPT: Dict[str, str]

class DatabaseConfig(TypedDict):
    """Type hints for database configuration."""
    EMAIL_DB_PATH: str
    ANALYSIS_DB_PATH: str
    EMAIL_DB_URL: str
    ANALYSIS_DB_URL: str
    EMAIL_TABLE: str
    ANALYSIS_TABLE: str
    email: Dict[str, str]
    analysis: Dict[str, str]
    catalog: Dict[str, str]
    session: Dict[str, str]

class MetricsConfig(TypedDict):
    """Type hints for metrics configuration."""
    PORT: int
    HOST: str
    ENABLED: bool
    METRICS_PORT: int

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
    DAYS_TO_FETCH: int

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

class TestingConfig(TypedDict):
    """Type hints for testing configuration."""
    EXCLUDED_DIRS: List[str]
    REQUIRED_VERSIONING: List[str]

class SessionConfig(TypedDict):
    """Type hints for session configuration."""
    MIN_PYTHON_VERSION: tuple
    DATE_FORMAT: str
    TIME_FORMAT: str
    TIME_ZONE_FORMAT: str
    GIT_COMMITS_TO_CHECK: int
    TEST_PATH: str
    REQUIREMENTS_FILE: str
    CONFIG_FILE_PATTERNS: List[str]
    SESSION_LOG_PREFIX: str
    VENV_DIR: str

# Database Column Sizes
COLUMN_SIZES = {
    'EMAIL_LABELS': 150,
    'GMAIL_LABEL_ID': 30,
    'GMAIL_LABEL_NAME': 100,
}

# Default Values
DEFAULT_VALUES = {
    'EMAIL_SUBJECT': 'No Subject',
    'API_RESPONSE': '{}',
    'HAS_ATTACHMENTS': '0',
    'EMPTY_STRING': '',
    'ACTION_NEEDED': False,
    'CONFIDENCE_SCORE': 0.9,
}

# Validation Constraints
VALIDATION = {
    'PRIORITY_SCORE': {
        'MIN': 1,
        'MAX': 5,
    },
    'CONFIDENCE_SCORE': {
        'MIN': 0.0,
        'MAX': 1.0,
    },
    'TEXT_LENGTH': {
        'MIN': 1,
        'MAX': 500,
    },
}

# Asset Types
class AssetTypes:
    """Valid asset types for the catalog."""
    CODE = 'code'
    DOCUMENT = 'document'
    TEST = 'test'
    CONFIG = 'config'
    SCRIPT = 'script'
    
    @classmethod
    def values(cls) -> List[str]:
        """Return all valid asset types."""
        return [cls.CODE, cls.DOCUMENT, cls.TEST, cls.CONFIG, cls.SCRIPT]

# Sentiment Values
class SentimentTypes:
    """Valid sentiment types for analysis."""
    POSITIVE = 'positive'
    NEGATIVE = 'negative'
    NEUTRAL = 'neutral'
    
    @classmethod
    def values(cls) -> List[str]:
        """Return all valid sentiment types."""
        return [cls.POSITIVE, cls.NEGATIVE, cls.NEUTRAL]

# Date Patterns
DATE_PATTERNS = {
    'ISO_DATE': r'^\d{4}-\d{2}-\d{2}$',
    'ISO_DATE_OR_EMPTY': r'^\d{4}-\d{2}-\d{2}$|^$',
    'ISO_DATE_OR_EMPTY_OR_ASAP': r'^\d{4}-\d{2}-\d{2}$|^$|^ASAP$',
}

# Email Configuration
EMAIL_CONFIG: EmailConfig = {
    'COUNT': 100,  # Number of emails to process at once
    'BATCH_SIZE': 10,  # Number of emails per API batch request
    'MAX_RETRIES': 3,  # Maximum number of retries for failed requests
    'RETRY_DELAY': 5,  # Delay between retries in seconds
    'LABELS': ['INBOX', 'SENT'],  # Labels to process
    'EXCLUDED_LABELS': ['SPAM', 'TRASH'],  # Labels to exclude
    'DAYS_TO_FETCH': 30  # Number of days of emails to fetch
}

# Database Configuration
DATABASE_CONFIG: DatabaseConfig = {
    'email': {
        'path': 'data/email.db',
        'url': None
    },
    'analysis': {
        'path': 'data/analysis.db',
        'url': None
    },
    'catalog': {
        'path': 'data/catalog.db',
        'url': None
    }
}

# API Configuration
API_CONFIG: APIConfig = {
    'MODEL': 'claude-3-opus-20240229',  # Main production model
    'TEST_MODEL': 'claude-3-haiku-20240307',  # Use Haiku for faster testing
    'MAX_TOKENS': 4000,
    'MAX_TOKENS_TEST': 1000,  # Reduced tokens for testing
    'TEMPERATURE': 0.0,  # Zero temperature for consistent outputs
    'REQUIRED_FIELDS': ['model', 'max_tokens', 'messages'],
    'EMAIL_ANALYSIS_PROMPT': {
        'claude-3-opus-20240229': '''Analyze the following email and provide a structured response in JSON format:

{email_content}

Provide a JSON response with the following fields:
{
    "summary": "Brief 1-2 sentence summary of the email",
    "category": ["List of categories that apply"],
    "priority_score": "Number from 1-5 indicating urgency/importance (1=lowest, 5=highest)",
    "priority_reason": "Brief explanation of the priority score",
    "action_needed": true/false,
    "action_type": ["List of required actions"],
    "action_deadline": "YYYY-MM-DD or ASAP or null if no deadline",
    "key_points": ["List of main points from the email"],
    "people_mentioned": ["List of people mentioned"],
    "project": "Project name or empty string",
    "topic": "Topic or empty string",
    "sentiment": "positive, negative, or neutral",
    "confidence_score": "Number between 0.0 and 1.0"
}''',
        'claude-3-haiku-20240307': '''Analyze this email and provide a JSON response:

{email_content}

Return a JSON object with these fields:
- summary: Brief summary
- category: List of categories that apply
- priority_score: Number 1-5 (1=lowest)
- priority_reason: Brief reason
- action_needed: true/false
- action_type: List of required actions
- action_deadline: YYYY-MM-DD or ASAP or null if no deadline
- key_points: Top 2-3 points
- people_mentioned: List of people mentioned
- project: Project name or empty string
- topic: Topic or empty string
- sentiment: positive/negative/neutral
- confidence_score: Number between 0.0 and 1.0'''
    }
}

# Default model for API calls
DEFAULT_MODEL = API_CONFIG['MODEL']  # Use the same model as defined in API_CONFIG

# Metrics Configuration
METRICS_CONFIG: MetricsConfig = {
    'PORT': 8125,  # Default StatsD port
    'HOST': 'localhost',
    'ENABLED': True,
    'METRICS_PORT': 8125  # Added for backward compatibility
}

# Logging Configuration
LOGGING_CONFIG: LoggingConfig = {
    'LOG_FILE': os.path.join(LOGS_DIR, 'marian.log'),
    'MAX_BYTES': 10485760,  # 10MB
    'BACKUP_COUNT': 5,
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'LOG_LEVEL': 'INFO'
}

# Session Management Constants
SESSION_CONFIG: SessionConfig = {
    'MIN_PYTHON_VERSION': (3, 12, 8),
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M',
    'TIME_ZONE_FORMAT': '%H:%M %Z',
    'GIT_COMMITS_TO_CHECK': 5,
    'TEST_PATH': 'tests/',
    'REQUIREMENTS_FILE': 'requirements.txt',
    'CONFIG_FILE_PATTERNS': ['*.ini', '*.cfg', '*.conf'],
    'SESSION_LOG_PREFIX': 'session_log_',
    'VENV_DIR': 'venv',
}

# Testing Configuration
TESTING_CONFIG: TestingConfig = {
    'EXCLUDED_DIRS': ['venv', '.git', '__pycache__', '.pytest_cache', 'build', 'dist'],
    'REQUIRED_VERSIONING': ['requirements.txt', 'setup.py']
}

# Catalog Configuration
CATALOG_CONFIG: CatalogConfig = {
    'DB_PATH': os.path.join(DATA_DIR, 'db_catalog.db'),
    'CHAT_LOG': 'chat_logs.jsonl',
    'MATCH_THRESHOLD': 0.85,  # High threshold for near-identical content
    'POTENTIAL_MATCH_THRESHOLD': 0.70,  # Lower threshold for potential matches
    'TAG_MATCH_THRESHOLD': 0.60,  # Threshold for tag matching
    'RESULTS_PER_PAGE': 10,
    'RELATIONSHIP_TYPES': ['similar', 'related', 'parent', 'child'],
    'TABLES': {
        'ENTRIES': 'catalog_entries',
        'RELATIONSHIPS': 'catalog_relationships',
        'TAGS': 'catalog_tags'
    },
    'ENABLE_SEMANTIC': True,
    'ERROR_MESSAGES': {
        'API_ERROR': 'Failed to get API response: {}',
        'DATABASE_ERROR': 'Database error: {}',
        'VALIDATION_ERROR': 'Invalid data: {}',
        'JSON_DECODE_ERROR': 'Failed to decode JSON: {}',
        'SEMANTIC_ERROR': 'Semantic matching error: {}',
        'DUPLICATE_ERROR': 'Duplicate entry: {}',
        'TAG_ERROR': 'Invalid tag: {}',
        'RELATIONSHIP_ERROR': 'Invalid relationship: {}'
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
