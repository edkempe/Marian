# Testing Guide and Strategy

> **Documentation Role**: This guide is a supporting document for testing all AI components in the Jexi project, which aims to develop a conversational AI assistant that integrates with various data sources and services. See `ai-architecture.md` for the complete documentation hierarchy.

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

## Test Categories

### 1. Development AI (Cassy) Testing
> These sections cover how we use Cassy to write and maintain tests

#### Test Development Practices
- Use test-driven development (TDD) where appropriate
- Write clear test descriptions
- Follow consistent naming patterns
- Document test rationale
- Include AI prompts that generated tests

#### Test Review and Maintenance
- AI-assisted test review
- Verify test coverage
- Update tests when code changes
- Document test changes in session logs
- Track test evolution

#### Test Generation Guidelines
- Provide clear context to Cassy
- Specify test requirements
- Review generated tests
- Validate edge cases
- Document AI assumptions

### 2. Core Assistant (Jexi) Testing
> These sections cover testing Jexi's core functionality

#### User Interaction Tests
Located in `tests/test_jexi_core.py`
- Command understanding
- Response generation
- Context management
- Error handling
- State persistence

#### Task Management Tests
Located in `tests/test_jexi_tasks.py`
- Task creation and updates
- Priority management
- Scheduling logic
- Notification handling
- Task completion

#### Integration Tests
Located in `tests/test_jexi_integration.py`
- Marian API interaction
- External service integration
- Error recovery
- Rate limiting
- Response validation

### 3. Librarian (Marian) Testing
> These sections cover testing Marian's catalog management

#### Catalog Intelligence Tests
Located in `tests/test_catalog_ai.py`
- Query understanding
- Content classification
- Relationship inference
- Search relevance
- Response quality

#### Data Model Tests
Located in `tests/test_models.py`
- Schema compliance
- Data integrity
- Business rules
- Relationship constraints
- Migration handling

#### Source of Truth Tests
Located in `tests/test_source_truth.py`
- Hierarchy validation
- Reference management
- Version control
- Conflict resolution
- Consistency checks

### 4. System Integration Testing
> These sections cover testing interactions between Jexi and Marian

#### End-to-End Tests
Located in `tests/test_e2e.py`
- Complete user workflows
- Cross-AI communication
- Performance metrics
- Error recovery
- State management

#### Data Flow Tests
Located in `tests/test_data_flow.py`
- Information passing
- State synchronization
- Cache management
- Event propagation
- Transaction handling

## Best Practices

### 1. Test Structure
- One concept per test
- Clear setup and teardown
- Descriptive test names
- Documented test rationale

### 2. Test Data
- Use realistic test data
- Clean up after tests
- Avoid data dependencies
- Document data sources

### 3. Test Maintenance
- Update tests with AI behavior changes
- Remove obsolete tests
- Keep tests focused
- Document changes

### 4. Test Performance
- Fast test execution
- Minimal dependencies
- Efficient setup/teardown
- Parallel test support

## Common Test Patterns

### 1. AI Response Testing
```python
def test_ai_response_validation():
    """Test AI response format and content."""
    response = ai.process_query("test query")
    assert_valid_response(response)
    assert response.content is not None
    assert response.confidence >= 0.8
```

### 2. Error Handling
```python
def test_ai_error_recovery():
    """Test AI error handling and recovery."""
    with pytest.raises(AITemporaryError):
        ai.process_with_retry(invalid_input)

    # Should recover after temporary error
    result = ai.process_with_retry(valid_input)
    assert result.status == "success"
```

### 3. Integration Testing
```python
def test_jexi_marian_integration():
    """Test interaction between Jexi and Marian."""
    # Jexi requests information
    query = jexi.create_catalog_query("test query")

    # Marian processes request
    result = marian.process_catalog_query(query)

    # Jexi handles response
    response = jexi.handle_catalog_response(result)
    assert response.is_valid()
```

## Test Environment Setup

### 1. Dependencies
```ini
[tool.poetry.dependencies]
pytest = "^7.0.0"
pytest-asyncio = "^0.18.0"
pytest-cov = "^3.0.0"
```

### 2. Configuration
```python
# conftest.py
@pytest.fixture
def jexi():
    """Create test instance of Jexi."""
    return Jexi(mode="test")

@pytest.fixture
def marian():
    """Create test instance of Marian."""
    return Marian(mode="test")
```

### 3. Environment Variables
```ini
JEXI_MODE=test
MARIAN_MODE=test
AI_API_KEY=test-key
TEST_DATA_DIR=tests/data
