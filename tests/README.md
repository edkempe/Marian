# Jexi Tests

**Version:** 1.0.1
**Status:** Authoritative

> Test suite for the Jexi project, including unit tests, integration tests, and test utilities.

## Overview
- **Purpose**: Ensure code quality
- **Stability**: Stable
- **Maintenance**: Active
- **Python**: >= 3.12

## Directory Structure
```
/tests/
├── README.md              # This file
├── test_database_utils.py # Database utilities tests
├── test_email.py         # Email model tests
├── test_catalog.py       # Catalog model tests
├── test_dependencies.py  # Dependency tests
└── test_imports.py       # Import validation tests
```

## Test Categories
1. **Core Tests**
   - `test_email_*.py`: Email processing tests
   - `test_analysis_*.py`: Content analysis tests
   - `test_gmail_*.py`: Gmail API tests

2. **Marian Tests**
   - `test_catalog_*.py`: Marian's catalog system tests
   - `test_librarian_*.py`: Marian's core functionality tests
   
3. **Support Tests**
   - `test_database_utils.py`: Database seeding and migration tests
   - `test_utils_*.py`: Utility function tests
   - `test_migrations_*.py`: Database migration tests
   - `test_imports.py`: Import validation and hygiene tests

## Running Tests

### All Tests
```bash
pytest -v
```

### Specific Categories
```bash
# Run database utility tests
pytest -v tests/test_database_utils.py

# Run email tests
pytest -v tests/test_email*.py

# Run catalog tests
pytest -v tests/test_catalog*.py
```

### Test Coverage
```bash
pytest --cov=. tests/
```

## Test Environment

### Setup
1. Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

2. Configure test environment:
   ```bash
   cp .env.test .env
   ```

### Database Tests
Database tests use:
- Temporary SQLite databases
- Test-specific configurations
- Automated cleanup

## Version History
- 1.0.1 (2024-12-30): Added database utilities test suite
  - Added comprehensive database seeding tests
  - Added migration utility tests
  - Added schema validation tests
  - Updated documentation
- 1.0.0 (2024-12-28): Initial test structure
  - Created core test suites
  - Added test utilities
  - Established test patterns
