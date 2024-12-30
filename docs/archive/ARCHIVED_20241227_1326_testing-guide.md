# Testing Guide and Strategy

> **Documentation Role**: This guide is a supporting document for both Development AI and Runtime AI testing. See `ai-architecture.md` for the complete documentation hierarchy.

This document outlines the testing strategy and guidelines for the Marian project, explaining our approach to different types of tests and why we made these choices.

## Core Testing Principles

### 1. Test What Matters
- Focus on critical user paths
- Test complex business logic
- Cover edge cases and error handling
- Validate data integrity

### 2. Test Close to Production
- Minimize mocking where possible
- Use realistic test data
- Match production configurations
- Test actual integrations

### 3. Test for Maintainability
- Keep tests simple and focused
- Document test rationale
- Make test failures clear
- Update tests with code changes

### 4. Test for Reliability
- Avoid flaky tests
- Handle async operations properly
- Clean up test data
- Isolate test environments

## Testing Philosophy
Our testing approach prioritizes reliability and maintainability over theoretical purity. While unit tests with mocks are valuable in some contexts, they can be problematic when testing complex API integrations.

### Key Decisions

1. **Minimal Mocking**
   - Mock only what's necessary (external APIs, time)
   - Use real database connections where possible
   - Test actual integrations when feasible

2. **Data Model First**
   - The data model is the single source of truth
   - Test structure follows data model hierarchy:
     1. Schema validation
     2. Data integrity
     3. Business logic
     4. Integration

3. **Clear Test Organization**
   - Group tests by functionality
   - Use descriptive test names
   - Document test purpose
   - Include example data

4. **Comprehensive Coverage**
   - Test happy paths thoroughly
   - Include error cases
   - Validate edge conditions
   - Check performance impacts

## Test Categories

### 1. Development AI Testing
> These sections support the Development AI (Windsurf.ai) workflow

#### Test Development Practices
- Use test-driven development (TDD) where appropriate
- Write clear test descriptions
- Follow consistent naming patterns
- Document test rationale

#### Test Organization
- Group tests by functionality
- Maintain clear test hierarchy
- Use descriptive test names
- Follow `test_category_action_result` pattern

### 2. Runtime AI Testing
> These sections support the Runtime AI (Anthropic) implementation

#### Data Model Tests
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

### 3. API Integration Tests
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

### 4. Catalog Tests
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

### 5. Database Tests
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
- Update tests with code
- Remove obsolete tests
- Keep tests focused
- Document changes

### 4. Test Performance
- Fast test execution
- Minimal dependencies
- Efficient setup/teardown
- Parallel test support

## Common Patterns

### 1. Setup/Teardown
```python
@pytest.fixture
def test_catalog():
    """Create test catalog with sample data."""
    catalog = Catalog()
    # Add test data
    yield catalog
    # Cleanup
    catalog.clear()
```

### 2. Test Categories
```python
class TestCatalogOperations:
    """Test catalog CRUD operations."""

    def test_create_entry(self, test_catalog):
        """Test creating new catalog entry."""
        entry = test_catalog.create_entry(...)
        assert entry.id is not None

    def test_update_entry(self, test_catalog):
        """Test updating existing entry."""
        entry = test_catalog.update_entry(...)
        assert entry.modified > entry.created
```

### 3. Error Handling
```python
def test_invalid_entry():
    """Test handling of invalid entry data."""
    with pytest.raises(ValidationError):
        catalog.create_entry(invalid_data)
```

## Test Environment

### 1. Dependencies
- pytest
- pytest-cov
- pytest-asyncio
- pytest-mock

### 2. Configuration
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### 3. Coverage
```ini
[coverage:run]
source = src
omit = tests/*
```
