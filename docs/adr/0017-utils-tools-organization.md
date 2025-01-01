# 17. Utils and Tools Organization

Date: 2024-12-31

## Status

Accepted

## Revision History
1.0.0 (2024-12-31) @dev
- Initial version
- Defined utils vs tools structure
- Added migration plan

1.1.0 (2025-01-01) @dev
- Added specific tooling decisions
- Clarified development dependencies

## Context
- Project needs clear separation between application utilities and development tools
- Current structure mixes these concerns
- Need to follow industry standards for better maintainability
- Need clear decisions on development tools and their organization

## Decision

We will organize utilities and tools into three distinct directories:

1. `/utils/`: Application-level utilities
```python
# Example: utils/date_utils.py
from datetime import datetime

def format_iso_date(date: datetime) -> str:
    """Format date in ISO format."""
    return date.isoformat()
```

2. `/tools/`: Development and build tools
```python
# Example: tools/doc_validator.py
def validate_docs(path: str) -> bool:
    """Validate documentation standards."""
    return True
```

3. `/tests/utils/`: Test-specific utilities
```python
# Example: tests/utils/db_test_utils.py
def setup_test_db():
    """Setup test database."""
    pass
```

### Directory Structure
```
/project_root
├── utils/                  # Application utilities
│   ├── __init__.py
│   ├── date_utils.py      # Date handling
│   ├── string_utils.py    # String manipulation
│   └── email_utils.py     # Email processing
│
├── tools/                  # Development tools
│   ├── __init__.py
│   ├── doc_validator.py   # Documentation validation
│   ├── setup.sh          # Setup scripts
│   ├── test_runner.py    # Test execution utilities
│   └── standards/        # Project standards
│
└── tests/
    └── utils/             # Test utilities
        ├── __init__.py
        ├── db_test_utils.py
        └── email_test_utils.py
```

### Development Tools

We will use the following development tools, organized by purpose:

1. **Code Quality**:
   - `black`: Code formatting (primary)
   - `pylint`: Comprehensive linting
   - `mypy`: Static type checking
   - `bandit`: Security checks

2. **Testing**:
   - `pytest`: Test framework
   - `pytest-cov`: Coverage reporting
   - `pytest-mock`: Mocking support
   - `pytest-asyncio`: Async test support
   - `pytest-faker`: Test data generation
   - `factory-boy`: Test factory patterns
   - `faker`: Test data generation

3. **Development Workflow**:
   - `pre-commit`: Git hooks management
   - All hooks must be defined in `.pre-commit-config.yaml`
   - Hooks must not block development (use `--allow-missing-config`)

### Usage Guidelines

1. `/utils/`:
   - General-purpose utilities used in application code
   - Pure functions with no side effects
   - No development tool dependencies
   - Must be importable without dev dependencies

2. `/tools/`:
   - Build scripts and development utilities
   - Documentation validators
   - Code generators
   - Can have development dependencies
   - Must be isolated from application code

3. `/tests/utils/`:
   - Test helpers and fixtures
   - Mock data generators
   - Test-specific utilities
   - Can depend on test packages

### Development Dependencies

Development dependencies must be:
1. Explicitly versioned
2. Documented in pyproject.toml
3. Organized by purpose (quality, testing, workflow)
4. Minimal and non-overlapping in functionality
5. Configured via pyproject.toml when possible

## Consequences

### Positive
1. Clear separation of concerns
2. Better code organization
3. Follows industry standards
4. Easier maintenance
5. Explicit tooling decisions
6. Standardized development environment

### Negative
1. Need to update existing imports
2. Migration effort required
3. May need to refactor some utilities
4. Must maintain tool configurations
5. Must keep development dependencies up to date

## Related
- ADR-0013: Minimalist CI/CD Pipeline
- ADR-0010: Documentation Standards Organization
