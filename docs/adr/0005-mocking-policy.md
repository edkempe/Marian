# ADR 0005: Mocking Policy in Test Code

## Status
Proposed

## Context
The project needs a clear policy on mocking in tests. While mocking can simplify testing, it can also make tests brittle and less reliable. We need to establish when real implementations should be used and when mocking might be appropriate.

## Decision

### General Policy
Mock usage is prohibited by default. All tests should use real implementations unless explicitly justified and documented in this ADR.

### External API Testing Strategy

1. **Default Approach: Use Real APIs**
   - Prefer real API calls for testing
   - Use test accounts for read/write operations
   - Implement proper cleanup of test data
   - Validate response schemas

2. **Required Test Infrastructure**
   - Network connectivity validation
   - API availability checks
   - Schema validation
   - Test data management
   - Response recording for analysis

3. **Test Account Management**
   - Read-only operations: Use real credentials when safe
   - Write operations: Require dedicated test accounts
   - Secure credential storage
   - Clear separation from production

### Permitted Mock Usage

Mocking is permitted only when ALL of the following conditions are met:

1. **Technical Requirements**
   - API has no test/sandbox environment
   - API has prohibitive rate limits for testing
   - API requires complex infrastructure setup
   - API has significant cost implications

2. **Documentation Requirements**
   - Document why mocking is necessary
   - Provide example of real API responses
   - Maintain schema validation
   - Regular validation against real API

3. **Implementation Requirements**
   - Use schema validation
   - Implement error scenarios
   - Match real API behavior
   - Regular updates with API changes

### Prohibited Mock Usage

1. **Internal Systems**
   - Database operations
   - File system operations
   - Internal services
   - Configuration systems

2. **Simple External Services**
   - Basic HTTP endpoints
   - Well-documented APIs
   - Services with test environments
   - Free/low-cost APIs

### API Stability Assessment

Before deciding on mocking vs. real API testing, evaluate:

1. **API Stability Criteria**
   - API version lifecycle and deprecation policy
   - Frequency of breaking changes
   - Quality of API documentation
   - Historical reliability metrics
   - Provider's communication of changes

2. **Version Management**
   - Document target API versions
   - Track API deprecation schedules
   - Monitor API changelog
   - Subscribe to API status updates
   - Regular compatibility checks

Example: Gmail API
```python
# API Version Information
GMAIL_API_VERSION = "v1"
GMAIL_API_MIN_SUPPORTED = "2018-12-01"
GMAIL_API_DEPRECATION_DATE = None  # Stable API with no planned deprecation
GMAIL_API_CHANGELOG = "https://developers.google.com/gmail/api/releases"
```

3. **Stability-Based Testing Strategy**

   a. Stable APIs (e.g., Gmail API):
      - Prefer real API calls
      - Focus on testing our implementation
      - Maintain version compatibility checks
      - Monitor for rare API issues

   b. Volatile APIs:
      - Consider selective mocking
      - Record real responses
      - Version response schemas
      - Frequent compatibility validation

4. **API Health Monitoring**
```python
def verify_api_compatibility():
    """Verify API version and features."""
    response = service.users().getProfile().execute()
    api_version = response.get('api_version')
    assert api_version >= GMAIL_API_MIN_SUPPORTED, (
        f"API version {api_version} not supported. "
        f"Minimum supported: {GMAIL_API_MIN_SUPPORTED}"
    )
```

### Stability Impact on Mock Usage

1. **Stable APIs (Like Gmail)**
   - Mock only when absolutely necessary
   - Real API calls are predictable
   - API errors are rare and well-documented
   - Version changes are announced well in advance

2. **Testing Focus**
   - Validate our code against real API
   - Test error handling in our implementation
   - Verify our API usage patterns
   - Monitor our API quota usage

### Implementation Guidelines

1. **API Test Setup**
```python
@pytest.fixture
def api_test():
    """Setup for API testing."""
    check_connectivity()
    validate_credentials()
    return test_manager
```

2. **Test Data Management**
```python
with test_manager.test_data() as data:
    # Test operations
    # Automatic cleanup after test
```

3. **Schema Validation**
```python
errors = validate_response_schema(response, EXPECTED_SCHEMA)
assert not errors, f"Schema validation errors: {errors}"
```

4. **Response Recording**
```python
test_manager.save_test_response("scenario_name", response)
```

5. **Version Verification**
```python
@pytest.fixture(scope="session")
def api_version_check():
    """Verify API version compatibility."""
    verify_api_compatibility()
    check_deprecation_status()
    validate_required_features()
```

### Source of Truth Hierarchy

1. **Configuration (`/config`)**
   - `api_versions.json`: Source of truth for API compatibility
     - Supported versions
     - Required features
     - Breaking changes
     - Update history
   - Used by both production and test code
   - Must be reviewed for any API changes
   - Drives version validation in shared libraries

2. **Shared Libraries (`/shared_lib`)**
   - Version validation logic
   - Compatibility checking
   - Feature verification
   - Used across all components

3. **Tests (`/tests`)**
   - Build on shared version validation
   - Add test-specific validation
   - Verify API compatibility
   - Track feature coverage

Example Configuration:
```json
{
    "gmail": {
        "current_version": "v1",
        "min_supported_version": "2018-12-01",
        "features_required": [
            "users.messages.list",
            "users.labels.create"
        ]
    }
}
```

Example Shared Library Usage:
```python
def initialize_api_client():
    """Initialize API client with version validation."""
    verify_api_compatibility()
    check_required_features()
    return create_client()
```

Example Test Usage:
```python
def test_api_feature():
    """Test specific API feature."""
    verify_api_version()  # From shared lib
    validate_test_requirements()  # Test specific
    perform_test()
```

### Required Tools

1. **Connectivity Testing**
   - Network availability check
   - API endpoint validation
   - Timeout handling

2. **Schema Validation**
   - Response structure validation
   - Type checking
   - Required field validation

3. **Test Data Management**
   - Resource cleanup
   - State tracking
   - History maintenance

4. **Response Recording**
   - Sample storage
   - Comparison utilities
   - Schema evolution tracking

### Key Testing Principles

1. **Predictability Over Convenience**
   - Prefer predictable, stable APIs over mocking
   - Real API calls are more reliable for stable services
   - Focus on testing our implementation, not the API
   - Errors are more likely in our code than stable APIs

2. **Test Account Strategy**
   - Use real credentials for read-only operations when safe
   - Dedicated test accounts for write operations
   - Simple > Complex: Avoid unnecessary test infrastructure
   - Document credential management approach

3. **API Reliability Assessment**
   - Consider API's historical reliability
   - Document API's update frequency
   - Track API's communication channels
   - Monitor API's status page

4. **Test Data Management**
   - Implement proper cleanup
   - Track test resource creation
   - Use context managers for cleanup
   - Document test data requirements

### Error Handling Strategy

1. **Focus Areas**
   - Our code's error handling
   - Our API usage patterns
   - Our request formatting
   - Our response processing

2. **API Error Scenarios**
   - Network connectivity issues
   - Authentication failures
   - Rate limiting
   - Malformed requests

3. **Response Validation**
   - Schema validation
   - Type checking
   - Required fields
   - Data constraints

### Implementation Requirements

1. **Version Management**
```python
# Required version information
API_VERSION_INFO = {
    "version": "v1",
    "min_supported": "2018-12-01",
    "changelog_url": "...",
    "features": ["..."],
}
```

2. **Connectivity Check**
```python
@pytest.fixture(scope="session")
def api_connectivity():
    """Verify API connectivity."""
    check_network()
    verify_api_access()
    validate_credentials()
```

3. **Test Data Cleanup**
```python
@contextmanager
def test_resources():
    """Manage test resources."""
    created = []
    try:
        yield created
    finally:
        cleanup_resources(created)
```

### Documentation Requirements

1. **API Information**
   - Target API version
   - Required features
   - Breaking changes
   - Update frequency

2. **Test Coverage**
   - Happy path scenarios
   - Error handling
   - Edge cases
   - Performance considerations

3. **Maintenance Guide**
   - Version update process
   - Breaking change handling
   - Test data management
   - Credential rotation

### Decision Criteria for Mocking

1. **Do Not Mock When**:
   - API is stable (like Gmail)
   - API has good documentation
   - API has consistent behavior
   - API has high reliability
   - API has reasonable rate limits
   - API provides test endpoints

2. **Consider Mocking When**:
   - API is unstable/evolving
   - API has poor documentation
   - API has inconsistent behavior
   - API has severe rate limits
   - API lacks test endpoints
   - API has significant costs

## Consequences

### Positive
- More reliable tests
- Better test coverage
- Real-world behavior testing
- Clear testing strategy
- Maintainable test suite

### Negative
- More complex test setup
- Need for test accounts
- Network dependencies
- Slightly slower tests

## Compliance

### Existing Code
All existing mock usage must be:
1. Justified according to this policy
2. Documented in this ADR
3. Refactored to use real implementations where possible

### New Code
New tests must:
1. Default to real implementations
2. Document any mock usage
3. Implement required test infrastructure
4. Follow schema validation requirements

## Implementation Plan

1. Create test utilities
   - Network validation
   - Schema validation
   - Test data management
   - Response recording

2. Setup test infrastructure
   - Test accounts
   - Credential management
   - Data cleanup

3. Migrate existing tests
   - Review current mock usage
   - Implement real API tests
   - Document necessary mocks

4. Monitor and maintain
   - Regular schema validation
   - API compatibility checks
   - Test data cleanup
   - Response recording updates
