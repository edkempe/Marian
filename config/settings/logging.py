"""Logging settings configuration."""

import os
from typing import Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings
from enum import Enum
from pathlib import Path

class LogLevel(str, Enum):
    """Valid log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LoggingSettings(BaseSettings):
    """Logging configuration with validation."""
    
    # Log directory
    LOG_DIR: Path = Field(
        default=Path("logs"),
        description="Directory for log files"
    )
    
    # Log files
    APP_LOG: str = Field(
        default="app.log",
        description="Main application log file"
    )
    ERROR_LOG: str = Field(
        default="error.log",
        description="Error log file"
    )
    ACCESS_LOG: str = Field(
        default="access.log",
        description="Access log file"
    )
    
    # Log levels
    DEFAULT_LEVEL: LogLevel = Field(
        default=LogLevel.INFO,
        description="Default logging level"
    )
    CONSOLE_LEVEL: LogLevel = Field(
        default=LogLevel.INFO,
        description="Console logging level"
    )
    FILE_LEVEL: LogLevel = Field(
        default=LogLevel.DEBUG,
        description="File logging level"
    )
    
    # Log rotation
    MAX_BYTES: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum log file size in bytes",
        ge=1024
    )
    BACKUP_COUNT: int = Field(
        default=5,
        description="Number of backup files to keep",
        ge=0
    )
    
    # Log formats
    CONSOLE_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Console log format"
    )
    FILE_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
        description="File log format"
    )
    DATE_FORMAT: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Log date format"
    )
    
    # Performance logging
    LOG_SLOW_QUERIES: bool = Field(
        default=True,
        description="Log slow database queries"
    )
    SLOW_QUERY_THRESHOLD: float = Field(
        default=1.0,
        description="Slow query threshold in seconds",
        ge=0
    )
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "LOG_"
        case_sensitive = True
        env_file = ".env"

# Create settings instance
logging_settings = LoggingSettings()
