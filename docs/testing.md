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

1. **Integration Tests** (`tests/test_minimal.py`):
   - Use real API calls for core functionality
   - Provide high confidence in actual behavior
   - Serve as documentation of real API usage
   - Run as part of CI/CD pipeline

2. **Unit Tests** (for pure functions):
   - Test functions that don't depend on external services
   - Focus on JSON parsing, data transformation, etc.
   - Run quickly and reliably
   - Example: `tests/test_json_extraction.py`

3. **Test Fixtures** (`tests/conftest.py`):
   - Provide reusable test data
   - Cache API responses where appropriate
   - Reduce test execution time
   - Minimize API costs

## Test Categories

### 1. API Integration Tests
- Located in: `tests/test_minimal.py`
- Purpose: Verify core API functionality
- Requirements: Valid API key
- When to run: Pre-deployment, major changes

### 2. Pure Function Tests
- Located in: `tests/test_json_extraction.py`, `tests/test_anthropic_lib.py`
- Purpose: Test utility functions
- No external dependencies
- Run frequently during development

### 3. Database Tests
- Located in: `tests/test_email_reports.py`
- Use SQLite in-memory database
- Test data models and queries
- Fast and reliable

## Best Practices

1. **API Tests**:
   ```python
   def test_email_analysis():
       """Test email analysis with real API calls."""
       try:
           analysis = analyzer.analyze_email(test_email)
           assert analysis is not None
           assert analysis.summary is not None
       except Exception as e:
           pytest.fail(f"Email analysis failed: {str(e)}")
   ```

2. **Pure Function Tests**:
   ```python
   def test_json_extraction():
       """Test JSON extraction from text."""
       input_text = 'Here is JSON: {"key": "value"}'
       json_str, error = extract_json(input_text)
       assert error is None
       assert json_str == '{"key": "value"}'
   ```

3. **Using Fixtures**:
   ```python
   @pytest.fixture(scope="session")
   def api_client():
       """Provide configured API client."""
       return get_anthropic_client()
   ```

## Running Tests

1. Run all tests:
   ```bash
   pytest
   ```

2. Run specific test file:
   ```bash
   pytest tests/test_minimal.py -v
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

1. **For API Features**:
   - Add to `test_minimal.py`
   - Include proper error handling
   - Document API key requirements

2. **For Utility Functions**:
   - Create dedicated test file
   - No external dependencies
   - Focus on edge cases

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
   - Add more edge case tests
   - Improve error scenario coverage
   - Add performance tests

3. **Test Organization**:
   - Better test categorization
   - More detailed test documentation
   - Improved test naming conventions
