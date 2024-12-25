# Testing Guide

## Core Testing Principles

### 1. Data Model Validation
- All tests must validate against the data model defined in `database_schema.md`
- Data model is the single source of truth
- Test structure follows data model hierarchy:
  1. Schema conformance tests
  2. Data integrity tests
  3. Business logic tests
  4. Integration tests

### 2. Test Preservation
- Existing tests must not be modified without approval
- Document any proposed changes thoroughly
- Maintain backward compatibility
- Prefer test duplication over removal

### 3. Test Coverage Requirements
- All new features require corresponding tests
- Integration tests preferred over unit tests
- Real API calls used instead of mocks
- Document test coverage gaps

## Test Categories

### 1. Data Model Tests
Located in `tests/test_data_model.py`

#### Schema Validation
- Verify database schema matches data model
- Validate field types and constraints
- Check index definitions
- Confirm foreign key relationships

#### Data Integrity
- Enforce required fields
- Validate data formats
- Check constraint enforcement
- Verify cascade behaviors

#### Model Consistency
- Test code models match schema
- Verify serialization formats
- Validate API request/response formats
- Check migration integrity

### 2. Integration Tests
Located in `tests/test_integration.py`

#### Email Processing
- Gmail API authentication
- Email retrieval and storage
- Label management
- Thread handling
- Metadata extraction

#### Analysis Pipeline
- Email content analysis
- Priority scoring
- Action detection
- Category assignment
- Summary generation

### 3. Catalog Tests
Located in `tests/test_catalog.py`

#### Entry Management
- Create catalog entries
- Update existing entries
- Archive/restore entries
- Delete entries (with approval)
- Validate entry schema

#### Search and Retrieval
- Full-text search
- Category filtering
- Tag-based search
- Metadata queries
- Combined search criteria

#### Semantic Checks
- Similar items detection
  ```python
  # Test similar items detection
  def test_similar_items():
      # Add original item
      add_item("Python Programming Guide", "A comprehensive guide to Python programming")
      
      # Try adding semantically similar items
      result = add_item("Python Tutorial", "A complete tutorial for Python programming")
      assert result.similarity_detected == True
      assert result.similarity_score > 0.8
  ```

- Tag similarity detection
  ```python
  # Test similar tags detection
  def test_similar_tags():
      # Create original tag
      create_tag("programming")
      
      # Try creating semantically similar tag
      result = create_tag("coding")
      assert result.similar_tags == ["programming"]
      assert result.similarity_score > 0.7
  ```

- Archived items handling
  ```python
  # Test archived items detection
  def test_archived_items():
      # Add and archive an item
      item = add_item("Python Guide", "Guide to Python")
      archive_item(item.id)
      
      # Try adding similar item
      result = add_item("Python Tutorial", "Tutorial for Python")
      assert result.archived_similar_items == [item.id]
  ```

### 4. Database Tests
Located in `tests/test_database.py`

#### Schema Tests
- Table creation
- Field constraints
- Index verification
- Foreign key relationships
- Default values

#### Data Operations
- CRUD operations
- Transaction handling
- Concurrent access
- Error conditions
- Data migration

## Test Implementation

### Test Structure
```python
def test_feature_name():
    """
    Test description explaining:
    1. What is being tested
    2. Expected behavior
    3. Success criteria
    """
    # Setup
    initial_state = setup_test_state()
    
    # Action
    result = perform_test_action()
    
    # Assert
    assert_expected_outcome(result)
    verify_side_effects()
```

### Test Documentation
Each test file must include:
1. Purpose of test suite
2. Prerequisites
3. Test categories
4. Expected outcomes
5. Known limitations

## Running Tests

### Local Development
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_catalog.py

# Run with coverage
pytest --cov

# Generate coverage report
pytest --cov --cov-report=html
```

### CI/CD Pipeline
- Tests run automatically on push
- Coverage reports generated
- Results posted to PR
- Required checks must pass

## Test Data Management

### Test Data Guidelines
1. Use realistic but sanitized data
2. Maintain test data versioning
3. Document data dependencies
4. Clean up test data after runs

### Test Database
- Separate test database
- Reset before each test
- Populated with known state
- Cleaned up after tests

## Troubleshooting Tests

### Common Issues
1. API rate limiting
2. Database connection errors
3. Test data inconsistencies
4. Timing-dependent failures

### Resolution Steps
1. Check API quotas
2. Verify database state
3. Review test logs
4. Check test data
5. Validate assumptions
