"""Test configuration for Marian project."""

import os
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / 'test_data'
TEST_DATA_DIR.mkdir(exist_ok=True)

# Test database paths
TEST_EMAIL_DB = str(TEST_DATA_DIR / 'test_email_store.db')
TEST_ANALYSIS_DB = str(TEST_DATA_DIR / 'test_analysis_store.db')

# Test environment configuration
TEST_ENV = {
    'ANTHROPIC_API_KEY': 'test-key',  # Will be replaced with real key in CI
    'DB_EMAIL_PATH': TEST_EMAIL_DB,
    'DB_ANALYSIS_PATH': TEST_ANALYSIS_DB,
    'LOG_LEVEL': 'INFO',
    'LOG_FILE': str(TEST_DATA_DIR / 'test.log'),
    'BATCH_SIZE': '10',
    'MAX_RETRIES': '2',
    'TIMEOUT_SECONDS': '5'
}

def setup_test_env():
    """Set up test environment variables."""
    for key, value in TEST_ENV.items():
        os.environ[key] = value

def cleanup_test_env():
    """Clean up test environment and databases."""
    # Remove test databases if they exist
    for db_path in [TEST_EMAIL_DB, TEST_ANALYSIS_DB]:
        if os.path.exists(db_path):
            os.remove(db_path)
    
    # Clean up environment variables
    for key in TEST_ENV:
        if key in os.environ:
            del os.environ[key]
