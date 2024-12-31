# 10. Documentation Standards Organization

Date: 2024-12-31

## Status

Accepted

## Revision History
1.0.0 (2024-12-31) @dev
- Initial version with standards consolidation
- Moved all standards to tools/doc_standards.py
- Added validation rules

## Context

Documentation standards and validation were split across multiple locations:

1. `shared_lib/doc_standards.py`: Constants and validation rules
2. `tools/doc_validator.py`: Pre-commit hook for validation
3. `tests/test_process_quality.py`: Duplicate standards and validation

This created several issues:
1. Documentation validation depended on shared_lib, pulling in unnecessary dependencies (like SQLAlchemy)
2. Pre-commit hooks failed due to missing database dependencies
3. Standards were duplicated between validation and testing code
4. No single source of truth for documentation requirements
5. Risk of standards diverging between tests and pre-commit hooks

## Decision

We will consolidate all documentation standards into tools/doc_standards.py:

```
tools/
├── doc_standards.py  # Single source of truth for all standards
└── doc_validator.py  # Pre-commit hook using doc_standards.py

tests/
└── test_process_quality.py  # Uses doc_standards.py for validation
```

### Key Changes

1. **Single Source of Truth**
   - Move all standards to tools/doc_standards.py
   - Remove duplicate constants from test_process_quality.py
   - Make both tests and pre-commit hook use the same code

2. **Break Dependencies**
   - Remove documentation code from shared_lib
   - Make pre-commit hooks independent
   - No more SQLAlchemy dependency

3. **Consistent Standards**
   - One set of required sections
   - One set of validation rules
   - Case-insensitive validation everywhere
   - Same behavior in tests and pre-commit

### Documentation Standards Example

```python
# Required files tracked in one place
REQUIRED_DOCS = {
    "development.md",
    "deployment.md", 
    "testing.md",
    "architecture.md",
    "README.md"
}

# Single source of truth for section requirements
REQUIRED_SECTIONS = {
    "development": ["setup", "workflow", "guidelines"],
    "deployment": ["environment", "configuration", "procedure"],
    "testing": ["setup", "running tests", "writing tests"],
    "architecture": ["overview", "components", "data flow"]
}

# Shared validation logic
def validate_doc(path: Path, doc_type: str, max_lines: int) -> List[str]:
    """Validate a document against standards."""
    errors = []
    content = path.read_text().lower()  # Case-insensitive everywhere
    
    for section in REQUIRED_SECTIONS[doc_type]:
        if section not in content:
            errors.append(f"[ERROR] Missing section: {section}")
    return errors
```

## Consequences

### Positive
1. Single source of truth for all documentation standards
2. Independent pre-commit hooks that don't require full environment
3. No unnecessary dependencies
4. Guaranteed consistency between tests and pre-commit
5. Easier maintenance - change standards in one place
6. Better test coverage of validation code

### Negative
1. Need to update imports in test_process_quality.py
2. One-time migration effort
3. Standards changes now affect both tests and pre-commit

### Mitigation
1. Keep standards in one file for clarity
2. Add tests to verify validation behavior
3. Document standards clearly in doc_standards.py

## References
- [Python Pre-commit Hooks](https://pre-commit.com/)
- [Python Documentation Standards](https://www.python.org/dev/peps/pep-0257/)
- [DRY (Don't Repeat Yourself)](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
