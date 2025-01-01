"""Constants package for the Marian project.

This package provides a centralized, hierarchical structure for all constants
used throughout the project. Constants are organized by domain and purpose
to maintain clarity and prevent duplication.

Usage:
    from shared_lib.constants import (
        API,           # API-related constants
        CONFIG,        # Application configuration
        DATABASE,      # Database constants
        DOCUMENTATION, # Documentation standards
        EMAIL,         # Email operations
        FILE,          # File operation constants
        LOGGING,       # Logging configuration
        MIGRATIONS,    # Database migrations
        SECURITY,      # Security-related constants
        TESTING,       # Testing constants
        VALIDATION,    # Validation rules and messages
        VERSIONING,    # API and DB versioning
        COLUMN_SIZES,  # Column sizes for database tables
        IMPORT_PATTERNS, # Import patterns for code analysis
        REQUIRED_DOCS,  # Required documentation sections
        DEFAULT_MODEL,  # Default model
        LOCAL_MODULES,  # Local modules for import validation
        PACKAGE_ALIASES, # Package aliases for requirements
        ErrorMessages,   # Error messages
        REGEX_PATTERNS,  # Regular expression patterns
        SentimentTypes,  # Sentiment types
    )

Note:
    This is the public interface for constants. Individual modules should
    import from this package rather than directly from the constant modules.
"""

from shared_lib.constants.api import API, API_CONFIG
from shared_lib.constants.base import BASE
from shared_lib.constants.config import CONFIG
from shared_lib.constants.database import DATABASE_CONFIG
from shared_lib.constants.documentation import STANDARDS as DOCUMENTATION
from shared_lib.constants.email import EMAIL
from shared_lib.constants.file import FILE
from shared_lib.constants.logging import LOGGING
from shared_lib.constants.migrations import MIGRATIONS
from shared_lib.constants.security import SECURITY
from shared_lib.constants.testing import TESTING_CONFIG
from shared_lib.constants.validation import RULES as VALIDATION_RULES, ERRORS as VALIDATION_ERRORS
from shared_lib.constants.versioning import VERSIONING
from shared_lib.constants.errors import ErrorMessages
from shared_lib.constants.regex_patterns import REGEX_PATTERNS
from shared_lib.constants.sentiment_types import SentimentTypes
from pathlib import Path

# Re-export for backward compatibility
CATALOG_CONFIG = CONFIG.DATABASE["catalog"]
DATABASE_CONFIG = CONFIG.DATABASE
EMAIL_CONFIG = CONFIG.DATABASE["email"]
LOGGING_CONFIG = CONFIG.LOGGING
ROOT_DIR = FILE.ROOT_DIR
DOCS_DIR = FILE.DOCS_DIR
CACHE_DIR = FILE.CACHE_DIR
SESSION_LOGS_DIR = FILE.SESSION_LOGS_DIR
DEV_DEPENDENCIES = CONFIG.DEV_DEPENDENCIES
VALID_SENTIMENTS = EMAIL.VALID_SENTIMENTS

# Additional constants
COLUMN_SIZES = {
    "tiny": 32,
    "small": 64,
    "medium": 128,
    "large": 256,
    "xlarge": 512,
    "huge": 1024,
}

IMPORT_PATTERNS = {
    "stdlib": r"^(?:(?!\\.|_)[a-zA-Z][a-zA-Z0-9_]*)+$",
    "local": r"^(?:(?:\\.)?[a-zA-Z][a-zA-Z0-9_]*)+$",
    "third_party": r"^(?:[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9])+$",
}

REQUIRED_DOCS = {
    "Overview": ["Purpose", "Features"],
    "Installation": ["Requirements", "Setup"],
    "Usage": ["Basic", "Advanced"],
    "Development": ["Testing", "Contributing"],
}

DEFAULT_MODEL = "gpt-4"

LOCAL_MODULES = {
    "src",
    "tests",
    "tools",
    "shared_lib",
    "scripts",
    "config",
}

PACKAGE_ALIASES = {
    "pytest-cov": "pytest_cov",
    "python-dotenv": "dotenv",
    "sqlalchemy-utils": "sqlalchemy_utils",
    "python-dateutil": "dateutil",
}

DATA_DIR = str(Path.cwd() / "data")  # Use absolute path

REQUIRED_SECTIONS = DOCUMENTATION.REQUIRED_SECTIONS

__all__ = [
    'API',
    'API_CONFIG',
    'BASE',
    'CONFIG',
    'DATABASE_CONFIG',
    'DOCUMENTATION',
    'EMAIL',
    'EMAIL_CONFIG',
    'FILE',
    'LOGGING',
    'LOGGING_CONFIG',
    'MIGRATIONS',
    'SECURITY',
    'TESTING_CONFIG',
    'VALIDATION_RULES',
    'VALIDATION_ERRORS',
    'VERSIONING',
    'ErrorMessages',
    'REGEX_PATTERNS',
    'SentimentTypes',
    # Re-exported constants
    'CATALOG_CONFIG',
    'ROOT_DIR',
    'DOCS_DIR',
    'CACHE_DIR',
    'SESSION_LOGS_DIR',
    'DEV_DEPENDENCIES',
    'VALID_SENTIMENTS',
    # Additional constants
    'COLUMN_SIZES',
    'IMPORT_PATTERNS',
    'REQUIRED_DOCS',
    'DEFAULT_MODEL',
    'LOCAL_MODULES',
    'PACKAGE_ALIASES',
    'DATA_DIR',
    'REQUIRED_SECTIONS'
]
