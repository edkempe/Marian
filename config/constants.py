"""Central configuration file for Marian project constants.

This file serves as the single source of truth for constants used throughout the project.
Update this file when adding new constants rather than hardcoding values in individual files.
"""

# Database Configuration
DATABASE_CONFIG = {
    # Database Files
    'EMAIL_DB_FILE': 'db_email_store.db',
    'ANALYSIS_DB_FILE': 'db_email_analysis.db',
    
    # Database URLs (SQLite)
    'EMAIL_DB_URL': 'sqlite:///db_email_store.db',
    'ANALYSIS_DB_URL': 'sqlite:///db_email_analysis.db',
    
    # Table Names
    'EMAIL_TABLE': 'emails',
    'ANALYSIS_TABLE': 'email_analysis',
}

# API Configuration
API_CONFIG = {
    'ANTHROPIC_MODEL': 'claude-3-opus-20240229',
    'MAX_TOKENS': 4000,
    'TEMPERATURE': 0.2,  # Slight variation allowed for more natural analysis
}

# Logging Configuration
LOGGING_CONFIG = {
    'LOG_FILE': 'marian.log',
    'MAX_BYTES': 10485760,  # 10MB
    'BACKUP_COUNT': 5,
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'LOG_LEVEL': 'INFO',
}

# Email Processing Configuration
EMAIL_CONFIG = {
    'BATCH_SIZE': 5,
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 5,  # seconds
}

# Metrics Configuration
METRICS_CONFIG = {
    'METRICS_PORT': 8000,
}
