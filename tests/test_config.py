"""Test configuration for Marian project."""

import os
from pathlib import Path
from typing import Dict, Union

from dotenv import load_dotenv

from shared_lib.constants import CONFIG

# Load environment variables from .env file
load_dotenv()

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# Test database paths - mirror production structure
TEST_DATABASE_CONFIG = {
    "email": {"path": str(TEST_DATA_DIR / "test_email.db")},
    "analysis": {"path": str(TEST_DATA_DIR / "test_analysis.db")},
    "catalog": {"path": str(TEST_DATA_DIR / "test_catalog.db")},
}

# Test environment configuration
TEST_ENV: Dict[str, str] = {
    "LOG_LEVEL": CONFIG.LOGGING["level"],
    "LOG_FILE": str(TEST_DATA_DIR / "test.log"),
    "BATCH_SIZE": str(CONFIG.DATABASE["email"]["batch_size"]),
    "MAX_RETRIES": str(CONFIG.DATABASE["email"]["max_retries"]),
    "TIMEOUT_SECONDS": "5",
}


def setup_test_env() -> None:
    """Set up test environment variables."""
    # Create test directories if they don't exist
    TEST_DATA_DIR.mkdir(exist_ok=True)
    
    # Preserve existing API key if present
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    # Set test environment variables
    for key, value in TEST_ENV.items():
        os.environ[key] = value
        
    # Set test database paths
    for db_type, config in TEST_DATABASE_CONFIG.items():
        os.environ[f"DB_{db_type.upper()}_PATH"] = config["path"]
    
    # Restore API key if it was present
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key


def cleanup_test_env() -> None:
    """Clean up test environment and databases."""
    # Remove test databases
    for config in TEST_DATABASE_CONFIG.values():
        db_path = Path(config["path"])
        if db_path.exists():
            db_path.unlink()

    # Remove test log file
    log_file = Path(TEST_ENV["LOG_FILE"])
    if log_file.exists():
        log_file.unlink()
