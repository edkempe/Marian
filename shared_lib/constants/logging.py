"""Logging configuration constants.

This module defines all logging-related constants used throughout the application.
"""

from dataclasses import dataclass, field
from typing import Dict
from pathlib import Path

@dataclass(frozen=True)
class LoggingConstants:
    """Logging configuration constants."""
    
    # Log file configuration
    LOG_DIR: Path = Path("logs")
    DEFAULT_LOG_FILE: str = "app.log"
    ERROR_LOG_FILE: str = "error.log"
    ACCESS_LOG_FILE: str = "access.log"
    
    # Log rotation
    MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT: int = 5
    
    # Log formats
    DEFAULT_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ERROR_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(exc_info)s"
    ACCESS_FORMAT: str = "%(asctime)s - %(remote_addr)s - %(request_method)s %(request_path)s"
    
    # Log levels by environment
    LOG_LEVELS: Dict[str, str] = field(default_factory=lambda: {
        "development": "DEBUG",
        "staging": "INFO",
        "production": "WARNING",
        "test": "DEBUG"
    })
    
    # Special loggers
    SECURITY_LOGGER: str = "security"
    API_LOGGER: str = "api"
    DB_LOGGER: str = "database"
    EMAIL_LOGGER: str = "email"
    
    # Performance logging
    SLOW_QUERY_THRESHOLD: float = 1.0  # seconds
    SLOW_REQUEST_THRESHOLD: float = 2.0  # seconds

# Singleton instance
LOGGING = LoggingConstants()
