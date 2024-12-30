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
Located in `tests/test_catalog.py` and `tests/test_semantic_search_pure.py`

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

#### Semantic Search Tests
Located in `tests/test_semantic_search_pure.py`

##### Pure Function Tests
Tests that don't require external API calls:
- Response validation tests (invalid JSON, missing fields)
- Score filtering tests (threshold-based filtering)
- Index validation tests (invalid indices handling)
- Prompt variation tests (short vs long queries)
- Item type handling tests (strings, CatalogItems, Tags)

Example test structure:
```python
def test_semantic_search_score_filtering():
    """Test filtering of matches based on threshold."""
    chat = CatalogChat(mode='test')
    items = [
        CatalogItem(title="Item 1"),
        CatalogItem(title="Item 2"),
        CatalogItem(title="Item 3")
    ]

    # Mock API response with various scores
    def mock_scores(*args, **kwargs):
        return type('Response', (), {
            'content': [type('Content', (), {'text': '''
                {
                    "matches": [
                        {"index": 0, "score": 0.9, "reasoning": "high match"},
                        {"index": 1, "score": 0.7, "reasoning": "medium match"},
                        {"index": 2, "score": 0.5, "reasoning": "low match"}
                    ]
                }
            '''})]
        })

    chat.client.messages.create = mock_scores

    # Test high threshold
    matches = chat.get_semantic_matches("query", items, threshold=0.8)
    assert len(matches) == 1
    assert matches[0][0].title == "Item 1"
```

##### Coverage Insights
Current coverage for semantic search functionality:
- Overall coverage for `app_catalog.py`: 17%
- Well-covered areas:
  * Semantic search core functionality
  * Error handling for API responses
  * Input validation
- Areas needing coverage:
  * Database operations (lines 246-315)
  * Item management (lines 328-347)
  * Tag management (lines 364-381)
  * Query processing (lines 789-813)
  * Result ranking (lines 913-945)

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

# Run coverage on specific module (recommended)
pytest --cov=app_catalog --cov-report=term-missing tests/test_semantic_search_pure.py

# Run coverage on entire codebase (may be slow)
pytest --cov --cov-report=html
```

### Coverage Reporting Best Practices
1. Focus coverage reporting on specific modules:
   - Run coverage reports on individual modules
   - Target specific test categories
   - Monitor coverage trends over time

2. Handle known coverage reporting issues:
   - Coverage tool may appear to stall on large codebases
   - Use module-specific coverage reporting
   - Set reasonable timeouts for CI/CD pipelines

3. Coverage improvement strategy:
   - Identify critical paths needing coverage
   - Prioritize business logic coverage
   - Document coverage gaps
   - Track coverage metrics in CI/CD

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
