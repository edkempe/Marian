# Marian Services

**Version:** 1.0.0  
**Status:** Authoritative

> Business logic services for the Marian project.

## Service Layer Hierarchy

Services implement business logic following our data flow:

```
External APIs → Models → Database → Services
```

Services are responsible for:
1. Processing API responses
2. Applying business rules
3. Managing persistence
4. Coordinating workflows

## Service Guidelines

### 1. API Integration
- Use API client abstractions
- Handle API responses consistently
- Map to model types correctly
Example:
```python
def process_message(msg_data: dict) -> Email:
    """Process Gmail message data into Email model."""
    return Email(
        id=msg_data['id'],
        thread_id=msg_data['threadId']
    )
```

### 2. Data Processing
- Follow API data structures
- Apply business rules
- Validate inputs/outputs
Example:
```python
def analyze_email(email: Email) -> EmailAnalysis:
    """Generate analysis from email content."""
    analysis = claude.analyze(email.body)
    return EmailAnalysis(
        email_id=email.id,
        summary=analysis['summary']
    )
```

### 3. Error Handling
- Handle API errors gracefully
- Provide clear error context
- Maintain consistency
Example:
```python
try:
    response = gmail.get_message(msg_id)
except GmailError as e:
    raise EmailError(f"Failed to fetch: {e}")
```

## Core Services

### Email Service
- Fetches emails from Gmail
- Processes messages
- Manages email lifecycle
Example: `services/email.py`

### Analysis Service
- Analyzes email content
- Generates insights
- Stores results
Example: `services/analysis.py`

## Common Patterns

### API Processing
```python
def process_emails(messages: List[dict]) -> List[Email]:
    """Process Gmail messages into Email models."""
    return [Email.from_api_response(msg) for msg in messages]
```

### Business Logic
```python
def categorize_email(email: Email) -> str:
    """Apply business rules for categorization."""
    if 'IMPORTANT' in email.labels:
        return 'high_priority'
    return 'normal'
```

### Persistence
```python
def save_analysis(email: Email, analysis: dict):
    """Save email analysis results."""
    email_analysis = EmailAnalysis(
        email_id=email.id,
        **analysis
    )
    db.session.add(email_analysis)
```

## Version History
- 1.0.0: Initial version with API-first service patterns
