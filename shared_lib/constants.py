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
    - SESSION: Session management settings
    - PACKAGE_ALIASES: Package aliases and dependencies

Usage:
    from shared_lib.constants import API_CONFIG, DATABASE_CONFIG

    model = API_CONFIG['MODEL']
    db_path = DATABASE_CONFIG['EMAIL_DB_PATH']
"""

import os
from typing import Any, Dict, List, TypedDict, Union

# Shared Constants
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
SESSION_LOGS_DIR = os.path.join(DOCS_DIR, "session_logs")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
CACHE_DIR = os.path.join(ROOT_DIR, "cache")

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
    USER_ID: str
    DEFAULT_SUBJECT: str
    EMPTY_STRING: str


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
    TEST_DB_PATH: str
    TEST_EMAIL_DATA: Dict[str, str]
    TEST_EMAIL_COUNT: int


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
    "EMAIL_LABELS": 500,  # Maximum size for labels string
    "EMAIL_SUBJECT": 500,  # Maximum size for subject
    "EMAIL_SENDER": 200,  # Maximum size for sender
    "EMAIL_THREAD": 100,  # Maximum size for thread ID
    "EMAIL_TO": 200,  # Maximum size for recipient
    "EMAIL_ID": 100,  # Maximum size for Gmail message ID
}

# Analysis Constants
ANALYSIS_VALIDATION = {
    "PRIORITY_SCORE": {"MIN": 1, "MAX": 5},
    "TEXT_LENGTH": {"MIN": 1, "MAX": 10000},
    "CONFIDENCE_SCORE": {"MIN": 0.0, "MAX": 1.0},
}

ANALYSIS_DEFAULTS = {
    "ACTION_NEEDED": False,
    "EMPTY_STRING": "",
    "CONFIDENCE_SCORE": 0.8,
}

ANALYSIS_SENTIMENT_TYPES = {
    "POSITIVE": "positive",
    "NEGATIVE": "negative",
    "NEUTRAL": "neutral",
}

ANALYSIS_DATE_PATTERNS = {
    "ISO_DATE_OR_EMPTY": r"^(\d{4}-\d{2}-\d{2})?$",
    "ISO_DATE_OR_EMPTY_OR_ASAP": r"^(\d{4}-\d{2}-\d{2}|ASAP)?$",
}

# Default Values
DEFAULT_VALUES = {
    "EMAIL_SUBJECT": "No Subject",
    "API_RESPONSE": "{}",
    "HAS_ATTACHMENTS": "0",
    "ACTION_NEEDED": False,
    "CONFIDENCE_SCORE": 0.9,
}

# Validation Constraints
VALIDATION = {
    "PRIORITY_SCORE": {
        "MIN": 1,
        "MAX": 5,
    },
    "CONFIDENCE_SCORE": {
        "MIN": 0.0,
        "MAX": 1.0,
    },
    "TEXT_LENGTH": {
        "MIN": 1,
        "MAX": 500,
    },
}


# Asset Types
class AssetTypes:
    """Valid asset types for the catalog."""

    CODE = "code"
    DOCUMENT = "document"
    TEST = "test"
    CONFIG = "config"
    SCRIPT = "script"

    @classmethod
    def values(cls) -> List[str]:
        """Return all valid asset types."""
        return [cls.CODE, cls.DOCUMENT, cls.TEST, cls.CONFIG, cls.SCRIPT]


# Sentiment analysis constants
VALID_SENTIMENTS = {"POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"}

# Sentiment Values
class SentimentTypes:
    """Valid sentiment types for analysis."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

    @classmethod
    def values(cls) -> List[str]:
        """Return all valid sentiment types."""
        return [cls.POSITIVE, cls.NEGATIVE, cls.NEUTRAL]


# Regex Patterns
REGEX_PATTERNS = {
    "URL": r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
    "ISO_DATE": r"^\d{4}-\d{2}-\d{2}$",
    "ISO_DATE_OR_EMPTY": r"^\d{4}-\d{2}-\d{2}$|^$",
    "ISO_DATE_OR_EMPTY_OR_ASAP": r"^\d{4}-\d{2}-\d{2}$|^$|^ASAP$",
}

# Date Patterns
DATE_PATTERNS = REGEX_PATTERNS

# Email Configuration
EMAIL_CONFIG: EmailConfig = {
    "COUNT": 100,  # Default number of emails to fetch
    "BATCH_SIZE": 50,  # Number of emails to process in one batch
    "MAX_RETRIES": 3,  # Maximum number of retries for failed operations
    "RETRY_DELAY": 1,  # Delay between retries in seconds
    "LABELS": ["INBOX", "SENT", "IMPORTANT"],  # Default labels to fetch
    "EXCLUDED_LABELS": ["SPAM", "TRASH"],  # Labels to exclude
    "DAYS_TO_FETCH": 30,  # Default number of days to fetch
    "USER_ID": "me",  # Gmail API user ID
    "DEFAULT_SUBJECT": "No Subject",  # Default subject for emails without one
    "EMPTY_STRING": "",  # Default empty string value
}

# Database Configuration
DATABASE_CONFIG: DatabaseConfig = {
    "EMAIL_DB_PATH": os.path.join(ROOT_DIR, "db_email_store.db"),
    "ANALYSIS_DB_PATH": os.path.join(ROOT_DIR, "db_email_analysis.db"),
    "EMAIL_DB_URL": f"sqlite:///{os.path.join(ROOT_DIR, 'db_email_store.db')}",
    "ANALYSIS_DB_URL": f"sqlite:///{os.path.join(ROOT_DIR, 'db_email_analysis.db')}",
    "EMAIL_TABLE": "emails",
    "ANALYSIS_TABLE": "email_analysis",
    "email": {
        "path": os.path.join(ROOT_DIR, "db_email_store.db"),
        "url": f"sqlite:///{os.path.join(ROOT_DIR, 'db_email_store.db')}",
    },
    "analysis": {
        "path": os.path.join(ROOT_DIR, "db_email_analysis.db"),
        "url": f"sqlite:///{os.path.join(ROOT_DIR, 'db_email_analysis.db')}",
    },
    "catalog": {
        "path": os.path.join(ROOT_DIR, "db_catalog.db"),
        "url": f"sqlite:///{os.path.join(ROOT_DIR, 'db_catalog.db')}",
    },
}

# API Configuration
API_CONFIG: APIConfig = {
    "MODEL": "claude-3-haiku-20240307",  # Temporarily using Haiku for both
    "TEST_MODEL": "claude-3-haiku-20240307",  # Use Haiku for faster testing
    "MAX_TOKENS": 4000,
    "MAX_TOKENS_TEST": 1000,  # Reduced tokens for testing
    "TEMPERATURE": 0.0,  # Zero temperature for consistent outputs
    "REQUIRED_FIELDS": ["model", "max_tokens", "messages"],
    "EMAIL_ANALYSIS_PROMPT": {
        "claude-3-haiku-20240307": """Analyze this email and provide a JSON response:

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
- confidence_score: Number between 0.0 and 1.0

IMPORTANT: Return ONLY the JSON object without any additional text or explanation.""",
    },
}

# Default model for API calls
DEFAULT_MODEL = API_CONFIG["MODEL"]  # Use the same model as defined in API_CONFIG

# Logging Configuration
LOGGING_CONFIG: LoggingConfig = {
    "LOG_FILE": os.path.join(LOGS_DIR, "marian.log"),
    "MAX_BYTES": 10485760,  # 10MB
    "BACKUP_COUNT": 5,
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "LOG_LEVEL": "INFO",
}

# Session Management Constants
SESSION_CONFIG: SessionConfig = {
    "MIN_PYTHON_VERSION": (3, 12, 8),
    "DATE_FORMAT": "%Y-%m-%d",
    "TIME_FORMAT": "%H:%M",
    "TIME_ZONE_FORMAT": "%H:%M %Z",
    "GIT_COMMITS_TO_CHECK": 5,
    "TEST_PATH": "tests/",
    "REQUIREMENTS_FILE": "requirements.txt",
    "CONFIG_FILE_PATTERNS": ["*.ini", "*.cfg", "*.conf"],
    "SESSION_LOG_PREFIX": "session_log_",
    "VENV_DIR": "venv",
}

# Testing Configuration
TESTING_CONFIG: TestingConfig = {
    "EXCLUDED_DIRS": ["venv", ".git", "__pycache__", ".pytest_cache", "build", "dist"],
    "REQUIRED_VERSIONING": [],  # Version info is in package versions and setup() function
    "TEST_DB_PATH": os.path.join(ROOT_DIR, "data", "test_email.db"),
    "TEST_EMAIL_DATA": {
        "id": "test1",
        "thread_id": "thread1",
        "subject": "Test Subject",
        "from_": "from@test.com",
        "to": "to@test.com",
        "body": "Test content",
    },
    "TEST_EMAIL_COUNT": 3,
}

# Catalog Configuration
CATALOG_CONFIG: CatalogConfig = {
    "DB_PATH": os.path.join(DATA_DIR, "db_catalog.db"),
    "CHAT_LOG": "chat_logs.jsonl",
    "MATCH_THRESHOLD": 0.85,  # High threshold for near-identical content
    "POTENTIAL_MATCH_THRESHOLD": 0.70,  # Lower threshold for potential matches
    "TAG_MATCH_THRESHOLD": 0.60,  # Threshold for tag matching
    "RESULTS_PER_PAGE": 10,
    "RELATIONSHIP_TYPES": ["similar", "related", "parent", "child"],
    "TABLES": {
        "ENTRIES": "catalog_entries",
        "RELATIONSHIPS": "catalog_relationships",
        "TAGS": "catalog_tags",
    },
    "ENABLE_SEMANTIC": True,
    "ERROR_MESSAGES": {
        "API_ERROR": "Failed to get API response: {}",
        "DATABASE_ERROR": "Database error: {}",
        "VALIDATION_ERROR": "Invalid data: {}",
        "JSON_DECODE_ERROR": "Failed to decode JSON: {}",
        "SEMANTIC_ERROR": "Semantic matching error: {}",
        "DUPLICATE_ERROR": "Duplicate entry: {}",
        "TAG_ERROR": "Invalid tag: {}",
        "RELATIONSHIP_ERROR": "Invalid relationship: {}",
    },
}

# Error Messages
ERROR_MESSAGES: ErrorMessages = {
    "API_ERROR": "Error calling Anthropic API: {error}",
    "DATABASE_ERROR": "Error accessing database: {error}",
    "VALIDATION_ERROR": "Error validating response: {error}",
    "JSON_DECODE_ERROR": "Error decoding JSON response: {error}",
    "SEMANTIC_ERROR": "Error in semantic analysis: {error}",
    "DUPLICATE_ERROR": "Item with similar title already exists: {title}",
    "TAG_ERROR": "Error managing tags: {error}",
    "RELATIONSHIP_ERROR": "Error managing relationships: {error}",
}

# Package Aliases and Dependencies
PACKAGE_ALIASES = {
    "google": "google-api-python-client",
    "google_auth_oauthlib": "google-auth-oauthlib",
    "googleapiclient": "google-api-python-client",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
    "jose": "python-jose",
    "pandas": "pandas",
    "plotly": "plotly",
    "pre_commit": "pre-commit",
    "pytest": "pytest",
    "pytest_cov": "pytest-cov",
    "pytest_mock": "pytest-mock",
    "python_dateutil": "python-dateutil",
    "python_dotenv": "python-dotenv",
    "python_jose": "python-jose",
    "pytz": "pytz",
    "setuptools": "setuptools",
    "sqlalchemy": "sqlalchemy",
    "structlog": "structlog",
    "tabulate": "tabulate",
    "tenacity": "tenacity",
    "textblob": "textblob",
    "tqdm": "tqdm",
}

DEV_DEPENDENCIES = {
    "alembic",  # Database migrations
    "anthropic",  # AI API client
    "bandit",  # Security testing
    "boto3",  # AWS SDK
    "botocore",  # AWS SDK core
    "cryptography",  # Security utilities
    "factory-boy",  # Test data generation
    "google-auth-httplib2",  # Google API client
    "jinja2",  # Template engine
    "markdown",  # Markdown processing
    "networkx",  # Graph processing
    "numpy",  # Numerical processing
    "pandas",  # Data analysis
    "passlib",  # Password hashing
    "plotly",  # Data visualization
    "pre-commit",  # Pre-commit hooks
    "prompt-toolkit",  # Interactive prompts
    "pydantic",  # Data validation
    "pytest",  # Testing framework
    "pytest-asyncio",  # Async test support
    "pytest-cov",  # Test coverage
    "pytest-mock",  # Test mocking
    "python-dateutil",  # Date utilities
    "python-dotenv",  # Environment variables
    "python-jose",  # JWT utilities
    "pytz",  # Timezone utilities
    "setuptools",  # Build utilities
    "sqlalchemy",  # ORM
    "structlog",  # Structured logging
    "tabulate",  # Table formatting
    "tenacity",  # Retry utilities
    "textblob",  # Text processing
    "tqdm",  # Progress bars
}

LOCAL_MODULES = [
    "app_api_client",
    "app_catalog",
    "app_email_analyzer",
    "app_email_reports",
    "app_email_self_log",
    "app_get_mail",
    "app_label_manager",
    "app_main",
    "app_reports",
    "app_search",
    "app_sync",
    "app_utils",
    "models",
    "shared_lib",
    "tests",
]

# Special import patterns to ignore
SPECIAL_IMPORTS = [
    r"^from\s+google\.oauth2",  # Special case for google-api-python-client
    r"^from\s+google_auth_oauthlib",  # Special case for google-auth-oauthlib
    r"^from\s+googleapiclient",  # Special case for google-api-python-client
]

# Import patterns for requirements analysis
IMPORT_PATTERNS = [
    r"^import\s+os",  # Standard library imports
    r"^import\s+sys",
    r"^import\s+json",
    r"^import\s+logging",
    r"^import\s+datetime",
    r"^import\s+time",
    r"^import\s+typing",
    r"^import\s+re",
    r"^import\s+pathlib",
    r"^import\s+sqlite3",
    r"^import\s+base64",
    r"^import\s+email",
    r"^import\s+mimetypes",
    r"^import\s+pickle",
    r"^import\s+uuid",
    r"^from\s+datetime\s+import",
    r"^from\s+typing\s+import",
    r"^from\s+pathlib\s+import",
    r"^from\s+email\s+import",
    r"^from\s+base64\s+import",
    r"^from\s+google\.oauth2",  # Special case for google-api-python-client
    r"^from\s+google_auth_oauthlib",  # Special case for google-auth-oauthlib
    r"^from\s+googleapiclient",  # Special case for google-api-python-client
]
