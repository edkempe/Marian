"""Database constants."""

from typing import Dict, Any
from config.settings.database import database_settings

def _get_database_config() -> Dict[str, Any]:
    """Get database configuration from settings."""
    return {
        "type": database_settings.TYPE,
        "echo_sql": database_settings.ECHO_SQL,
        "url": str(database_settings.URL),
        "email_db_url": str(database_settings.EMAIL_DB_URL),
        "analysis_db_url": str(database_settings.ANALYSIS_DB_URL),
        "catalog_db_url": str(database_settings.CATALOG_DB_URL),
        "min_connections": database_settings.MIN_CONNECTIONS,
        "max_connections": database_settings.MAX_CONNECTIONS,
        "pool_size": database_settings.POOL_SIZE,
        "max_overflow": database_settings.MAX_OVERFLOW,
        "pool_timeout": database_settings.POOL_TIMEOUT,
        "pool_recycle": database_settings.POOL_RECYCLE,
        "statement_timeout": database_settings.STATEMENT_TIMEOUT,
        "idle_timeout": database_settings.IDLE_IN_TRANSACTION_SESSION_TIMEOUT,
        "sqlite_pragmas": database_settings.SQLITE_PRAGMAS,
    }

# Database configuration
DATABASE_CONFIG = _get_database_config()
