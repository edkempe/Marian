"""Database-related constants."""

# Database Configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "jexi",
    "user": "jexi",
    "password": None,  # Set via environment variable
}

# Connection Pool Settings
MIN_POOL_SIZE = 5
MAX_POOL_SIZE = 20
POOL_TIMEOUT = 30

# Query Timeouts (seconds)
QUERY_TIMEOUT = 30
LONG_QUERY_TIMEOUT = 300

# Batch Sizes
BATCH_SIZE = 1000
MAX_BATCH_SIZE = 10000
