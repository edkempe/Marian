"""Utility for reliable logging of chat interactions.

This module provides robust logging of all chat interactions between users and the AI.
Chat logging is a critical system requirement - no interaction should proceed without
being properly logged.

The module uses a dual logging approach:
1. System events and errors are logged via standard logging
2. Chat interactions are stored in JSONL format for easy processing

Security considerations:
1. File operations are atomic to prevent data corruption
2. Proper permissions are checked before operations
3. Input is validated to prevent injection
4. Sensitive data is handled appropriately
5. All operations validate inputs and handle errors consistently
6. Permissions are enforced for all file operations
"""

import json
import logging
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union

from shared_lib.file_constants import ALLOWED_ROLES
from shared_lib.file_constants import DEFAULT_DIR_PERMISSIONS as DIR_PERMISSIONS_DEFAULT
from shared_lib.file_constants import (
    DEFAULT_FILE_PERMISSIONS as FILE_PERMISSIONS_DEFAULT,
)
from shared_lib.file_constants import (
    FILE_ENCODING,
    JSONL_EXT,
    LOGS_PATH,
    MAX_FILE_SIZE_MB,
    MAX_INPUT_LENGTH,
    PROJECT_ROOT,
    REQUIRED_METADATA_KEYS,
    ROTATION_TIMESTAMP_FORMAT,
    TEMP_SUFFIX,
)
from shared_lib.file_permission_util import FilePermissionManager
from shared_lib.logging_util import log_security_event, setup_logging
from shared_lib.path_security_util import PathSecurityManager

# Configure logger
logger = logging.getLogger(__name__)

# Environment settings with safe defaults
LOG_DIR = os.getenv("CHAT_LOG_DIR", str(LOGS_PATH))
LOG_PERMISSIONS = int(
    os.getenv("CHAT_LOG_PERMISSIONS", f"{FILE_PERMISSIONS_DEFAULT:o}"), 8
)
DIR_PERMISSIONS = int(
    os.getenv("CHAT_DIR_PERMISSIONS", f"{DIR_PERMISSIONS_DEFAULT:o}"), 8
)
LOG_ROTATION_SIZE_MB = int(
    os.getenv("CHAT_LOG_ROTATION_SIZE_MB", str(MAX_FILE_SIZE_MB))
)
ENFORCE_PERMISSIONS = (
    os.getenv("CHAT_ENFORCE_PERMISSIONS", "1") == "1"
)  # Enable by default

# Create logs directory if it doesn't exist
try:
    os.makedirs(LOG_DIR, mode=DIR_PERMISSIONS, exist_ok=True)
except Exception as e:
    logger.error(f"Failed to create log directory: {str(e)}")
    raise RuntimeError(f"Cannot create log directory: {str(e)}")

# File operation settings
ENCODING = FILE_ENCODING


class ChatLogger:
    """Handles reliable logging of chat interactions with security measures.

    This class provides secure and atomic logging of chat interactions to a JSONL file.
    It includes input validation, error handling, and secure file operations.

    Security measures:
    1. Input validation for all parameters
    2. Atomic file operations
    3. Secure file permissions (optional)
    4. Path traversal prevention
    5. Error handling with proper logging

    Configuration:
    Environment variables can be used to customize behavior:
    - CHAT_LOG_DIR: Optional base directory for log files
    - CHAT_LOG_PERMISSIONS: File permissions (default: 0o644)
    - CHAT_DIR_PERMISSIONS: Directory permissions (default: 0o755)
    - CHAT_LOG_ROTATION_SIZE_MB: Log rotation size in MB (default: 100)
    - CHAT_ENFORCE_PERMISSIONS: Whether to enforce permissions (default: 1)
    """

    def __init__(self, log_file: str) -> None:
        """Initialize the chat logger with security checks.

        Args:
            log_file: Path to the JSONL log file

        Raises:
            ValueError: If log_file path is invalid or empty
            OSError: If log directory cannot be created or accessed
            PermissionError: If lacking permissions to create/write to log file
            RuntimeError: If logging system cannot be initialized

        Security:
            - Validates log file path
            - Sets secure file permissions (if enabled)
            - Checks directory permissions
            - Prevents path traversal
        """
        if not log_file or not isinstance(log_file, str):
            logger.error("Invalid log file path provided")
            raise ValueError("Log file path must be a non-empty string")

        # Initialize security managers
        self.session_id = str(uuid.uuid4())
        self.path_manager = PathSecurityManager(LOG_DIR, self.session_id)
        self.perm_manager = FilePermissionManager(
            ENFORCE_PERMISSIONS, LOG_PERMISSIONS, DIR_PERMISSIONS, self.session_id
        )

        # Convert to Path object and validate
        self.log_path = Path(log_file).resolve()
        if self.log_path.suffix.lower() != JSONL_EXT:
            logger.error("Invalid log file extension")
            raise ValueError(f"Log file must have {JSONL_EXT} extension")

        # Validate path security
        self.log_path = self.path_manager.validate_path(self.log_path)

        # Ensure log directory exists with proper permissions
        try:
            if self.log_path.parent != Path("."):
                self.perm_manager.create_directory(self.log_path.parent)
        except PermissionError as e:
            logger.error(f"Permission denied creating log directory: {str(e)}")
            raise PermissionError(f"Cannot create log directory: {str(e)}")
        except OSError as e:
            logger.error(f"Failed to create log directory: {str(e)}")
            raise OSError(f"Cannot create log directory: {str(e)}")

        # Verify we can write to the log file
        try:
            if not self.log_path.exists():
                self.perm_manager.create_file(self.log_path)
            else:
                self.perm_manager.check_file_permissions(self.log_path)
                with self.log_path.open("a", encoding=ENCODING) as f:
                    f.write("")
        except PermissionError as e:
            logger.error(f"Permission denied accessing log file: {str(e)}")
            raise PermissionError(f"Cannot access log file: {str(e)}")
        except (OSError, IOError) as e:
            logger.error(f"Failed to access chat log file: {str(e)}")
            raise OSError(f"Cannot access log file: {str(e)}")

    def _validate_input(
        self,
        user_input: str,
        system_response: Any,
        model: str,
        role: str,
        metadata: Optional[Dict],
    ) -> None:
        """Validate input parameters.

        Args:
            user_input: The raw user input
            system_response: The system's response
            model: Model identifier
            role: Message role
            metadata: Additional metadata

        Raises:
            ValueError: If any input is invalid
            TypeError: If inputs have wrong type
            RuntimeError: If validation fails

        Security:
            - Validates input types
            - Checks input lengths
            - Validates role permissions
            - Verifies metadata format
        """
        if not isinstance(user_input, str):
            raise TypeError("user_input must be a string")
        if not isinstance(model, str):
            raise TypeError("model must be a string")
        if not user_input or not model:
            raise ValueError("user_input and model are required")
        if len(user_input) > MAX_INPUT_LENGTH:
            raise ValueError(f"user_input exceeds maximum length of {MAX_INPUT_LENGTH}")

        if role not in ALLOWED_ROLES:
            raise ValueError(f"role must be one of: {ALLOWED_ROLES}")

        if metadata is not None:
            if not isinstance(metadata, dict):
                raise TypeError("metadata must be a dictionary")
            missing_keys = REQUIRED_METADATA_KEYS - set(metadata.keys())
            if missing_keys:
                raise ValueError(f"Missing required metadata keys: {missing_keys}")

    def log_interaction(
        self,
        user_input: str,
        system_response: Any,
        model: str,
        role: str = "user",
        status: str = "success",
        error_details: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Log a single chat interaction with security measures.

        Args:
            user_input: The raw user input
            system_response: The system's response (will be converted to string)
            model: Identifier of the model used
            role: Role of the message ("user", "assistant", or "system")
            status: Status of the interaction ("success" or "error")
            error_details: Error information if status is "error"
            metadata: Additional metadata to log

        Returns:
            bool: True if logging succeeded, False if failed

        Raises:
            ValueError: If required fields are missing or invalid
            TypeError: If inputs have wrong types
            OSError: If file operations fail
            PermissionError: If lacking permissions to write logs
            RuntimeError: If logging fails due to system error

        Security:
            - Validates all inputs
            - Uses atomic file operations
            - Handles sensitive data
            - Proper error handling
            - Secure file permissions
        """
        # Validate all inputs
        self._validate_input(user_input, system_response, model, role, metadata)

        # Prepare log entry with security measures
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "role": role,
            "user_input": user_input[
                :MAX_INPUT_LENGTH
            ],  # Truncate if somehow bypassed validation
            "system_response": str(system_response)[:MAX_INPUT_LENGTH],
            "model": model,
            "status": status,
            "error_details": error_details,
            "metadata": metadata or {},
        }

        # Create temp file path using pathlib
        temp_path = self.log_path.with_suffix(TEMP_SUFFIX)

        try:
            # Atomic write by first writing to temp file
            try:
                mode = LOG_PERMISSIONS if ENFORCE_PERMISSIONS else None
                with temp_path.open("w", encoding=ENCODING) as f:
                    if mode is not None:
                        os.chmod(temp_path, mode)
                    json.dump(log_entry, f)
                    f.write("\n")
                    f.flush()
                    os.fsync(f.fileno())
            except (TypeError, ValueError) as e:
                logger.error(f"Failed to serialize log entry: {str(e)}")
                raise TypeError(f"Failed to serialize log entry: {str(e)}")
            except (OSError, IOError) as e:
                logger.error(f"Failed to write temporary log file: {str(e)}")
                raise OSError(f"Failed to write temporary log file: {str(e)}")

            # Atomic move of temp file to append to log file
            try:
                with self.log_path.open("a", encoding=ENCODING) as f:
                    with temp_path.open("r", encoding=ENCODING) as t:
                        f.write(t.read())
                    f.flush()
                    os.fsync(f.fileno())
            except (OSError, IOError) as e:
                logger.error(f"Failed to append to log file: {str(e)}")
                # Try to restore original file
                if temp_path.exists():
                    shutil.copy2(temp_path, self.log_path)
                    if ENFORCE_PERMISSIONS:
                        os.chmod(self.log_path, LOG_PERMISSIONS)
                raise OSError(f"Failed to append to log file: {str(e)}")
            finally:
                # Clean up temp file
                try:
                    if temp_path.exists():
                        temp_path.unlink()
                except OSError:
                    logger.warning(f"Failed to remove temporary file: {temp_path}")

            logger.info(
                "Chat interaction logged",
                extra={
                    "session_id": self.session_id,
                    "status": status,
                    "has_error": error_details is not None,
                },
            )
            return True

        except PermissionError as e:
            logger.error(f"Permission denied writing to log file: {str(e)}")
            raise PermissionError(f"Cannot write to log file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during logging: {str(e)}")
            raise RuntimeError(f"Failed to log interaction: {str(e)}")

    def rotate_logs(self, max_size_mb: Optional[int] = None) -> bool:
        """Rotate log file if it exceeds max_size_mb with security measures.

        Args:
            max_size_mb: Maximum size in MB before rotation. If None, uses
                        CHAT_LOG_ROTATION_SIZE_MB environment setting.

        Returns:
            bool: True if rotation succeeded or wasn't needed, False if failed

        Raises:
            ValueError: If max_size_mb is invalid
            OSError: If file operations fail
            PermissionError: If lacking permissions
            RuntimeError: If rotation fails due to system error

        Security:
            - Validates input size
            - Atomic file operations
            - Preserves file permissions
            - Proper error handling
            - Secure cleanup
        """
        max_size = max_size_mb if max_size_mb is not None else LOG_ROTATION_SIZE_MB

        if not isinstance(max_size, int) or max_size <= 0:
            logger.error("Invalid maximum log size")
            log_security_event(
                logger,
                "invalid_log_rotation_size",
                {"max_size_mb": max_size, "session_id": self.session_id},
            )
            raise ValueError("max_size_mb must be a positive integer")

        try:
            if not self.log_path.exists():
                return True

            size_mb = self.log_path.stat().st_size / (1024 * 1024)
            if size_mb < max_size:
                return True

            # Create rotated file path
            timestamp = datetime.now().strftime(ROTATION_TIMESTAMP_FORMAT)
            rotated_path = self.log_path.with_name(f"{self.log_path.name}.{timestamp}")

            # Check permissions before rotation
            self.perm_manager.check_file_permissions(self.log_path)
            self.perm_manager.check_directory_permissions(self.log_path.parent)

            try:
                # Use shutil.copy2 to preserve metadata
                self.perm_manager.copy_file(self.log_path, rotated_path)
                log_security_event(
                    logger,
                    "log_rotation_started",
                    {
                        "original_file": str(self.log_path),
                        "rotated_file": str(rotated_path),
                        "size_mb": size_mb,
                        "session_id": self.session_id,
                    },
                )
            except (OSError, IOError) as e:
                logger.error(f"Failed to copy log file: {str(e)}")
                log_security_event(
                    logger,
                    "log_rotation_copy_failed",
                    {
                        "error": str(e),
                        "original_file": str(self.log_path),
                        "rotated_file": str(rotated_path),
                        "session_id": self.session_id,
                    },
                )
                raise OSError(f"Failed to copy log file: {str(e)}")

            try:
                # Truncate original file
                self.perm_manager.truncate_file(self.log_path)
                log_security_event(
                    logger,
                    "log_rotation_completed",
                    {
                        "original_file": str(self.log_path),
                        "rotated_file": str(rotated_path),
                        "session_id": self.session_id,
                    },
                )
            except (OSError, IOError) as e:
                logger.error(f"Failed to truncate log file: {str(e)}")
                log_security_event(
                    logger,
                    "log_rotation_truncate_failed",
                    {
                        "error": str(e),
                        "original_file": str(self.log_path),
                        "rotated_file": str(rotated_path),
                        "session_id": self.session_id,
                    },
                )
                # Try to restore original file
                if rotated_path.exists():
                    self.perm_manager.copy_file(rotated_path, self.log_path)
                raise OSError(f"Failed to truncate log file: {str(e)}")

            logger.info(
                f"Rotated chat log file",
                extra={
                    "old_file": str(self.log_path),
                    "new_file": str(rotated_path),
                    "size_mb": size_mb,
                },
            )
            return True

        except Exception as e:
            logger.error(f"Unexpected error during log rotation: {str(e)}")
            log_security_event(
                logger,
                "log_rotation_failed",
                {
                    "error": str(e),
                    "original_file": str(self.log_path),
                    "session_id": self.session_id,
                },
            )
            raise RuntimeError(f"Failed to rotate logs: {str(e)}")
