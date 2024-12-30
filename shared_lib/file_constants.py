"""Shared constants for file operations.

This module provides centralized constants for file operations across the codebase.
All file-related modules should import these constants to ensure consistency.

Constants are configured via environment variables where appropriate, with secure
defaults if environment variables are not set.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Set

# Configure logger
logger = logging.getLogger(__name__)

# File permission constants
try:
    DEFAULT_FILE_PERMISSIONS = int(os.getenv("FILE_PERMISSION_DEFAULT", "0o644"), 8)
    DEFAULT_DIR_PERMISSIONS = int(os.getenv("DIR_PERMISSION_DEFAULT", "0o755"), 8)
except ValueError as e:
    logger.error(f"Invalid permission values in environment: {str(e)}")
    DEFAULT_FILE_PERMISSIONS = 0o644  # rw-r--r--
    DEFAULT_DIR_PERMISSIONS = 0o755  # rwxr-xr-x

# Permission enforcement
ENFORCE_PERMISSIONS = (
    os.getenv("FILE_PERMISSION_ENFORCE", "1") == "1"
)  # Enable by default

# Permission limits
MAX_PERMISSION_MODE = 0o777  # rwxrwxrwx - maximum allowed permissions
REQUIRED_FILE_MODES = 0o600  # Minimum required: rw------- (owner read/write)
REQUIRED_DIR_MODES = 0o700  # Minimum required: rwx------ (owner read/write/execute)

# File operation constants
FILE_ENCODING = "utf-8"  # Default file encoding for all operations
TEMP_SUFFIX = ".tmp"  # Suffix for temporary files
ROTATION_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"  # Format for rotated file timestamps

# File size limits
MAX_FILE_SIZE_MB = int(
    os.getenv("MAX_FILE_SIZE_MB", "100")
)  # Default max file size in MB
MAX_INPUT_LENGTH = int(
    os.getenv("MAX_INPUT_LENGTH", "1000000")
)  # Default max input length (1MB)

# Similarity threshold for file name comparison
SIMILARITY_THRESHOLD = float(
    os.getenv("FILE_SIMILARITY_THRESHOLD", "0.92")
)  # Only flag extremely similar names

# File extensions
JSONL_EXT = ".jsonl"  # JSON Lines file extension
LOG_EXT = ".log"  # Log file extension
TMP_EXT = ".tmp"  # Temporary file extension
PY_EXT = ".py"  # Python file extension
MD_EXT = ".md"  # Markdown file extension
TOML_EXT = ".toml"  # TOML file extension
PICKLE_EXT = ".pickle"  # Pickle file extension
HTML_EXT = ".html"  # HTML file extension

# Common filenames
INIT_FILE = "__init__.py"  # Python package marker
GITKEEP_FILE = ".gitkeep"  # Git directory marker
GITIGNORE_FILE = ".gitignore"  # Git ignore file
README_FILE = "README.md"  # Documentation file
SETUP_FILE = "setup.py"  # Python setup file
PYPROJECT_FILE = "pyproject.toml"  # Python project file
CONSTANTS_FILE = "constants.py"  # Constants file
TOKEN_FILE = "token.pickle"  # OAuth token file
HISTORY_FILE = ".marian_history"  # Command history file
DEFAULT_CHAT_LOG = "chat.jsonl"  # Default chat log file

# Directory names
DATA_DIR = "data"  # Data directory
LOGS_DIR = "logs"  # Logs directory
REPORTS_DIR = "reports"  # Reports directory
TESTING_DIR = "testing"  # Testing directory
ARCHIVE_DIR = "archive"  # Archive directory
CACHE_DIR = "__pycache__"  # Python cache directory
PYTEST_CACHE_DIR = ".pytest_cache"  # Pytest cache directory

# Project root and absolute paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / DATA_DIR
LOGS_PATH = PROJECT_ROOT / LOGS_DIR
REPORTS_PATH = PROJECT_ROOT / REPORTS_DIR / TESTING_DIR
TESTING_PATH = PROJECT_ROOT / TESTING_DIR
ARCHIVE_PATH = PROJECT_ROOT / ARCHIVE_DIR

# Create essential directories
for path in [DATA_PATH, LOGS_PATH, REPORTS_PATH]:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {str(e)}")
        raise RuntimeError(f"Cannot create directory {path}: {str(e)}")

# File patterns for testing
UNIQUE_FILENAMES: List[str] = [
    SETUP_FILE,
    GITIGNORE_FILE,
    PYPROJECT_FILE,
]

UNIQUE_CONTENT_FILES: List[str] = [
    README_FILE,  # Each README should be specific to its directory
]

ALLOWED_DUPLICATES: List[str] = [
    INIT_FILE,  # Python package markers
    GITKEEP_FILE,  # Git directory markers
    CONSTANTS_FILE,  # Allow domain-specific constants files
]

# Ignored directories for file operations
IGNORED_DIRS: List[str] = [
    CACHE_DIR,  # Python cache
    PYTEST_CACHE_DIR,  # Pytest cache
    ARCHIVE_DIR,  # Archived files
]

# Default paths
DEFAULT_LOG_DIR = str(Path.home() / "logs")  # Default directory for logs

# Chat log constants
ALLOWED_ROLES: Set[str] = {"user", "assistant", "system"}  # Valid chat roles
REQUIRED_METADATA_KEYS: Set[str] = {
    "session_id",
    "timestamp",
}  # Required chat metadata keys

# Environment variable names (for documentation and reference)
ENV_VARS: Dict[str, str] = {
    "FILE_PERMISSION_DEFAULT": "Default file permissions (octal, e.g. 0o644)",
    "DIR_PERMISSION_DEFAULT": "Default directory permissions (octal, e.g. 0o755)",
    "FILE_PERMISSION_ENFORCE": "Whether to enforce exact permissions (0 or 1)",
    "FILE_PERMISSION_LOG_LEVEL": "Logging level for permission events",
    "MAX_FILE_SIZE_MB": "Maximum file size in MB before rotation",
    "MAX_INPUT_LENGTH": "Maximum length for input strings",
}
