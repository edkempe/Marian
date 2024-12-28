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

4. **HTML Reports**
   - All test suites generate HTML reports in `reports/testing/`
   - Reports use consistent styling and formatting
   - Issues are reported as warnings to avoid blocking tests
   - Common report types:
     ```python
     def generate_html_report(data, title):
         """Generate HTML report with standard template."""
         template = jinja2.Template(HTML_TEMPLATE)
         return template.render(
             title=title,
             content=markdown.markdown(data)
         )
     ```
   - Reports include:
     - Documentation quality and versioning
     - Import analysis and style
     - Code duplication detection
     - Test coverage metrics

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

### Report Generation
```python
def test_with_report():
    """Test that generates an HTML report."""
    # Run analysis
    results = analyze_code()
    
    # Generate report
    report = generate_html_report(
        data=format_results(results),
        title="Code Analysis Report"
    )
    
    # Save report
    save_report("code_analysis.html", report)
    
    # Report issues as warnings
    for issue in results.issues:
        pytest.warns(UserWarning, match=str(issue))
```

## Running Tests

1. **Basic Test Run**
   ```bash
   python -m pytest
   ```

2. **Generate Reports**
   ```bash
   # Generate all reports
   python -m pytest tests/
   
   # Generate specific report
   python -m pytest tests/test_imports.py
   ```

3. **View Reports**
   - Reports are generated in `reports/testing/`
   - Open HTML reports in a browser for best viewing
   - Reports are self-contained with embedded styles
   - Each test run updates existing reports

4. **Report Types**
   - Documentation: `doc_versioning.html`
   - Imports: `import_analysis.html`
   - Duplicates: `file_duplicates.html`
   - Coverage: `coverage.html`

## Version History
- 1.0.0: Initial version with API-first testing hierarchy
