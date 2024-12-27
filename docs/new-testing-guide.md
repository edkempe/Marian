# NEW Testing Guide and Strategy

> **Documentation Role**: This guide is a supporting document for testing all AI components in the Jexi project. See `ai-architecture.md` for the complete documentation hierarchy.

## Overview
This document outlines the testing strategy and guidelines for the Jexi project, explaining our approach to testing different AI components and their interactions.

## Core Testing Principles

### 1. Test What Matters
- Focus on critical user paths
- Test complex AI interactions
- Cover edge cases and error handling
- Validate data integrity

### 2. Test Close to Production
- Minimize mocking where possible
- Use realistic test data
- Match production configurations
- Test actual AI integrations

### 3. Test for Maintainability
- Keep tests simple and focused
- Document test rationale
- Make test failures clear
- Update tests with AI behavior changes

### 4. Test for Reliability
- Avoid flaky tests
- Handle async AI operations properly
- Clean up test data
- Isolate test environments

## Testing Approach

### Why We Don't Mock the Claude API
We deliberately avoid mocking the Claude API for several reasons:

1. **Complexity**: The Claude API has nuanced behavior that's difficult to mock correctly
2. **Maintenance Burden**: Mock tests often break when the API changes
3. **False Positives**: Mocks might pass even when real integration would fail
4. **False Negatives**: Tests might fail due to incorrect mock setup
5. **Time Investment**: Setting up good mocks often takes more time than writing integration tests

### Our Hybrid Approach

1. **Pure Function Tests** (`tests/test_*_pure.py`):
   - Test functions that don't depend on external services
   - Focus on JSON parsing, data transformation, etc.
   - Run quickly and reliably
   - Examples:
     * `test_semantic_search_pure.py`: Tests semantic search logic without API calls
     * `test_json_extraction.py`: Tests JSON parsing utilities
     * `test_pure_functions.py`: Tests other utility functions

2. **Integration Tests** (`tests/test_*.py`):
   - Use real API calls for core functionality
   - Provide high confidence in actual behavior
   - Serve as documentation of real API usage
   - Run as part of CI/CD pipeline
   - Skip tests gracefully if API is unavailable

3. **Test Fixtures** (`tests/conftest.py`):
   - Provide reusable test data
   - Cache API responses where appropriate
   - Reduce test execution time
   - Minimize API costs

## Test Categories

### 1. Data Model Tests
Located in `tests/test_data_model.py`

#### Schema Validation
- Verify data models match schema
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

### 2. API Integration Tests
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
- Use SQLite in-memory database
- Test data models and queries
- Fast and reliable

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

## Best Practices

### Example Test Implementations

1. **Pure Function Tests**:
   ```python
   def test_semantic_search_disabled():
       """Test that semantic search returns empty list when disabled."""
       chat = CatalogChat(mode='test', enable_semantic=False)
       items = [CatalogItem(title="Python Tutorial")]
       matches = chat.get_semantic_matches("python", items)
       assert len(matches) == 0
   ```

2. **API Integration Tests**:
   ```python
   @pytest.fixture(scope="session", autouse=True)
   def verify_claude_api():
       """Verify Claude API before running tests."""
       try:
           # API verification code
           response = client.messages.create(...)
           if "API_TEST" not in response:
               pytest.skip("API test failed")
       except Exception as e:
           pytest.skip(f"API unavailable: {str(e)}")
   ```

3. **Using Fixtures**:
   ```python
   @pytest.fixture(scope="session")
   def test_items():
       """Provide test catalog items."""
       return get_test_items()
   ```

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

# Run only pure function tests
pytest tests/test_*_pure.py

# Run with output
pytest -s

# Run coverage on specific module (recommended)
pytest --cov=app_catalog --cov-report=term-missing tests/test_semantic_search_pure.py
```

## Test Environment

1. Required environment variables:
   - `ANTHROPIC_API_KEY`: For API tests
   - `TEST_EMAIL_DB`: For database tests
   - `TEST_ANALYSIS_DB`: For analysis tests

2. Configuration:
   - Test settings in `tests/test_config.py`
   - Database setup in `tests/conftest_db.py`

## Adding New Tests

When adding new tests:

1. **For Core Logic**:
   - Create `test_*_pure.py` file
   - No external dependencies
   - Focus on edge cases
   - Test error handling

2. **For API Features**:
   - Add to existing test file
   - Include API verification
   - Handle API unavailability
   - Document API requirements

3. **For Database Operations**:
   - Use in-memory database
   - Clean up after tests
   - Test transactions and rollbacks

## Continuous Integration

Our CI pipeline:

1. Runs pure function tests first
2. Runs API tests if pure tests pass
3. Requires API key in CI environment
4. Reports test coverage

## Coverage Reporting Best Practices

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

## Future Improvements

1. **Response Caching**:
   - Cache API responses for specific test cases
   - Reduce API costs in CI
   - Speed up test execution

2. **Test Coverage**:
   - Add more pure function tests
   - Improve error scenario coverage
   - Add performance tests

3. **Test Organization**:
   - Better test categorization
   - More detailed test documentation
   - Improved test naming conventions
