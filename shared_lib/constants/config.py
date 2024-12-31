"""Application configuration constants.

This module defines constants related to application configuration and settings.
These are different from runtime settings which should be in config/settings.py.
"""

from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path

@dataclass(frozen=True)
class ApplicationConfig:
    """Application-wide configuration constants."""
    
    # Application metadata
    APP_NAME: str = "Jexi"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "AI-powered email and document analysis"
    
    # Path configuration
    CONFIG_DIR: Path = Path("config")
    DATA_DIR: Path = Path("data")
    LOGS_DIR: Path = Path("logs")
    TEMP_DIR: Path = Path("temp")
    
    # File patterns
    CONFIG_PATTERNS: List[str] = [
        "*.yml",
        "*.yaml",
        "*.json",
        "*.toml",
        "*.ini",
        ".env*"
    ]
    
    # Environment names
    ENV_DEVELOPMENT: str = "development"
    ENV_STAGING: str = "staging"
    ENV_PRODUCTION: str = "production"
    ENV_TEST: str = "test"
    
    # Default timeouts (seconds)
    DEFAULT_TIMEOUT: int = 30
    LONG_TIMEOUT: int = 300
    
    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour
    MAX_CACHE_SIZE: int = 1000
    
    # Logging configuration
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    LOG_LEVELS: Dict[str, str] = {
        "development": "DEBUG",
        "staging": "INFO",
        "production": "WARNING",
        "test": "DEBUG"
    }
    
    # Session configuration
    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_TIMEOUT: int = 3600  # 1 hour
    
    # API configuration
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api"
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100

# Singleton instance
CONFIG = ApplicationConfig()
