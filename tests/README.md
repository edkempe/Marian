# Marian Tests

**Version:** 1.0.0  
**Status:** Authoritative

> Test suite for the Marian project.

## Testing Hierarchy

Our tests follow the data flow hierarchy:

```
External APIs → Models → Database → Application Code
           ↓         ↓         ↓            ↓
     API Tests   Model Tests  Schema Tests  Integration Tests
```

## Test Categories

### 1. API Tests
- Verify API response handling
- Check type conversions
- Test error conditions
Example: `test_gmail_api.py`

### 2. Model Tests
- Validate field types match APIs
- Check constraints
- Test relationships
Example: `test_email_fields.py`

### 3. Schema Tests
- Verify model-database alignment
- Check migrations
- Test constraints
Example: `test_schema.py`

### 4. Integration Tests
- End-to-end workflows
- Real API interactions
- Data consistency
Example: `test_email_processing.py`

## Testing Guidelines

1. **API Integration**
   - Use real APIs (no mocks)
   - Test with actual responses
   - Verify type handling
   ```python
   def test_gmail_message():
       msg = gmail.get_message("msg123")
       assert isinstance(msg.id, str)  # Match API type
   ```

2. **Data Validation**
   - Test against API schemas
   - Verify type conversions
   - Check constraints
   ```python
   def test_email_fields():
       email = Email(id="msg123")  # String ID from Gmail
       assert email.id.isalnum()
   ```

3. **Schema Alignment**
   - Test model-database match
   - Verify migrations
   - Check constraints
   ```python
   def test_schema_alignment():
       assert_schema_equal(migration_schema, model_schema)
   ```

## Common Test Patterns

### API Response Testing
```python
def test_process_message():
    response = get_gmail_message()
    email = Email.from_api_response(response)
    assert email.id == response['id']
```

### Model Validation
```python
def test_email_validation():
    email = Email(id="msg123")
    assert validate_email(email)
```

### Schema Testing
```python
def test_email_schema():
    assert Email.__table__.c.id.type.python_type == str
```

## Version History
- 1.0.0: Initial version with API-first testing hierarchy
