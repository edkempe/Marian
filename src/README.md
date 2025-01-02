# Jexi Source Code

**Version:** 1.0.0
**Status:** Authoritative

> Source code for the Jexi email processing system and Marian catalog management.

## Revision History
1.0.0 (2024-12-31) @dev
- Initial source code structure
- Added module organization
- Added coding standards

## Directory Structure

1. **Jexi Core Components**
   - `app_email_analyzer.py`: Email analysis engine
   - `app_email_self_log.py`: Email monitoring system
   - `app_get_mail.py`: Gmail integration
   - `app_email_reports.py`: Email reporting

2. **Marian Components** 
   - `app_catalog.py`: Catalog management system
   - `app_catalog_interactive.py`: Catalog interface
   
3. **Support Modules**
   - `proto_*.py`: Prototype implementations
   - `utils/`: Utility functions and helpers

## Data Flow Hierarchy

This package implements application logic following our data flow hierarchy:

```
External APIs → Models → Database → Application Code
```

Application code is the final consumer in our data flow, meaning it should:
1. Use types defined by models
2. Respect API constraints
3. Follow database schema
4. Handle API responses correctly

## Code Organization

```
src/
├── api/              # API client implementations
│   ├── gmail.py      # Gmail API client
│   └── claude.py     # Claude API client
├── services/         # Business logic services
│   ├── email.py      # Email processing
│   └── analysis.py   # Email analysis
└── utils/           # Shared utilities
    ├── parsing.py    # Data parsing
    └── validation.py # Input validation
```

## API Integration Guidelines

1. **Type Consistency**
   - Use types from models package
   - Don't create parallel type definitions
   - Handle API responses consistently
   Example:
   ```python
   from models import Email

   def process_message(msg_data: dict) -> Email:
       return Email(
           id=msg_data['id'],  # String ID from Gmail
           thread_id=msg_data['threadId']
       )
   ```

2. **Data Validation**
   - Validate against model constraints
   - Check API response structure
   - Handle missing fields gracefully
   Example:
   ```python
   def validate_email(email: Email) -> bool:
       if not email.id or not email.thread_id:
           raise ValueError("Email missing required fields")
       return True
   ```

3. **Error Handling**
   - Use API-specific error types
   - Map API errors to domain errors
   - Preserve error context
   Example:
   ```python
   from googleapiclient.errors import HttpError

   try:
       response = gmail.users().messages().get(...).execute()
   except HttpError as e:
       raise EmailError(f"Failed to fetch email: {e}")
   ```

4. **Response Processing**
   - Follow API response structure
   - Map to model fields correctly
   - Preserve API data types
   Example:
   ```python
   def process_labels(labels_data: dict) -> str:
       # Preserve Gmail's label format
       return ','.join(labels_data.get('labelIds', []))
   ```

## Testing Guidelines

1. **Integration Tests**
   - Test with real APIs
   - Verify type handling
   - Check error cases
   Example: `tests/test_gmail_integration.py`

2. **Response Validation**
   - Verify API response parsing
   - Check field mapping
   - Test error handling
   Example: `tests/test_email_processing.py`

## Common Tasks

### Fetching Emails
```python
from src.api.gmail import GmailClient
from models import Email

client = GmailClient()
messages = client.fetch_messages()
emails = [Email.from_api_response(msg) for msg in messages]
```

### Processing Analysis
```python
from src.services.analysis import AnalysisService
from models import EmailAnalysis

service = AnalysisService()
analysis = service.analyze_email(email)
analysis.save()
```

## Error Handling

1. **API Errors**
   - `GmailApiError`: Gmail API issues
   - `ClaudeApiError`: Claude API issues
   - `NetworkError`: Connection problems

2. **Processing Errors**
   - `EmailProcessingError`: Email handling
   - `AnalysisError`: Analysis failures
   - `ValidationError`: Data validation

## Version History
- 1.0.0: Initial version with API-first hierarchy
