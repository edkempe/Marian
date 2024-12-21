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
    - `email_triage`: Legacy triage data (deprecated)

## Project Structure
```
marian/
├── app_*.py              # Main application files
├── config/              # Configuration files
│   ├── constants.py    # Central source of truth for constants
│   └── __init__.py
├── database/           # Database related code
│   ├── config.py      # Database configuration
│   └── __init__.py
├── model_*.py          # SQLAlchemy and Pydantic models
├── utils/             # Utility functions
│   ├── logging_config.py  # Logging configuration
│   └── __init__.py
├── tests/             # Test files
├── logs/              # Log files
├── docs/              # Documentation
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Configuration
The project uses a centralized configuration system:

1. **Constants** (`config/constants.py`):
   - Database file names and URLs
   - Table names
   - API configuration
   - Logging settings
   - Email processing parameters

2. **Environment Variables**:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   export EMAIL_DB_URL=sqlite:///db_email_store.db      # Optional
   export ANALYSIS_DB_URL=sqlite:///db_email_analysis.db # Optional
   ```

## Logging
The project uses structured JSON logging with both file and console output:

- Log files are stored in `logs/marian.log`
- Logs rotate at 10MB with 5 backup files
- Each log entry includes:
  - Timestamp
  - Event name
  - Error type and message (if applicable)
  - Additional context

## File Naming Convention
- Processors: `processor_<type>.py` (e.g., processor_email.py)
- Utilities: `util_<purpose>.py` (e.g., util_db.py)
- Models: `model_<type>.py` (e.g., model_email.py)
- Tests: `test_<module>.py` (e.g., test_processor_email.py)

## Prompt Naming Convention
Format: `<domain>.<task>.<subtask>.v<version>`
Example: `email.analysis.triage.v1.0.0`

## Prerequisites
1. Python 3.13 or higher
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
   ```
6. Place your Gmail API `credentials.json` in the project root

## Pre-Run Checklist
1. Verify virtual environment is activated
2. Check core files exist and are up to date:
   - `app_get_mail.py`: Email fetching script
   - `app_email_analyzer.py`: Email analysis script
   - `lib_gmail.py`: Gmail API authentication
   - `model_email.py`: Email database model
   - `model_email_analysis.py`: Analysis database model
   - `model_base.py`: SQLAlchemy base model
3. Verify database files:
   - `db_email_store.db`: Main database for emails and analysis
4. Confirm environment variables are set:
   - `ANTHROPIC_API_KEY`
5. Ensure `credentials.json` and `token.pickle` exist for Gmail API

## Database Architecture
The project uses SQLite for data storage. See [Database Schema](docs/database_schema.md) for detailed information about tables and fields.

## Usage
1. Fetch emails:
   ```bash
   python app_get_mail.py [--newer] [--older] [--clear] [--label] [--list-labels]
   ```
2. Analyze emails:
   ```bash
   python app_email_analyzer.py
   ```

## Common Issues and Solutions

### 1. Database Schema Mismatches
If you encounter database errors like "no such column" or "datatype mismatch":

a) **Schema vs Model Mismatch**:
   - Check that your SQLAlchemy models match the database schema
   - Use `sqlite3 db_email_store.db ".schema"` to view current schema
   - Compare with models in `model_*.py` files

b) **JSON Field Issues**:
   - SQLite requires JSON fields to be stored as TEXT/STRING
   - Always use `json.dumps()` before storing lists/dicts
   - Use `json.loads()` when retrieving

c) **Migration Required**:
   - If schema changes are needed, either:
     1. Delete the database and let it recreate (development only)
     2. Create a proper migration script (production)

### 2. API Response Parsing
When dealing with Claude API responses:

a) **Incomplete JSON**:
   - Increase `max_tokens` if responses are getting truncated
   - Validate JSON structure before parsing
   - Use error handling around `json.loads()`

b) **Missing Fields**:
   - Ensure all required fields are in the prompt
   - Add default values for optional fields
   - Validate response against Pydantic models

### 3. File Naming Conflicts
To avoid confusion:

a) **Database Files**:
   - Email database: `db_email_store.db`
   - Analysis database: `db_email_analysis.db`
   - Never use generic names like `emails.db`

b) **Log Files**:
   - Main log: `logs/marian.log`
   - Rotated logs: `marian.log.1`, `marian.log.2`, etc.

## Best Practices

1. **Constants**:
   - Always use constants from `config/constants.py`
   - Never hardcode values in application code
   - Update constants file when adding new configuration

2. **Logging**:
   - Use structured logging with event names
   - Include relevant context in log entries
   - Use appropriate log levels (INFO, ERROR, etc.)

3. **Error Handling**:
   - Always catch and log specific exceptions
   - Include context in error logs
   - Use transaction rollback when appropriate

4. **Database Operations**:
   - Use session context managers
   - Implement proper error handling
   - Validate data before insertion
