# 15. Minimalist Error Handling Strategy

Date: 2024-12-31

## Status

Proposed

## Revision History
1.0.0 (2024-12-31) @dev
- Initial version with basic error hierarchy
- Added FastAPI error handlers
- Added structured logging

## Context

As a solo developer with AI assistance, we need error handling that:
1. Is consistent and predictable
2. Helps with debugging
3. Provides clear user feedback
4. Works well with AI analysis

## Decision

We will implement a simple but comprehensive error handling strategy:

### 1. Error Hierarchy
Basic error classes that map to HTTP status codes:

```python
# errors.py
from typing import Any, Dict, Optional

class AppError(Exception):
    """Base error class."""
    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class NotFoundError(AppError):
    """Resource not found."""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} not found: {resource_id}",
            code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "id": resource_id}
        )

class ValidationError(AppError):
    """Invalid input data."""
    def __init__(self, message: str, fields: Dict[str, str]):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details={"fields": fields}
        )

class AuthError(AppError):
    """Authentication/authorization error."""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="AUTH_ERROR",
            status_code=401
        )
```

### 2. Error Handling
Consistent error handling in FastAPI:

```python
# error_handlers.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(AppError)
async def app_error_handler(
    request: Request,
    error: AppError
) -> JSONResponse:
    """Handle application errors."""
    return JSONResponse(
        status_code=error.status_code,
        content={
            "success": False,
            "error": {
                "message": error.message,
                "code": error.code,
                "details": error.details
            }
        }
    )

# Usage
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await find_user(user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return {"success": True, "data": user}
```

### 3. Error Logging
Structured error logging for AI analysis:

```python
# error_logging.py
import logging
import traceback
from typing import Type

def log_error(
    error: Exception,
    context: dict = None
) -> None:
    """Log error with context for AI analysis."""
    error_data = {
        "error_type": error.__class__.__name__,
        "message": str(error),
        "traceback": traceback.format_exc(),
        "context": context or {}
    }
    
    if isinstance(error, AppError):
        error_data.update({
            "code": error.code,
            "status_code": error.status_code,
            "details": error.details
        })
    
    logging.error(
        f"Error: {error}",
        extra={"error_data": error_data}
    )

# Usage
try:
    process_data()
except Exception as e:
    log_error(e, context={"process": "data_processing"})
```

### 4. Error Recovery
Simple retry mechanism:

```python
# retry.py
import time
from functools import wraps
from typing import Type, Tuple

def retry(
    retries: int = 3,
    delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < retries - 1:
                        wait = delay * (2 ** attempt)
                        logging.warning(
                            f"Retry {attempt + 1}/{retries} "
                            f"after {wait}s due to {e}"
                        )
                        time.sleep(wait)
            raise last_error
        return wrapper
    return decorator

# Usage
@retry(retries=3, exceptions=(ConnectionError,))
async def fetch_data():
    pass
```

## Consequences

### Positive
1. Consistent error handling
2. Clear error hierarchy
3. Structured logging for AI
4. Simple recovery mechanisms

### Negative
1. Limited error categorization
2. Basic retry mechanism
3. No distributed error tracking

### Mitigation
1. Use AI to analyze error patterns
2. Add categories as needed
3. Implement better recovery as required

## References
- [Python Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
