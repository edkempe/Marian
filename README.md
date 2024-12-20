# Marian Project

## Overview
An AI-powered email analysis and management system that uses advanced language models to process, categorize, and extract insights from emails.

## Key Components
- **Email Fetcher** (`app_get_mail.py`): Fetches emails from Gmail and stores them in SQLite
- **Email Analyzer** (`app_email_analyzer.py`): Analyzes emails using Claude-3-Haiku and stores insights
- **Database**:
  - `db_email_store.db`: Main database for email storage and analysis
    - `emails`: Raw email data
    - `email_analysis`: AI analysis results

## Prerequisites
1. Python 3.12.8 or higher
2. Gmail API credentials (`credentials.json`) from Google Cloud Console
3. Anthropic API key for Claude-3-Haiku

## Setup Instructions
1. Clone the repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   export EMAIL_DB_URL=sqlite:///db_email_store.db      # Optional
   export ANALYSIS_DB_URL=sqlite:///db_email_analysis.db # Optional
   ```
6. Place your Gmail API `credentials.json` in the project root

## Usage
1. Fetch emails:
   ```bash
   python app_get_mail.py [--newer] [--older] [--clear] [--label] [--list-labels]
   ```
2. Analyze emails:
   ```bash
   python app_email_analyzer.py
   ```

## Troubleshooting
If you encounter any issues while running the application, please refer to our comprehensive [Troubleshooting Guide](docs/troubleshooting.md). The guide covers:
- Database initialization issues
- Data model validation errors
- Port management
- Common error messages and their solutions
- Best practices for development

## Project Structure
marian/
├── app_*.py           # Main application files
├── util_*.py         # Utility scripts
│   └── util_email_analysis_db.py  # Email analysis database verification tool
├── config/           # Configuration files
├── database/         # Database related code
├── models/          # SQLAlchemy models
├── utils/           # Utility functions
├── docs/            # Documentation
│   └── troubleshooting.md  # Troubleshooting guide
├── tests/           # Test files
└── README.md        # This file

## Security and Compliance
1. **Data Security**
   - Store API keys in environment variables
   - Use secure database connections
   - Encrypt sensitive data
   - Follow GDPR/privacy guidelines
   - Implement data retention policies

2. **Access Control**
   - Implement proper authentication
   - Regular security audits
   - Monitor for suspicious activity

## Monitoring and Maintenance
1. **Logging**
   - Use structured JSON logging
   - Log files stored in `logs/marian.log`
   - Logs rotate at 10MB with 5 backup files
   - Each log includes:
     * Timestamp
     * Event name
     * Error details
     * Context

2. **Performance**
   - Monitor API rate limits
   - Track database performance
   - Implement proper caching
   - Use connection pooling

## File Naming Conventions
1. **Application Files**
   - Main apps: `app_*.py` (e.g., `app_email_analyzer.py`)
   - Models: `model_*.py` (e.g., `model_email.py`)
   - Tests: `test_*.py` (e.g., `test_email_analyzer.py`)

2. **Database Files**
   - Main database: `db_email_store.db`
   - Never use generic names like `emails.db`

## Schema Management
1. **Verification Process**
   ```python
   # Example schema verification
   from sqlalchemy import inspect
   
   def verify_schema(engine, model_class):
       inspector = inspect(engine)
       table_name = model_class.__tablename__
       columns = {col.name: col for col in model_class.__table__.columns}
       db_columns = {col['name']: col for col in inspector.get_columns(table_name)}
       
       # Verify columns match
       missing_in_db = set(columns.keys()) - set(db_columns.keys())
       if missing_in_db:
           raise ValueError(f"Columns missing in database: {missing_in_db}")
   ```

2. **Migration Management**
   - Track schema changes in migrations
   - Test migrations in development
   - Document migration dependencies

## Data Models as Source of Truth

The SQLAlchemy models in `models/` are the SINGLE SOURCE OF TRUTH for data structures in this project.

1. **Model Definition**
   ```python
   # models/email.py - Source of truth for email structure
   class Email(Base):
       __tablename__ = 'emails'
       
       id = Column(Integer, primary_key=True)
       subject = Column(String, nullable=False)
       body = Column(Text, nullable=False)
       sender = Column(String, nullable=False)
       date = Column(DateTime, nullable=False)
       labels = Column(String)
       analyzed = Column(Boolean, default=False)
   ```

2. **Schema Alignment**
   - Database schemas MUST match model definitions
   - Code accessing data MUST use model field names
   - API responses MUST be validated against models
   - Never create parallel definitions of data structures

3. **Making Changes**
   - Always update the model first
   - Create database migrations based on model changes
   - Update dependent code to match model changes
   - Never modify database schema directly

4. **Verification**
   - Run schema verification on startup
   - Use Alembic for migration management
   - Write tests that verify data consistency
   - Log any schema mismatches as critical errors

Example of enforcing model as source of truth:
```python
# Right way: Use model fields directly
email = Email(
    subject=data['subject'],
    body=data['body'],
    sender=data['sender'],
    date=datetime.now()
)

# Wrong way: Define fields separately from model
email_fields = {  # DON'T DO THIS
    'subject': 'text',
    'body': 'text',
    'sender': 'text',
    'date': 'datetime'
}
```

## Known Issues and Solutions

### Anthropic Client Initialization Error
If you encounter an error like `__init__() got an unexpected keyword argument 'proxies'` when running the email analyzer, this is due to a compatibility issue between newer versions of `httpx` and the Anthropic client library. The error occurs because newer versions of httpx (0.28.0+) have removed the deprecated 'proxies' argument.

**Solution**: We've pinned `httpx==0.27.2` in requirements.txt to resolve this issue. If you still encounter this error:

1. Manually install the correct version:
   ```bash
   pip install httpx==0.27.2
   ```

2. Verify your Anthropic client version is correct:
   ```bash
   pip install anthropic==0.18.1
   ```

## Common Issues and Solutions

### 1. API Response Handling
- **Issue**: Claude API may return responses with extra text around JSON
- **Solution**: 
  - Use robust JSON extraction
  - Validate response structure
  - Handle missing fields gracefully
  ```python
  # Example of handling API response
  try:
      json_str = extract_json(response)  # Remove extra text
      data = json.loads(json_str)       # Parse JSON
      validate_response(data)           # Validate structure
  except json.JSONDecodeError:
      handle_invalid_json()
  ```

### 2. Data Validation
- **Issue**: Schema constraints may fail with unexpected data
- **Solution**:
  - Use Pydantic models for validation
  - Add database constraints
  - Test with edge cases
  ```python
  # Example of data validation
  class EmailAnalysis(BaseModel):
      summary: str
      sentiment: Literal["positive", "negative", "neutral"]
      priority: int = Field(ge=1, le=5)
  ```

### 3. URL Handling
- **Issue**: Long URLs can break JSON parsing
- **Solution**:
  - Store full URLs separately from display URLs
  - Truncate display URLs to 100 characters
  - Use TEXT type for URL storage

### 4. Database Operations
- **Issue**: Connection management and transaction handling
- **Solution**:
  - Use SQLAlchemy session management
  - Implement proper error handling
  - Use transactions appropriately
  ```python
  # Example of proper database handling
  with Session() as session:
      try:
          session.add(email)
          session.commit()
      except SQLAlchemyError:
          session.rollback()
          raise
  ```

## Best Practices

1. **API Usage**
   - Set appropriate token limits
   - Use temperature=0 for consistent results
   - Handle rate limits properly
   - Log API errors with context

2. **Error Handling**
   - Catch specific exceptions
   - Log errors with context
   - Use proper error types
   - Implement graceful fallbacks

3. **Data Management**
   - Validate data before storage
   - Use appropriate data types
   - Implement proper constraints
   - Handle duplicates appropriately

4. **Testing**
   - Write unit tests for core functionality
   - Test edge cases
   - Mock external APIs
   - Use consistent test data
