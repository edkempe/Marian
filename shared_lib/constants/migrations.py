"""Database migration constants.

This module defines all migration-related constants used throughout the application.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set
from pathlib import Path

@dataclass(frozen=True)
class MigrationConstants:
    """Database migration constants."""
    
    # Migration directories
    MIGRATIONS_DIR: Path = Path("migrations")
    VERSIONS_DIR: Path = Path("migrations/versions")
    
    # Migration file patterns
    MIGRATION_FILE_PATTERN: str = r"^\d{14}_.+\.py$"
    MIGRATION_TEMPLATE: str = "migration_template.py.mako"
    
    # Migration table
    MIGRATION_TABLE: str = "alembic_version"
    
    # Migration settings
    BATCH_SIZE: int = 1000
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # seconds
    TIMEOUT: int = 300  # seconds
    
    # Migration types
    MIGRATION_TYPES: Set[str] = field(default_factory=lambda: {
        "schema",
        "data",
        "index",
        "constraint",
        "trigger"
    })
    
    # Dependencies
    REQUIRED_PACKAGES: Set[str] = field(default_factory=lambda: {
        "alembic",
        "sqlalchemy"
    })
    
    # Error messages
    ERROR_MESSAGES: Dict[str, str] = field(default_factory=lambda: {
        "missing_head": "Migration head is missing",
        "multiple_heads": "Multiple migration heads found",
        "invalid_revision": "Invalid migration revision",
        "failed_migration": "Migration failed: {error}",
        "invalid_type": "Invalid migration type",
        "missing_dependency": "Missing required dependency: {package}",
        "version_mismatch": "Version mismatch: expected {expected}, got {actual}",
        "timeout": "Migration timed out after {timeout} seconds"
    })
    
    # Validation rules
    MAX_MIGRATION_SIZE: int = 1000  # lines
    MAX_TABLE_NAME_LENGTH: int = 63
    MAX_COLUMN_NAME_LENGTH: int = 63
    RESERVED_KEYWORDS: Set[str] = field(default_factory=lambda: {
        "table",
        "column",
        "index",
        "constraint",
        "database",
        "schema"
    })

# Singleton instance
MIGRATIONS = MigrationConstants()
