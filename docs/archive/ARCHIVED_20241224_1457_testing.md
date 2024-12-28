# Testing Strategy

## Overview
Our testing approach focuses on integration testing with real API calls to validate the actual behavior of the application. Instead of complex mocking setups, we test against the production APIs to ensure our code works as expected in real-world conditions.

## Testing Guidelines and Standards

## Critical Guidelines

1. **Test Preservation Policy**
   - **NEVER** remove or modify existing tests without explicit permission
   - This includes:
     - Test cases and assertions
     - Test helper functions
     - Test documentation and comments
     - Test output formatting
     - Test metrics and counting
   - If a test seems redundant or unnecessary, document why and get approval before removing
   - Prefer duplicating important test cases over removing them
   - Always maintain backward compatibility in test suites

2. **Test Addition Policy**
   - **NEVER** add new test functionality without explicit approval
   - This includes:
     - New test files or suites
     - Test frameworks or libraries
     - Test helper functions
     - Test output formatting changes
     - Changes to test running process
   - Always propose and get approval before:
     - Adding new test dependencies
     - Creating new test files
     - Modifying test output format
     - Adding new test categories
     - Changing test infrastructure
   - Document the purpose and coverage of new tests

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

## Semantic Checking Tests

### Catalog Item Semantic Checks

Test the semantic similarity detection for catalog items:

1. Test Similar Items Detection
   ```
   # Add original item
   add "Python Programming Guide" - "A comprehensive guide to Python programming"
   
   # Try adding semantically similar items
   add "Python Tutorial" - "A complete tutorial for Python programming"
   add "Guide to Programming in Python" - "Learn Python programming from scratch"
   ```
   - Verify that semantic similarity is detected
   - Check similarity scores are reasonable
   - Confirm options are presented in interactive mode

2. Test Different Items
   ```
   # Add items with different meanings
   add "Python Programming Guide" - "A guide to Python programming"
   add "Python Snake Care" - "Guide to caring for python snakes"
   ```
   - Verify that items with different meanings are allowed
   - Check that false positives are minimized

3. Test Archived Items
   ```
   # Add and archive an item
   add "Python Guide" - "Guide to Python"
   archive "Python Guide"
   
   # Try adding similar item
   add "Python Tutorial" - "Tutorial for Python"
   ```
   - Verify option to restore archived item is presented
   - Check that restoration works correctly

### Tag Semantic Checks

Test the semantic similarity detection for tags:

1. Test Similar Tags Detection
   ```
   # Create original tag
   create_tag programming
   
   # Try creating semantically similar tags
   create_tag coding
   create_tag development
   ```
   - Verify semantic similarity is detected
   - Check similarity scores
   - Test interactive mode options

2. Test Tag Application
   ```
   # Create item and apply similar tags
   add "Test Item" - "Content"
   tag "Test Item" programming
   tag "Test Item" coding
   ```
   - Verify similar tag detection during tagging
   - Test option to use existing tag
   - Check tag reuse vs. new tag creation

3. Test Archived Tags
   ```
   # Create and archive tag
   create_tag programming
   archive_tag programming
   
   # Try using similar tag
   create_tag coding
   ```
   - Verify archived tag detection
   - Test restoration option
   - Check tag state after restoration

### Edge Cases

1. Test Empty Database
   ```
   # Clear database
   # Try semantic checks with no existing items/tags
   add "First Item" - "Content"
   create_tag first
   ```
   - Verify graceful handling with no items to compare

2. Test Special Characters
   ```
   add "Python (Programming)" - "Content"
   add "Python [Code]" - "Content"
   create_tag "programming/coding"
   ```
   - Verify semantic checking works with special characters

3. Test Long Text
   ```
   # Add items with long titles/content
   add "Very long title..." - "Very long content..."
   create_tag "very_long_tag_name"
   ```
   - Verify semantic checking handles long text properly

### Performance Testing

1. Test Response Time
   - Measure time taken for semantic checks
   - Verify reasonable performance with:
     - Large number of existing items
     - Long text content
     - Multiple concurrent checks

2. Test API Usage
   - Monitor Claude API calls
   - Verify efficient use of tokens
   - Check error handling for API limits

### Integration Testing

1. Test with Other Features
   - Verify semantic checking works with:
     - Search functionality
     - List operations
     - Tag management
     - Item archival/restoration

2. Test CLI vs Interactive Mode
   - Verify behavior differences
   - Check force flag functionality
   - Test user interaction flows

### Error Cases

1. Test API Failures
   - Simulate Claude API errors
   - Verify graceful degradation
   - Check user feedback

2. Test Invalid Input
   - Test with malformed input
   - Verify error handling
   - Check recovery process

### Configuration Testing

1. Test Similarity Threshold
   - Try different threshold values
   - Verify impact on matching
   - Test threshold edge cases

2. Test Model Parameters
   - Test different Claude models
   - Verify temperature settings
   - Check token limit handling

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
