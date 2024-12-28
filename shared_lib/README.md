# Marian Shared Library

**Version:** 1.0.0  
**Status:** Authoritative

> Shared utilities and helpers for the Marian project.

## Utility Hierarchy

Shared utilities support our data flow:

```
External APIs → Models → Database → Application Code
        ↓          ↓         ↓            ↓
    API Utils  Model Utils  DB Utils  General Utils
```

## Utility Categories

### 1. API Utilities
- API response parsing
- Type conversion helpers
- Error handling wrappers
Example: `api_utils.py`

### 2. Model Utilities
- Field validators
- Type converters
- Common mixins
Example: `model_utils.py`

### 3. Database Utilities
- Connection management
- Transaction helpers
- Query builders
Example: `db_utils.py`

### 4. General Utilities
- Date/time handling
- String processing
- Configuration
Example: `config_utils.py`

## Implementation Guidelines

### 1. Type Safety
- Preserve API types
- Use type hints
- Validate conversions
Example:
```python
def parse_gmail_date(date_str: str) -> datetime:
    """Parse Gmail API date format."""
    return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
```

### 2. Error Handling
- Consistent error types
- Clear error messages
- Context preservation
Example:
```python
def safe_api_call(func):
    """Wrapper for API calls with error handling."""
    try:
        return func()
    except ApiError as e:
        raise ApiCallError(f"API call failed: {e}")
```

### 3. Configuration
- Environment-based config
- Secure credentials
- Default values
Example:
```python
def get_api_config():
    """Get API configuration with defaults."""
    return {
        'timeout': int(os.getenv('API_TIMEOUT', '30')),
        'retries': int(os.getenv('API_RETRIES', '3'))
    }
```

## Common Utilities

### API Response Processing
```python
def extract_email_id(response: dict) -> str:
    """Extract email ID from Gmail response."""
    return str(response.get('id', ''))
```

### Date Handling
```python
def to_utc_datetime(dt: datetime) -> datetime:
    """Convert datetime to UTC."""
    return dt.astimezone(timezone.utc)
```

### Configuration
```python
def load_credentials(cred_path: str) -> dict:
    """Load API credentials securely."""
    with open(cred_path) as f:
        return json.load(f)
```

## Version History
- 1.0.0: Initial version with API-aligned utilities
