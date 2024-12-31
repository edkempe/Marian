"""Database settings configuration."""

import os
from typing import Dict, Optional
from enum import Enum

from pydantic import Field, PostgresDsn

from config.settings.base import Settings

class DatabaseType(str, Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"

class DatabaseSettings(Settings):
    """Database configuration with validation."""
    
    # Connection settings
    TYPE: DatabaseType = Field(
        default=DatabaseType.POSTGRESQL,
        description="Database type"
    )
    URL: PostgresDsn = Field(
        default="postgresql://user:pass@localhost:5432/db",
        description="Database connection URL"
    )
    
    # Connection pool
    MIN_CONNECTIONS: int = Field(
        default=5,
        description="Minimum number of connections",
        ge=1
    )
    MAX_CONNECTIONS: int = Field(
        default=20,
        description="Maximum number of connections",
        ge=5
    )
    CONNECTION_TIMEOUT: int = Field(
        default=30,
        description="Connection timeout in seconds",
        ge=1
    )
    
    # Query settings
    QUERY_TIMEOUT: int = Field(
        default=30,
        description="Query timeout in seconds",
        ge=1
    )
    MAX_QUERY_ROWS: int = Field(
        default=10000,
        description="Maximum rows per query",
        ge=1
    )
    
    # Migration settings
    AUTO_MIGRATE: bool = Field(
        default=True,
        description="Automatically run migrations on startup"
    )
    MIGRATION_TABLE: str = Field(
        default="alembic_version",
        description="Migration version table name"
    )
    
    # Backup settings
    BACKUP_ENABLED: bool = Field(
        default=True,
        description="Enable automated backups"
    )
    BACKUP_RETENTION_DAYS: int = Field(
        default=30,
        description="Number of days to retain backups",
        ge=1
    )
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "DB_"
        case_sensitive = True
        env_file = ".env"

# Create settings instance
db_settings = DatabaseSettings()
