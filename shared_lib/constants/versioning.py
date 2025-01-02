"""API and database versioning constants.

This module defines all versioning-related constants used throughout the application.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set
from enum import Enum

@dataclass(frozen=True)
class VersioningConstants:
    """API and database versioning constants."""
    
    # API versions
    CURRENT_API_VERSION: str = "v1"
    SUPPORTED_API_VERSIONS: Set[str] = field(default_factory=lambda: {"v1"})
    DEPRECATED_API_VERSIONS: Set[str] = field(default_factory=set)
    
    # Version headers
    API_VERSION_HEADER: str = "X-API-Version"
    DEPRECATION_HEADER: str = "X-API-Deprecated"
    SUNSET_HEADER: str = "X-API-Sunset"
    
    # Database versions
    CURRENT_DB_VERSION: str = "1.0.0"
    MIN_SUPPORTED_DB_VERSION: str = "1.0.0"
    
    # Migration settings
    AUTO_MIGRATE: bool = True
    MIGRATION_TIMEOUT: int = 300  # seconds
    MAX_MIGRATION_RETRIES: int = 3
    
    # Version patterns
    SEMVER_PATTERN: str = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    
    # Version compatibility
    VERSION_COMPATIBILITY: Dict[str, Set[str]] = field(default_factory=lambda: {
        "v1": {"1.0.x"}
    })
    
    # Deprecation settings
    DEPRECATION_WINDOW: int = 180  # days
    SUNSET_WINDOW: int = 365  # days

class ChangeType(str, Enum):
    """Types of changes in versioning."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    BREAKING = "breaking"

# Singleton instance
VERSIONING = VersioningConstants()
