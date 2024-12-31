# 9. Constants and Configuration Management

Date: 2024-12-31

## Status

Proposed

## Context

Currently, constants and configuration settings are spread across multiple files:
1. `shared_lib/constants.py` - Main constants
2. `shared_lib/file_constants.py` - File-related constants
3. `shared_lib/schema_constants.py` - Database schema constants
4. `models/domain_constants.py` - Domain-specific constants
5. `shared_lib/config_loader.py` - Configuration loading utilities

This creates several issues:
1. Duplication of constants
2. Unclear source of truth
3. Difficulty in maintaining consistency
4. Complex import patterns
5. No clear separation between constants and configuration

## Decision

After reviewing industry standards and best practices, we will separate constants from configuration:

### 1. Configuration Management (`config/`)
- Environment-specific values (following 12-Factor App)
- Uses Pydantic for validation and environment loading
- Handles runtime configuration
```python
# config/settings.py
from pydantic import BaseSettings, Field

class DatabaseSettings(BaseSettings):
    """Database configuration with validation."""
    URL: str = Field(..., regex=r'^postgresql://.*')
    MAX_CONNECTIONS: int = Field(default=5, gt=0)
    
    class Config:
        env_prefix = 'DB_'  # Will look for DB_URL, DB_MAX_CONNECTIONS
```

### 2. Constants Management (`constants/`)
- Uses dataclasses for immutable constants
- Uses Enums for fixed sets of values
- No runtime configuration or validation needed
```python
# constants/domain.py
from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class BusinessRules:
    """Core business rules that don't change."""
    MIN_PASSWORD_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 3

class UserRole(str, Enum):
    """Fixed set of user roles."""
    ADMIN = "admin"
    USER = "user"
```

### Directory Structure
```
shared_lib/
├── config/                 # Runtime configuration
│   ├── __init__.py
│   ├── settings.py        # Pydantic settings models
│   └── environment.py     # Environment loading
└── constants/             # Static constants
    ├── __init__.py
    ├── domain.py         # Business rules and types
    ├── security.py       # Security constants
    ├── database.py       # Database constants
    └── technical.py      # Technical constants
```

### Key Principles

1. **Configuration vs Constants**
   - Configuration: Environment-specific, loaded at runtime using Pydantic
   - Constants: Fixed values using dataclasses and enums

2. **Type Safety**
   - Configuration: Runtime validation with Pydantic
   - Constants: Static type checking with dataclasses

3. **Immutability**
   - Configuration: Mutable based on environment
   - Constants: Immutable using frozen dataclasses

4. **Validation**
   - Configuration: Runtime validation with Pydantic
   - Constants: Compile-time validation with type checkers

## Consequences

### Positive
1. Clear separation of constants and configuration
2. Better type safety and validation where needed
3. Simplified constant management
4. Proper environment configuration handling
5. Better alignment with 12-Factor App
6. No unnecessary complexity in constants

### Negative
1. Two different approaches to manage values
2. Migration effort required
3. Need to update imports

### Mitigation
1. Clear documentation of when to use each approach
2. Gradual migration strategy
3. Type checking to catch import errors

## References
- [12 Factor App - Config](https://12factor.net/config)
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Type Hints PEP 484](https://www.python.org/dev/peps/pep-0484/)
