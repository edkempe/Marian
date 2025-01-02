"""Configuration constants."""

from dataclasses import dataclass, field
from typing import Dict, Any, Set
from pathlib import Path

@dataclass(frozen=True)
class ConfigConstants:
    """Configuration constants.
    
    This class serves as a central configuration store for the entire application.
    It includes settings for databases, logging, caching, security, and features.
    The configuration is immutable (frozen) to prevent accidental modifications.
    """

    # Development dependencies
    DEV_DEPENDENCIES: Set[str] = field(default_factory=lambda: {
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "black",
        "isort",
        "mypy",
        "pylint"
    })

    # Database configuration
    DATABASE: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        # Default database for general application data
        "default": {
            "type": "sqlite",  # Database type (sqlite, postgres, etc.)
            "url": "sqlite:///data/default.db",  # SQLAlchemy connection URL
            "DB_PATH": "data/default.db",  # File path for SQLite database
            "min_connections": 1,  # Minimum number of connections in pool
            "max_connections": 5,  # Maximum number of connections in pool
            "connection_timeout": 30,  # Connection timeout in seconds
            "query_timeout": 30,  # Query execution timeout in seconds
            "max_query_rows": 10000,  # Maximum rows to return in a query
            "auto_migrate": True,  # Automatically run migrations on startup
            "migrations_dir": "migrations",  # Directory containing migrations
        },
        # Email-specific database configuration
        "email": {
            "type": "sqlite",
            "url": "sqlite:///data/email.db",
            "DB_PATH": "data/email.db",
            "min_connections": 1,
            "max_connections": 5,
            "connection_timeout": 30,
            "query_timeout": 30,
            "max_query_rows": 10000,
            "auto_migrate": True,
            "migrations_dir": "migrations/email",
            "batch_size": 50,  # Number of emails to process in one batch
            "max_retries": 3,  # Maximum retry attempts for failed operations
            "smtp_host": "smtp.gmail.com",  # SMTP server for sending emails
            "smtp_port": 587,  # SMTP port (587 for TLS)
            "imap_host": "imap.gmail.com",  # IMAP server for receiving emails
            "imap_port": 993,  # IMAP port (993 for SSL)
        },
        # Analysis database for storing email analysis results
        "analysis": {
            "type": "sqlite",
            "url": "sqlite:///data/analysis.db",
            "DB_PATH": "data/analysis.db",
            "min_connections": 1,
            "max_connections": 5,
            "connection_timeout": 30,
            "query_timeout": 30,
            "max_query_rows": 10000,
            "auto_migrate": True,
            "migrations_dir": "migrations/analysis",
        },
        # Catalog database for storing document metadata and search indices
        "catalog": {
            "type": "sqlite",
            "url": "sqlite:///data/catalog.db",
            "DB_PATH": "data/catalog.db",
            "CHAT_LOG": "data/catalog/chat_log.db",  # Chat history database
            "min_connections": 1,
            "max_connections": 5,
            "connection_timeout": 30,
            "query_timeout": 30,
            "max_query_rows": 10000,
            "auto_migrate": True,
            "migrations_dir": "migrations/catalog",
            "index_dir": "data/catalog/index",  # Directory for search indices
            "cache_dir": "data/catalog/cache",  # Directory for caching
            "max_size": 1024 * 1024 * 1024,  # Maximum catalog size (1GB)
            "chunk_size": 1000,  # Size of chunks for processing
        },
    })

    # Logging configuration
    LOGGING: Dict[str, Any] = field(default_factory=lambda: {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/app.log",
        "max_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5,
    })

    # Cache configuration
    CACHE: Dict[str, Any] = field(default_factory=lambda: {
        "type": "redis",
        "url": "redis://localhost:6379/0",
        "ttl": 3600,
        "max_size": 1000,
    })

    # Security settings
    SECURITY: Dict[str, Any] = field(default_factory=lambda: {
        "secret_key": "your-secret-key",
        "token_expiry": 3600,
        "max_attempts": 3,
        "lockout_time": 300,
    })

    # Feature flags
    FEATURES: Dict[str, bool] = field(default_factory=lambda: {
        "enable_cache": True,
        "enable_auth": True,
        "enable_rate_limit": True,
        "enable_monitoring": True,
    })

    # Session configuration
    SESSION: Dict[str, Any] = field(default_factory=lambda: {
        "timeout": 30,  # seconds
        "max_size": 1000,  # maximum number of sessions
        "cleanup_interval": 300,  # cleanup every 5 minutes
    })

    # Valid sentiment values
    VALID_SENTIMENTS: Set[str] = field(default_factory=lambda: {
        "positive",
        "negative",
        "neutral",
        "mixed"
    })

    def __getitem__(self, key: str) -> Any:
        """Access configuration values using dictionary-style access.
        
        This method allows accessing configuration values using square bracket notation,
        e.g., CONFIG["EMAIL"] or CONFIG["CATALOG"]. It provides backward compatibility
        for code that expects EMAIL and CATALOG as top-level keys.
        
        Args:
            key: The configuration key to access. Can be a direct attribute name
                 or one of the special keys: "EMAIL" or "CATALOG"
        
        Returns:
            The configuration value associated with the key
            
        Raises:
            KeyError: If the key is not found in the configuration
        """
        if key in self.__dict__:
            return getattr(self, key)
        elif key == "EMAIL":
            return self.DATABASE["email"]
        elif key == "CATALOG":
            return self.DATABASE["catalog"]
        raise KeyError(f"Configuration key not found: {key}")

# Singleton instance
CONFIG = ConfigConstants()
