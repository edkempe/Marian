"""Database-related constants.

This module is deprecated. Use config.settings.database instead.
"""

from typing import Dict, Any
from warnings import warn

from config.settings.database import database_settings

warn(
    "shared_lib.constants.database is deprecated. "
    "Use config.settings.database.database_settings instead.",
    DeprecationWarning,
    stacklevel=2
)

def _get_database_config() -> Dict[str, Any]:
    """Get database configuration for backward compatibility."""
    return {
        "host": database_settings.URL.host,
        "port": database_settings.URL.port,
        "database": database_settings.URL.path.lstrip("/"),
        "user": database_settings.URL.username,
        "password": database_settings.URL.password,
        "min_connections": database_settings.MIN_CONNECTIONS,
        "max_connections": database_settings.MAX_CONNECTIONS,
        "connection_timeout": database_settings.CONNECTION_TIMEOUT,
        "query_timeout": database_settings.QUERY_TIMEOUT,
    }

# Deprecated: Use config.settings.database.database_settings instead
DATABASE_CONFIG = _get_database_config()

# Connection Pool Settings (Deprecated)
MIN_POOL_SIZE = database_settings.MIN_CONNECTIONS
MAX_POOL_SIZE = database_settings.MAX_CONNECTIONS
POOL_TIMEOUT = database_settings.CONNECTION_TIMEOUT

# Query Timeouts (Deprecated)
QUERY_TIMEOUT = database_settings.QUERY_TIMEOUT
LONG_QUERY_TIMEOUT = database_settings.QUERY_TIMEOUT * 10

# Batch Sizes (Deprecated)
BATCH_SIZE = database_settings.MAX_QUERY_ROWS // 10
MAX_BATCH_SIZE = database_settings.MAX_QUERY_ROWS
