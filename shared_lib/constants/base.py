"""Base constants and types for the Marian project.

This module defines base constants and types that are used across multiple
domains. It serves as a foundation for other constant modules.

Note:
    This module has the LOWEST precedence in the constants hierarchy.
    Values defined here can be overridden by any other constants module
    according to the following precedence (highest to lowest):
    1. security.py  - Security-critical values
    2. domain.py   - Business rules and core types
    3. database.py - Schema and database config
    4. api.py      - External service config
    5. file.py     - File operations
    6. testing.py  - Test configurations
    7. base.py     - This module (lowest precedence)

Key Features:
1. Type definitions used across modules
2. Base configuration types
3. Common validation functions
4. Shared enums and constants
"""

from enum import Enum
from typing import Any, Dict, List, TypedDict, Union

class BaseConfig(TypedDict):
    """Base configuration type with common fields.
    
    Note:
        These values can be overridden by higher precedence modules.
        See module docstring for precedence order.
    """
    
    version: str
    environment: str
    debug: bool
    strict_mode: bool

class TimeConfig(TypedDict):
    """Time-related configuration.
    
    Note:
        These values can be overridden by higher precedence modules.
        See module docstring for precedence order.
    """
    
    date_format: str
    time_format: str
    timezone: str
    utc_offset: int

class ValidationConfig(TypedDict):
    """Validation configuration.
    
    Note:
        These values can be overridden by higher precedence modules.
        See module docstring for precedence order.
    """
    
    strict_validation: bool
    allow_unknown: bool
    coerce_types: bool

# Base configuration instance
BASE = BaseConfig(
    version="1.0.0",
    environment="development",
    debug=True,
    strict_mode=True,
)

# Time configuration
TIME = TimeConfig(
    date_format="%Y-%m-%d",
    time_format="%H:%M:%S",
    timezone="UTC",
    utc_offset=0,
)

# Validation configuration
VALIDATION = ValidationConfig(
    strict_validation=True,
    allow_unknown=False,
    coerce_types=True,
)

# Common status values
class Status(str, Enum):
    """Common status values.
    
    Note:
        These values can be overridden by higher precedence modules.
        See module docstring for precedence order.
    """
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"
    SUCCESS = "success"
    FAILURE = "failure"
    
    @classmethod
    def values(cls) -> List[str]:
        """Get all valid status values."""
        return [member.value for member in cls]
