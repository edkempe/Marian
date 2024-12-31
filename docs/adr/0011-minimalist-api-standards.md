# 11. Minimalist API Standards

Date: 2024-12-31

## Status

Proposed

## Revision History
1.0.0 (2024-12-31) @dev
- Initial version with FastAPI standards
- Added response format
- Added error handling patterns

## Context

As a solo developer working with an AI copilot, we need API standards that are:
1. Easy to maintain
2. Self-documenting
3. Consistent for AI to understand
4. Simple to validate

## Decision

We will use FastAPI with a minimalist approach:

### 1. API Structure
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Jexi API",
    version="1.0.0",
    docs_url="/docs"  # Always enable docs for AI reference
)

class ErrorResponse(BaseModel):
    """Standard error response."""
    message: str
    code: str
```

### 2. Endpoint Design
- Use RESTful patterns for familiarity
- Keep URLs simple and literal
- Favor clarity over brevity

```python
# Good: Clear and literal
@app.get("/users/{user_id}/emails")
async def get_user_emails(user_id: int):
    pass

# Bad: Too clever/abbreviated
@app.get("/u/{uid}/m")
async def get_mails(uid: int):
    pass
```

### 3. Response Format
All responses use Pydantic models for validation and documentation:

```python
class APIResponse(BaseModel):
    """Standard response wrapper."""
    success: bool
    data: dict | None = None
    error: ErrorResponse | None = None
```

### 4. Error Handling
Simple, consistent error pattern:

```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return APIResponse(
        success=False,
        error=ErrorResponse(
            message=str(exc.detail),
            code=f"HTTP_{exc.status_code}"
        )
    )
```

### 5. Documentation
- Let FastAPI handle OpenAPI docs
- Focus on clear docstrings that help AI understand intent
- Document by example in docstrings

```python
async def create_user(user: UserCreate) -> APIResponse:
    """Create a new user.
    
    Example:
        >>> user = UserCreate(name="Alice", email="alice@example.com")
        >>> response = await create_user(user)
        >>> assert response.success
        >>> assert response.data["id"] > 0
    """
    pass
```

## Consequences

### Positive
1. AI can easily understand and generate consistent endpoints
2. Self-documenting via FastAPI's OpenAPI integration
3. Type safety via Pydantic
4. Easy to maintain as a solo developer

### Negative
1. Less flexible than complex REST/GraphQL patterns
2. May need refactoring for team scaling
3. Limited optimization options

### Mitigation
1. Use clear docstrings to explain any deviations
2. Let AI handle boilerplate code generation
3. Focus on maintainability over optimization

## References
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [RESTful API Design](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
