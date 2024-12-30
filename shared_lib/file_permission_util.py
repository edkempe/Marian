"""Utility for secure file permission management.

This module provides consistent and secure file permission handling across
the codebase. It includes permission validation, enforcement, and security
event logging.

Security measures:
1. Configurable permission enforcement
2. Secure default permissions
3. Proper error handling and logging
4. Permission validation and correction
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Optional

from shared_lib.file_constants import (
    DEFAULT_DIR_PERMISSIONS,
    DEFAULT_FILE_PERMISSIONS,
    ENFORCE_PERMISSIONS,
    FILE_ENCODING,
    MAX_PERMISSION_MODE,
    REQUIRED_DIR_MODES,
    REQUIRED_FILE_MODES,
)
from shared_lib.logging_util import log_security_event

# Configure logger
logger = logging.getLogger(__name__)


class FilePermissionManager:
    """Manages file permissions with security measures."""

    def __init__(
        self,
        enforce_permissions: Optional[bool] = None,
        file_permissions: Optional[int] = None,
        dir_permissions: Optional[int] = None,
        session_id: Optional[str] = None,
    ):
        """Initialize permission manager with secure defaults."""
        self.enforce_permissions = (
            enforce_permissions
            if enforce_permissions is not None
            else ENFORCE_PERMISSIONS
        )
        self.file_permissions = (
            file_permissions
            if file_permissions is not None
            else DEFAULT_FILE_PERMISSIONS
        )
        self.dir_permissions = (
            dir_permissions if dir_permissions is not None else DEFAULT_DIR_PERMISSIONS
        )
        self.session_id = session_id

        # Validate permission values
        if not 0 <= self.file_permissions <= MAX_PERMISSION_MODE:
            raise ValueError(
                f"File permissions must be between 0 and {MAX_PERMISSION_MODE:o}"
            )
        if not 0 <= self.dir_permissions <= MAX_PERMISSION_MODE:
            raise ValueError(
                f"Directory permissions must be between 0 and {MAX_PERMISSION_MODE:o}"
            )

        # Validate minimum required permissions
        if self.file_permissions & REQUIRED_FILE_MODES != REQUIRED_FILE_MODES:
            raise ValueError("File permissions must include read and write access")
        if self.dir_permissions & REQUIRED_DIR_MODES != REQUIRED_DIR_MODES:
            raise ValueError(
                "Directory permissions must include read, write, and execute access"
            )

        # Log initialization
        log_security_event(
            logger,
            "permission_manager_initialized",
            {
                "enforce_permissions": self.enforce_permissions,
                "file_permissions": f"{self.file_permissions:o}",
                "dir_permissions": f"{self.dir_permissions:o}",
                "session_id": self.session_id,
            },
        )

    def check_directory_permissions(self, path: Path) -> None:
        """Check and enforce directory permissions."""
        try:
            if not path.exists():
                raise FileNotFoundError(f"Directory does not exist: {path}")
            if not path.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {path}")

            if not os.access(path, REQUIRED_DIR_MODES):
                log_security_event(
                    logger,
                    "insufficient_directory_permissions",
                    {
                        "path": str(path),
                        "required_permissions": "read|write|execute",
                        "session_id": self.session_id,
                    },
                )
                raise PermissionError(f"Insufficient permissions for directory: {path}")

            if self.enforce_permissions:
                current_mode = path.stat().st_mode & MAX_PERMISSION_MODE
                if current_mode != self.dir_permissions:
                    os.chmod(path, self.dir_permissions)
                    log_security_event(
                        logger,
                        "directory_permissions_fixed",
                        {
                            "path": str(path),
                            "old_mode": f"{current_mode:o}",
                            "new_mode": f"{self.dir_permissions:o}",
                            "session_id": self.session_id,
                        },
                    )
        except OSError as e:
            log_security_event(
                logger,
                "directory_permission_error",
                {"path": str(path), "error": str(e), "session_id": self.session_id},
            )
            raise RuntimeError(f"Failed to check directory permissions: {str(e)}")

    def check_file_permissions(self, path: Path) -> None:
        """Check and enforce file permissions."""
        try:
            if not path.exists():
                raise FileNotFoundError(f"File does not exist: {path}")
            if not path.is_file():
                raise IsADirectoryError(f"Path is not a file: {path}")

            if not os.access(path, REQUIRED_FILE_MODES):
                log_security_event(
                    logger,
                    "insufficient_file_permissions",
                    {
                        "path": str(path),
                        "required_permissions": "read|write",
                        "session_id": self.session_id,
                    },
                )
                raise PermissionError(f"Insufficient permissions for file: {path}")

            if self.enforce_permissions:
                current_mode = path.stat().st_mode & MAX_PERMISSION_MODE
                if current_mode != self.file_permissions:
                    os.chmod(path, self.file_permissions)
                    log_security_event(
                        logger,
                        "file_permissions_fixed",
                        {
                            "path": str(path),
                            "old_mode": f"{current_mode:o}",
                            "new_mode": f"{self.file_permissions:o}",
                            "session_id": self.session_id,
                        },
                    )
        except OSError as e:
            log_security_event(
                logger,
                "file_permission_error",
                {"path": str(path), "error": str(e), "session_id": self.session_id},
            )
            raise RuntimeError(f"Failed to check file permissions: {str(e)}")

    def create_directory(self, path: Path) -> None:
        """Create directory with secure permissions."""
        try:
            path.mkdir(parents=True, exist_ok=True)
            if self.enforce_permissions:
                os.chmod(path, self.dir_permissions)
                log_security_event(
                    logger,
                    "directory_created",
                    {
                        "path": str(path),
                        "permissions": f"{self.dir_permissions:o}",
                        "session_id": self.session_id,
                    },
                )
            self.check_directory_permissions(path)
        except OSError as e:
            log_security_event(
                logger,
                "directory_creation_failed",
                {"path": str(path), "error": str(e), "session_id": self.session_id},
            )
            raise RuntimeError(f"Failed to create directory: {str(e)}")

    def create_file(self, path: Path) -> None:
        """Create file with secure permissions."""
        try:
            path.touch()
            if self.enforce_permissions:
                os.chmod(path, self.file_permissions)
                log_security_event(
                    logger,
                    "file_created",
                    {
                        "path": str(path),
                        "permissions": f"{self.file_permissions:o}",
                        "session_id": self.session_id,
                    },
                )
            self.check_file_permissions(path)
        except OSError as e:
            log_security_event(
                logger,
                "file_creation_failed",
                {"path": str(path), "error": str(e), "session_id": self.session_id},
            )
            raise RuntimeError(f"Failed to create file: {str(e)}")

    def copy_file(self, src: Path, dst: Path) -> None:
        """Copy file with secure permissions."""
        try:
            self.check_file_permissions(src)
            shutil.copy2(src, dst)

            if self.enforce_permissions:
                os.chmod(dst, self.file_permissions)
                log_security_event(
                    logger,
                    "file_copied",
                    {
                        "source": str(src),
                        "destination": str(dst),
                        "permissions": f"{self.file_permissions:o}",
                        "session_id": self.session_id,
                    },
                )

            self.check_file_permissions(dst)
        except OSError as e:
            log_security_event(
                logger,
                "file_copy_failed",
                {
                    "source": str(src),
                    "destination": str(dst),
                    "error": str(e),
                    "session_id": self.session_id,
                },
            )
            raise RuntimeError(f"Failed to copy file: {str(e)}")

    def truncate_file(self, path: Path) -> None:
        """Truncate file with secure permissions."""
        try:
            self.check_file_permissions(path)
            path.write_text("", encoding=FILE_ENCODING)

            if self.enforce_permissions:
                os.chmod(path, self.file_permissions)
                log_security_event(
                    logger,
                    "file_truncated",
                    {
                        "path": str(path),
                        "permissions": f"{self.file_permissions:o}",
                        "session_id": self.session_id,
                    },
                )
        except OSError as e:
            log_security_event(
                logger,
                "file_truncate_failed",
                {"path": str(path), "error": str(e), "session_id": self.session_id},
            )
            raise RuntimeError(f"Failed to truncate file: {str(e)}")
