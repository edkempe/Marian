"""Database configuration settings."""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field, AnyUrl

from config.settings.base import Settings


class DatabaseType(str, Enum):
    """Database type enumeration."""
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    MYSQL = "mysql"


class DatabaseSettings(Settings):
    """Database settings with comprehensive configuration."""
    
    # Core settings
    TYPE: DatabaseType = Field(
        default=DatabaseType.SQLITE,
        description="Database type"
    )
    ECHO_SQL: bool = Field(
        default=False,
        description="Echo SQL statements for debugging"
    )
    
    # Database URLs
    URL: AnyUrl = Field(
        default="sqlite:///data/default.db",
        description="Default database URL"
    )
    EMAIL_DB_URL: AnyUrl = Field(
        default="sqlite:///data/email.db",
        description="Email database URL"
    )
    ANALYSIS_DB_URL: AnyUrl = Field(
        default="sqlite:///data/analysis.db",
        description="Analysis database URL"
    )
    CATALOG_DB_URL: AnyUrl = Field(
        default="sqlite:///data/catalog.db",
        description="Catalog database URL"
    )
    
    # Connection Pool Settings
    MIN_CONNECTIONS: int = Field(
        default=5,
        description="Minimum database connections",
        ge=1
    )
    MAX_CONNECTIONS: int = Field(
        default=20,
        description="Maximum database connections",
        ge=1
    )
    CONNECTION_TIMEOUT: int = Field(
        default=30,
        description="Database connection timeout in seconds",
        ge=1
    )
    
    # Query Settings
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
    
    # Migration Settings
    MIGRATIONS_DIR: Path = Field(
        default=Path("migrations"),
        description="Database migrations directory"
    )
    AUTO_MIGRATE: bool = Field(
        default=True,
        description="Automatically run migrations on startup"
    )
    
    # SQLite-specific Settings
    SQLITE_PRAGMA: dict = Field(
        default={
            "journal_mode": "WAL",
            "cache_size": -64000,  # 64MB cache
            "foreign_keys": "ON",
            "synchronous": "NORMAL"
        },
        description="SQLite PRAGMA settings"
    )
    
    def __init__(self, **kwargs):
        """Initialize database settings and create data directory."""
        super().__init__(**kwargs)
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)


# Create database settings instance
database_settings = DatabaseSettings()
