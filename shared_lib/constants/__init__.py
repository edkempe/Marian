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
    )

Note:
    This is the public interface for constants. Individual modules should
    import from this package rather than directly from the constant modules.
"""

from shared_lib.constants.api import *
from shared_lib.constants.base import *
from shared_lib.constants.config import CONFIG
from shared_lib.constants.database import *
from shared_lib.constants.documentation import STANDARDS as DOCUMENTATION
from shared_lib.constants.email import EMAIL
from shared_lib.constants.file import *
from shared_lib.constants.logging import LOGGING
from shared_lib.constants.migrations import MIGRATIONS
from shared_lib.constants.security import *
from shared_lib.constants.testing import *
from shared_lib.constants.validation import RULES as VALIDATION_RULES, ERRORS as VALIDATION_ERRORS
from shared_lib.constants.versioning import VERSIONING

__all__ = [
    'API',
    'CONFIG',
    'DATABASE',
    'DOCUMENTATION',
    'EMAIL',
    'FILE',
    'LOGGING',
    'MIGRATIONS',
    'SECURITY',
    'TESTING',
    'VALIDATION_RULES',
    'VALIDATION_ERRORS',
    'VERSIONING',
]
