"""Logging settings configuration."""

import os
from typing import Dict, Optional
from enum import Enum
from pathlib import Path

from pydantic import Field

from config.settings.base import Settings

class LogLevel(str, Enum):
    """Valid log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LoggingSettings(Settings):
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
    
    # Log format
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    DATE_FORMAT: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Log date format"
    )
    
    # Log rotation
    MAX_BYTES: int = Field(
        default=10_485_760,  # 10MB
        description="Maximum log file size in bytes",
        ge=1024
    )
    BACKUP_COUNT: int = Field(
        default=5,
        description="Number of backup files to keep",
        ge=0
    )
    
    # Performance
    ASYNC_LOGGING: bool = Field(
        default=True,
        description="Use asynchronous logging"
    )
    QUEUE_SIZE: int = Field(
        default=1000,
        description="Queue size for async logging",
        ge=100
    )
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "LOG_"
        case_sensitive = True
        env_file = ".env"

# Create settings instance
logging_settings = LoggingSettings()
