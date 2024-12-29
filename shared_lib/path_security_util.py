"""Utility for secure path operations.

This module provides secure path validation and operations across the codebase.
It prevents path traversal attacks and ensures paths stay within allowed directories.

Security measures:
1. Path traversal prevention
2. Base directory enforcement
3. Path validation and normalization
4. Security event logging
"""

import logging
from pathlib import Path
from typing import Optional

from shared_lib.logging_util import log_security_event
from shared_lib.file_constants import PROJECT_ROOT

# Configure logger
logger = logging.getLogger(__name__)

class PathSecurityManager:
    """Manages secure path operations.
    
    This class provides consistent path security across the codebase with
    proper validation and logging.
    """
    
    def __init__(self, base_dir: Optional[str] = None, session_id: Optional[str] = None):
        """Initialize path security manager.
        
        Args:
            base_dir: Optional base directory to restrict paths to
            session_id: Optional session ID for logging
            
        Security:
            - Validates base directory
            - Normalizes paths
            - Logs configuration
        """
        self.base_dir = Path(base_dir).resolve() if base_dir else PROJECT_ROOT
        self.session_id = session_id
        
        # Validate base directory exists
        if not self.base_dir.exists():
            logger.error(f"Base directory does not exist: {self.base_dir}")
            raise ValueError(f"Base directory does not exist: {self.base_dir}")
    
    def validate_path(self, path: Path) -> Path:
        """Validate path for security concerns.
        
        Args:
            path: Path to validate
            
        Returns:
            Path: Resolved and validated path
            
        Raises:
            ValueError: If path contains security risks
            RuntimeError: If path validation fails
            
        Security:
            - Prevents path traversal attacks
            - Validates path is within allowed directory
            - Checks path format
        """
        try:
            real_path = path.resolve()
            if self.base_dir:
                if not str(real_path).startswith(str(self.base_dir)):
                    logger.error("Path outside of base directory")
                    log_security_event(logger, "path_traversal_attempt", {
                        "path": str(path),
                        "base_dir": str(self.base_dir),
                        "session_id": self.session_id
                    })
                    raise ValueError("Path must be within base directory")
            return real_path
        except (RuntimeError, OSError) as e:
            logger.error(f"Path validation failed: {str(e)}")
            log_security_event(logger, "path_validation_error", {
                "path": str(path),
                "error": str(e),
                "session_id": self.session_id
            })
            raise ValueError(f"Invalid path: {str(e)}")
    
    def is_safe_path(self, path: Path) -> bool:
        """Check if path is safe without raising exceptions.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path is safe, False otherwise
            
        Security:
            - Same checks as validate_path but returns bool
            - Logs security events
            - No exceptions
        """
        try:
            self.validate_path(path)
            return True
        except ValueError:
            return False
    
    def get_relative_path(self, path: Path) -> Path:
        """Get path relative to base directory.
        
        Args:
            path: Path to convert
            
        Returns:
            Path: Path relative to base directory
            
        Raises:
            ValueError: If path is outside base directory
            RuntimeError: If conversion fails
            
        Security:
            - Validates path is within base directory
            - Normalizes path format
            - Logs security events
        """
        if not self.base_dir:
            raise RuntimeError("Base directory not configured")
            
        try:
            real_path = self.validate_path(path)
            return real_path.relative_to(self.base_dir)
        except ValueError as e:
            logger.error(f"Failed to get relative path: {str(e)}")
            log_security_event(logger, "relative_path_error", {
                "path": str(path),
                "base_dir": str(self.base_dir),
                "error": str(e),
                "session_id": self.session_id
            })
            raise ValueError(f"Cannot get relative path: {str(e)}")
    
    def join_path(self, *paths: str) -> Path:
        """Securely join path components.
        
        Args:
            *paths: Path components to join
            
        Returns:
            Path: Joined and validated path
            
        Raises:
            ValueError: If resulting path is unsafe
            RuntimeError: If join fails
            
        Security:
            - Validates joined path
            - Prevents path traversal
            - Logs security events
        """
        try:
            path = Path(*paths)
            return self.validate_path(path)
        except (ValueError, RuntimeError) as e:
            logger.error(f"Failed to join paths: {str(e)}")
            log_security_event(logger, "path_join_error", {
                "paths": paths,
                "error": str(e),
                "session_id": self.session_id
            })
            raise ValueError(f"Cannot join paths: {str(e)}")
