# 17. Utils and Tools Organization

Date: 2024-12-31

## Status

Proposed

## Revision History
1.0.0 (2024-12-31) @dev
- Initial version
- Defined utils vs tools structure
- Added migration plan

## Context
- Project needs clear separation between application utilities and development tools
- Current structure mixes these concerns
- Need to follow industry standards for better maintainability

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
│   └── standards/        # Project standards
│
└── tests/
    └── utils/             # Test utilities
        ├── __init__.py
        ├── db_test_utils.py
        └── email_test_utils.py
```

### Usage Guidelines

1. `/utils/`:
   - General-purpose utilities used in application code
   - Pure functions with no side effects
   - No development tool dependencies

2. `/tools/`:
   - Build scripts and development utilities
   - Documentation validators
   - Code generators
   - Can have development dependencies

3. `/tests/utils/`:
   - Test helpers and fixtures
   - Mock data generators
   - Test-specific utilities

## Consequences

### Positive
1. Clear separation of concerns
2. Better code organization
3. Follows industry standards
4. Easier maintenance

### Negative
1. Need to update existing imports
2. Migration effort required
3. May need to refactor some utilities

### Mitigation
1. Create clear migration plan
2. Update imports gradually
3. Add automated tests for utilities

## References
- [Python Application Layouts](https://realpython.com/python-application-layouts/)
- [FastAPI Project Structure](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
