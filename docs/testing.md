# Testing Strategy

This document outlines the testing strategy for the Marian project, explaining our approach to different types of tests and why we made these choices.

## Testing Philosophy

Our testing approach prioritizes reliability and maintainability over theoretical purity. We've found that while unit tests with mocks are valuable in some contexts, they can be problematic when testing complex API integrations.

### Why We Don't Mock the Claude API

We deliberately avoid mocking the Claude API for several reasons:

1. **Complexity**: The Claude API has nuanced behavior that's difficult to mock correctly
2. **Maintenance Burden**: Mock tests often break when the API changes
3. **False Positives**: Mocks might pass even when real integration would fail
4. **False Negatives**: Tests might fail due to incorrect mock setup
5. **Time Investment**: Setting up good mocks often takes more time than writing integration tests

### Our Testing Approach

Instead, we use a hybrid approach:

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
   - Example: `test_semantic_search.py`

3. **Test Fixtures** (`tests/conftest.py`):
   - Provide reusable test data
   - Cache API responses where appropriate
   - Reduce test execution time
   - Minimize API costs

## Test Categories

### 1. Pure Function Tests
- No external dependencies
- Fast execution
- High reliability
- Test core logic and edge cases
- Examples:
  * Semantic search threshold logic
  * JSON response parsing
  * Input validation
  * Error handling

### 2. API Integration Tests
- Located in: `tests/test_*.py`
- Purpose: Verify core API functionality
- Requirements: Valid API key
- When to run: Pre-deployment, major changes
- Skip gracefully if API unavailable

### 3. Database Tests
- Located in: `tests/test_email_reports.py`
- Use SQLite in-memory database
- Test data models and queries
- Fast and reliable

## Best Practices

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

## Running Tests

1. Run all tests:
   ```bash
   pytest
   ```

2. Run only pure function tests:
   ```bash
   pytest tests/test_*_pure.py
   ```

3. Run with output:
   ```bash
   pytest -s
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
