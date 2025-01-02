"""Database configuration settings."""

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field, AnyUrl

from config.settings.base import Settings

# Get the absolute path to the data directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(ROOT_DIR, "data")

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
    
    # Main database path and URL
    DATABASE_PATH: Path = Path(DATA_DIR) / "jexi.db"
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"

    class Config:
        """Pydantic config."""
        env_prefix = "JEXI_"
        case_sensitive = False

# Create database settings instance
database_settings = DatabaseSettings()
