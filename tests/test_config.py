"""Test configuration for Marian project."""

import os
from pathlib import Path
from typing import Dict, Union

from dotenv import load_dotenv

from shared_lib.constants import LOGGING_CONFIG, EMAIL_CONFIG

# Load environment variables from .env file
load_dotenv()

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# Test database paths
TEST_EMAIL_DB = TEST_DATA_DIR / "test_email_store.db"
TEST_ANALYSIS_DB = TEST_DATA_DIR / "test_analysis_store.db"

# Test environment configuration
TEST_ENV: Dict[str, str] = {
    "DB_EMAIL_PATH": str(TEST_EMAIL_DB),
    "DB_ANALYSIS_PATH": str(TEST_ANALYSIS_DB),
    "LOG_LEVEL": LOGGING_CONFIG["LOG_LEVEL"],
    "LOG_FILE": str(TEST_DATA_DIR / "test.log"),
    "BATCH_SIZE": str(EMAIL_CONFIG["BATCH_SIZE"]),
    "MAX_RETRIES": str(EMAIL_CONFIG["MAX_RETRIES"]),
    "TIMEOUT_SECONDS": "5",
}


def setup_test_env() -> None:
    """Set up test environment variables."""
    # Preserve existing API key if present
    api_key = os.getenv("ANTHROPIC_API_KEY")

    # Set test environment variables
    for key, value in TEST_ENV.items():
        os.environ[key] = value

    # Restore API key if it was present
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key


def cleanup_test_env() -> None:
    """Clean up test environment and databases."""
    # Remove test databases if they exist
    for db_path in [TEST_EMAIL_DB, TEST_ANALYSIS_DB]:
        if os.path.exists(str(db_path)):
            os.remove(str(db_path))

    # Remove test log file
    log_file = Path(TEST_ENV["LOG_FILE"])
    if log_file.exists():
        log_file.unlink()
