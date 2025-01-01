# ADR-0018: Testing API Pagination and Mock Configuration

## Status
Accepted

## Context
On January 1, 2025, we encountered a critical issue where tests in `test_get_mail.py` were hanging indefinitely. After investigation, we discovered this was caused by incomplete mocking of the Gmail API's pagination mechanism. The test suite would hang while waiting for a response from the `list_next` method, which wasn't properly mocked.

This issue highlighted several important aspects of testing APIs with pagination:
1. API clients often implement pagination using helper methods (like `list_next` in Gmail's API)
2. Incomplete mocking can lead to tests that hang rather than fail explicitly
3. The relationship between the main API call and its pagination mechanism isn't always obvious

## Decision
We will implement the following guidelines for testing APIs with pagination:

1. **Complete Mock Configuration**
   ```python
   # INCORRECT - Only mocks the initial response
   service.users().messages().list().execute.return_value = {'messages': data}
   
   # CORRECT - Mocks both initial response and pagination
   service.users().messages().list().execute.return_value = {'messages': data}
   service.users().messages().list_next.return_value = None  # Indicates no more pages
   ```

2. **Test Helper Functions**
   - Create dedicated test utilities for common API mock setups
   - Document the complete chain of API calls that need to be mocked
   - Include pagination-related mocks in these utilities

3. **Documentation Requirements**
   - All API client tests must document their pagination strategy
   - Mock setup functions must list all methods being mocked
   - Comments should explain the expected behavior of pagination-related code

4. **Test Timeouts**
   - Add explicit timeouts to tests that interact with APIs
   - Configure pytest to fail tests that run longer than expected
   - Add the `@pytest.mark.timeout(seconds=5)` decorator to API tests

## Implementation
1. Updated `gmail_utils.py` to properly mock pagination:
   ```python
   def setup_mock_messages(service, messages_data):
       """Set up mock messages response with pagination handling.
       
       Args:
           service: Mock Gmail service
           messages_data: List of message dictionaries to return
       """
       list_response = {'messages': messages_data}
       service.users().messages().list().execute.return_value = list_response
       
       # Mock list_next to return None (no more pages)
       service.users().messages().list_next.return_value = None
   ```

2. Added test timeout configuration to `pytest.ini`:
   ```ini
   [pytest]
   # Fail tests that take longer than 30 seconds
   timeout = 30
   ```

## Consequences

### Positive
- Tests fail fast instead of hanging indefinitely
- Clear documentation of API mock requirements
- Reduced risk of incomplete mock configurations
- Better test maintainability

### Negative
- More complex mock setup required
- Additional documentation overhead
- Need to maintain more test utilities

### Risks
- Mock configurations might need updates when API versions change
- Test timeouts might need adjustment for different environments

## References
- [Gmail API Pagination Documentation](https://developers.google.com/gmail/api/guides/pagination)
- [Issue #XXX: Test Suite Hanging](link-to-issue)
- [Commit XXX: Fix API Pagination Tests](link-to-commit)

## Notes
This pattern of incomplete mock configuration was found in several tests. We should:
1. Review all API tests for similar issues
2. Add test utilities for other paginated APIs
3. Consider adding static analysis to catch missing pagination mocks
