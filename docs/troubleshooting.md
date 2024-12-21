# Troubleshooting Guide

## Common Issues and Solutions

### Database Initialization
- **Issue**: "no such table: email_analysis" error when running the analyzer
- **Solution**: Initialize the database tables first by running:
  ```python
  from database.config import init_db
  init_db()
  ```
- **Note**: This needs to be done once before first running the analyzer or after any schema changes

### Data Model Validation
- **Issue**: Pydantic validation errors with `null` values from API
- **Solution**: The analyzer now preprocesses API responses to convert `null` values to empty strings for required string fields
- **Example Fields**: `project`, `topic`
- **Location**: See `_parse_api_response` method in `app_email_analyzer.py`

### Port Management
- **Issue**: "Address already in use" error on port 8000 (metrics server)
- **Solution**: Kill existing Python processes using port 8000:
  ```bash
  lsof -i :8000  # Find process ID
  kill -9 <PID>  # Kill the process
  ```
- **Prevention**: Future enhancement could include automatic port cleanup or configurable ports

### Best Practices
1. **Database Operations**:
   - Use SQLAlchemy ORM instead of raw SQL queries
   - Always handle database connections in a context manager
   - Properly commit or rollback transactions

2. **Data Validation**:
   - Use Pydantic models for API response validation
   - Add preprocessing for fields that might be null
   - Document expected data types and formats

3. **Error Handling**:
   - Log errors with sufficient context
   - Include error type and original response in logs
   - Handle database errors gracefully

## Monitoring and Debugging
- Use the `util_email_analysis_db.py` script to verify database contents:
  ```bash
  python util_email_analysis_db.py
  ```
- Monitor the metrics server output for real-time processing information
- Check logs for any API or database errors

## Future Improvements
1. Implement automatic port management for metrics server
2. Add database migration support for schema changes
3. Enhance error reporting and recovery mechanisms
4. Add automated tests for edge cases discovered during troubleshooting
