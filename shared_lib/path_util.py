"""Utility for common path operations.

This module provides common path operations used across the codebase.
It ensures consistent path handling and proper use of Path objects.

Security measures:
1. Path validation
2. Error handling
3. Logging of operations
4. Integration with security settings
"""

import os
import logging
from pathlib import Path
from typing import Union, List, Optional

from shared_lib.file_constants import (
    FILE_ENCODING,
    IGNORED_DIRS,
    DEFAULT_FILE_PERMISSIONS,
    DEFAULT_DIR_PERMISSIONS
)
from shared_lib.logging_util import log_security_event

# Configure logger
logger = logging.getLogger(__name__)

def get_project_root() -> Path:
    """Get the project root directory.
    
    Returns:
        Path: Absolute path to project root
        
    Raises:
        RuntimeError: If project root cannot be determined
    """
    try:
        return Path(__file__).resolve().parent.parent
    except Exception as e:
        logger.error(f"Failed to determine project root: {str(e)}")
        raise RuntimeError(f"Cannot determine project root: {str(e)}")

def get_absolute_path(path: Union[str, Path], validate: bool = True) -> Path:
    """Convert path to absolute Path object.
    
    Args:
        path: Path to convert
        validate: Whether to validate path
        
    Returns:
        Path: Absolute path
        
    Raises:
        ValueError: If path is invalid or unsafe
        RuntimeError: If path resolution fails
    """
    try:
        abs_path = Path(path).resolve()
        if validate and any(part in str(abs_path) for part in IGNORED_DIRS):
            logger.error(f"Path contains ignored directory: {str(abs_path)}")
            raise ValueError(f"Path contains ignored directory: {str(abs_path)}")
        return abs_path
    except Exception as e:
        logger.error(f"Failed to get absolute path: {str(e)}")
        raise RuntimeError(f"Cannot get absolute path: {str(e)}")

def join_paths(*paths: Union[str, Path], validate: bool = True) -> Path:
    """Join path components.
    
    Args:
        *paths: Path components to join
        validate: Whether to validate path
        
    Returns:
        Path: Joined path
        
    Raises:
        ValueError: If resulting path is invalid or unsafe
        RuntimeError: If path joining fails
    """
    try:
        path = Path(*paths)
        return get_absolute_path(path, validate)
    except Exception as e:
        logger.error(f"Failed to join paths: {str(e)}")
        raise RuntimeError(f"Cannot join paths: {str(e)}")

def get_relative_path(path: Union[str, Path], start: Optional[Union[str, Path]] = None) -> Path:
    """Get relative path from start.
    
    Args:
        path: Path to convert
        start: Start path (defaults to current directory)
        
    Returns:
        Path: Relative path
        
    Raises:
        ValueError: If path is outside start directory
        RuntimeError: If conversion fails
    """
    try:
        path = get_absolute_path(path)
        if start:
            start = get_absolute_path(start)
        else:
            start = Path.cwd()
        return path.relative_to(start)
    except Exception as e:
        logger.error(f"Failed to get relative path: {str(e)}")
        raise RuntimeError(f"Cannot get relative path: {str(e)}")

def ensure_directory(path: Union[str, Path], mode: int = DEFAULT_DIR_PERMISSIONS) -> Path:
    """Ensure directory exists with proper permissions.
    
    Args:
        path: Directory path
        mode: Directory permissions
        
    Returns:
        Path: Directory path
        
    Raises:
        PermissionError: If lacking permissions
        RuntimeError: If directory creation fails
    """
    try:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True, mode=mode)
        return path
    except Exception as e:
        logger.error(f"Failed to ensure directory exists: {str(e)}")
        raise RuntimeError(f"Cannot create directory: {str(e)}")

def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
    ignore_dirs: bool = True
) -> List[Path]:
    """List files in directory matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern
        ignore_dirs: Whether to ignore directories in IGNORED_DIRS
        
    Returns:
        List[Path]: Matching files
        
    Raises:
        ValueError: If directory is invalid
        RuntimeError: If listing fails
    """
    try:
        directory = get_absolute_path(directory)
        files = list(directory.glob(pattern))
        if ignore_dirs:
            files = [f for f in files if not any(d in str(f) for d in IGNORED_DIRS)]
        return files
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise RuntimeError(f"Cannot list files: {str(e)}")

def read_file(path: Union[str, Path], encoding: str = FILE_ENCODING) -> str:
    """Read file contents safely.
    
    Args:
        path: Path to file
        encoding: File encoding
        
    Returns:
        str: File contents
        
    Raises:
        FileNotFoundError: If file does not exist
        PermissionError: If lacking permissions
        RuntimeError: If reading fails
    """
    try:
        path = get_absolute_path(path)
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file: {str(e)}")
        raise RuntimeError(f"Cannot read file: {str(e)}")

def write_file(
    path: Union[str, Path],
    content: str,
    encoding: str = FILE_ENCODING,
    mode: int = DEFAULT_FILE_PERMISSIONS
) -> None:
    """Write file contents safely.
    
    Args:
        path: Path to file
        content: Content to write
        encoding: File encoding
        mode: File permissions
        
    Raises:
        PermissionError: If lacking permissions
        RuntimeError: If writing fails
    """
    try:
        path = get_absolute_path(path)
        ensure_directory(path.parent)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        path.chmod(mode)
    except Exception as e:
        logger.error(f"Failed to write file: {str(e)}")
        raise RuntimeError(f"Cannot write file: {str(e)}")
