"""File operation constants."""

from dataclasses import dataclass, field
from typing import Dict, Set
from pathlib import Path

@dataclass(frozen=True)
class FileConstants:
    """File operation constants."""
    
    # File Size Limits
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # File Types
    ALLOWED_EXTENSIONS: Set[str] = field(default_factory=lambda: {
        "txt",
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "csv",
    })
    
    # File Paths
    UPLOAD_FOLDER: Path = Path("uploads")
    TEMP_FOLDER: Path = Path("temp")
    BACKUP_FOLDER: Path = Path("backup")
    
    # Project Directories
    ROOT_DIR: Path = Path(__file__).parent.parent.parent
    DOCS_DIR: Path = ROOT_DIR / "docs"
    CACHE_DIR: Path = ROOT_DIR / "cache"
    SESSION_LOGS_DIR: Path = ROOT_DIR / "logs" / "sessions"
    
    # File Categories
    FILE_CATEGORIES: Dict[str, Set[str]] = field(default_factory=lambda: {
        "documents": {"txt", "pdf", "doc", "docx"},
        "spreadsheets": {"xls", "xlsx", "csv"},
        "images": {"jpg", "jpeg", "png", "gif"},
        "archives": {"zip", "tar", "gz", "7z"}
    })
    
    # File Size Categories (in bytes)
    SIZE_CATEGORIES: Dict[str, int] = field(default_factory=lambda: {
        "tiny": 1024,  # 1KB
        "small": 1024 * 1024,  # 1MB
        "medium": 10 * 1024 * 1024,  # 10MB
        "large": 100 * 1024 * 1024,  # 100MB
        "huge": 1024 * 1024 * 1024  # 1GB
    })

# Singleton instance
FILE = FileConstants()
