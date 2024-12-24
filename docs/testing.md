# Testing Strategy

## Overview
Our testing approach focuses on integration testing with real API calls to validate the actual behavior of the application. Instead of complex mocking setups, we test against the production APIs to ensure our code works as expected in real-world conditions.

## Test Structure

### Integration Tests (`tests/test_integration.py`)
Primary test suite that validates core functionality using real API calls:

1. **Gmail Authentication**
   - Validates API credentials
   - Confirms service connection
   - Verifies user profile access

2. **Label Operations**
   - Lists available Gmail labels
   - Validates system label access (INBOX, SENT, etc.)
   - Tests label ID retrieval

3. **Email Operations**
   - Fetches recent emails
   - Tests date-based filtering
   - Tests label-based filtering
   - Validates email content retrieval

4. **Email Processing**
   - Tests email parsing
   - Validates database storage
   - Verifies label tracking

## Running Tests

```bash
# Run all integration tests
pytest -v tests/test_integration.py

# Run specific test categories
pytest -v tests/test_integration.py -k "test_gmail_authentication"
pytest -v tests/test_integration.py -k "test_label_operations"
pytest -v tests/test_integration.py -k "test_email"
```

## Test Requirements

1. **Gmail API Access**
   - Valid OAuth2 credentials
   - Required scopes:
     - `gmail.readonly`
     - `gmail.modify`

2. **Database Setup**
   - SQLite database configured
   - Tables created for:
     - Emails
     - Labels
     - Analysis results

## Best Practices

1. **Data Handling**
   - Tests use recent emails (last 7 days)
   - Limited to processing 3 emails per test
   - Avoids modifying existing emails

2. **Output and Logging**
   - Tests provide detailed output:
     - Authentication status
     - Available labels
     - Email details
     - Processing results

3. **Error Handling**
   - Tests include error cases
   - Validates API error responses
   - Checks database constraints

## Adding New Tests

When adding new integration tests:

1. **Test Real Functionality**
   ```python
   def test_new_feature():
       # Initialize API
       gmail = GmailAPI()
       
       # Make real API calls
       result = gmail.some_operation()
       
       # Validate actual results
       assert result is not None
       print(f"Operation result: {result}")
   ```

2. **Include Output**
   - Add print statements for key information
   - Show relevant data for debugging
   - Log important operations

3. **Handle Resources**
   - Use test database session
   - Clean up after tests
   - Consider API rate limits

## Future Improvements

1. **Test Data Management**
   - Create dedicated test labels
   - Use specific test emails
   - Implement cleanup procedures

2. **Performance Testing**
   - Add timing measurements
   - Test batch operations
   - Monitor API usage

3. **Continuous Integration**
   - Add CI pipeline support
   - Automate test credentials
   - Schedule regular test runs
