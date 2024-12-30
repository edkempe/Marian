# Tests Directory

**Version:** 1.0.0
**Status:** Authoritative

> Test suite for the Marian project, including unit tests, integration tests, and test utilities.

## Overview
- **Purpose**: Ensure code quality
- **Stability**: Stable
- **Maintenance**: Active
- **Python**: >= 3.12

## Directory Structure
```
/tests/
├── README.md              # This file
├── test_email.py         # Email model tests
├── test_catalog.py       # Catalog model tests
└── test_dependencies.py  # Dependency tests
```

## Core Components
1. **Model Tests**
   - Purpose: Test domain models
   - When to use: Model changes
   - Location: `test_*.py`

2. **Integration Tests**
   - Purpose: Test component interactions
   - When to use: API changes
   - Location: `test_*_integration.py`

## Version History
- 1.0.0 (2024-12-28): Initial test structure
  - Created core test suites
  - Added test utilities
  - Established test patterns
