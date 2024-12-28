# Marian Project

**Version:** 1.0.0  
**Status:** Authoritative

## Document Version Guidelines
All project documentation follows this version notation:
- Format: `[Major].[Minor].[Patch]`
- Example: `1.2.3`

Version components:
- Major: Breaking changes
- Minor: New features, backward compatible
- Patch: Bug fixes, clarifications

Status levels:
- Draft: Initial creation, not reviewed
- Review: Under review/testing
- Authoritative: Current source of truth
- Deprecated: Superseded but preserved

## Version History
- 1.0.0: Initial project setup and core documentation

## Important Process Documents
**REQUIRED**: Follow the authoritative [Development Session Checklist](docs/dev-checklist.md) for all development sessions.

**Core Documentation**:
- [Development Session Logs](docs/session_logs/) - Daily development tracking (REQUIRED)
- [Session Logs Guide](docs/session_logs/README.md) - Session logging standards
- [Session Workflow Guide](docs/session-workflow.md) - Development workflow
- [Project Guidelines](docs/contributing.md) - Contribution standards
- [Setup Guide](docs/setup.md) - Environment setup
- [Project Design Decisions](docs/design-decisions.md) - Architecture choices

The checklist and session logs must be maintained for every development session, with the supporting documents providing additional context and details as needed.

## Critical Development Guidelines

1. **Code Preservation Policy**
   - **NEVER** remove functionality or information/documentation without explicit permission
   - This includes:
     - Test cases and functionality
     - Documentation and comments
     - Helper functions and utilities
     - Logging and debugging code
     - Error handling
   - Duplicate important information rather than removing it
   - Always get explicit approval before removing any code
   - This guideline is critical and applies to all aspects of the project

2. **Code Addition Policy**
   - **NEVER** add new functionality without explicit approval
   - This includes:
     - New files or modules
     - External libraries and dependencies
     - New features or functionality
     - Code reformatting or restructuring
     - Changes to build or deployment processes
   - Always propose and get approval before adding:
     - New dependencies
     - New files
     - Code reformatting
     - New features
     - Project structure changes
   - Document the reason and impact of proposed additions
   - This guideline is critical and applies to all aspects of the project

3. **Testing Policy**
   - **NO MOCK TESTING** - All tests must use real integrations
   - Tests interact with actual APIs, databases, and services
   - Any changes to use mocks require explicit permission
   - Test data volumes are limited to prevent timeouts
   - Tests must be reliable and not dependent on mock behavior
   - This policy ensures tests validate real-world behavior

4. **Change Management Policy**
   - Keep detailed session logs of all development work in `docs/session_logs/`
   - Follow the [Session Logs Guide](docs/session_logs/README.md) for format and naming
   - Make changes small and incremental
   - Ensure diffs are readable for review and approval
   - Document reasoning behind each change
   - Break large changes into smaller, reviewable chunks
   - This policy ensures changes can be properly reviewed and tracked

## Test Setup Requirements

Before running tests:

1. **Gmail API Authentication**
   - Valid Gmail credentials required in `config/credentials.json`
   - Valid token required in `config/token.pickle`
   - Run `python app_get_mail.py` first to authenticate
   - Token must be refreshed when expired
   - Tests will stall if authentication is needed

2. **Database Setup**
   - Email database must be initialized
   - Label database must be synced
   - Run `python app_get_mail.py --sync-labels` to initialize

3. **Test Data Requirements**
   - Gmail account must have some emails
   - Tests use real emails from the last 7 days
   - Limited to small batches to prevent timeouts

4. **Test Reports**
   - HTML test reports are generated in `reports/testing/`
   - Reports include:
     - Documentation quality and versioning
     - Import analysis (unused imports, style issues)
     - File duplicates and similarities
     - Test coverage
   - View reports in browser for best experience
   - Reports are generated automatically during test runs
   - Issues are reported as warnings to avoid blocking tests

## Project Overview

Marian is an AI-powered email analysis and cataloging system that helps organize and understand email content at scale.

### Key Features
- Automated email analysis and categorization
- Smart priority scoring
- Catalog generation and management
- Integration with Gmail API
- Extensible analysis framework

### Quick Links
- [Project Plan](PROJECT_PLAN.md) - Detailed development roadmap and project structure
- [Documentation](docs/) - Guides and technical documentation
  - [Development Session Logs](docs/session_logs/) - Required daily development tracking
  - [Session Logs Guide](docs/session_logs/README.md) - Session logging standards
  - [Project Guidelines](docs/contributing.md) - Code standards and contribution guidelines
  - [Design Decisions](docs/design-decisions.md) - Architecture and technical decisions
- [Infrastructure](infrastructure/) - AWS deployment templates

### Getting Started
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables (see [Setup Guide](docs/setup.md))
4. Run tests: `python -m pytest tests/`

For detailed setup instructions and development guidelines, see the [Setup Guide](docs/setup.md).

## Key Components
- **Email Fetcher** (`app_get_mail.py`): Fetches emails from Gmail and stores them in SQLite
- **Email Analyzer** (`app_email_analyzer.py`): Analyzes emails using Claude-3 and stores insights
- **Data Models** (`models/`): SQLAlchemy models serving as source of truth for:
  - Email and thread schema (`email.py`)
  - Catalog item schema (`catalog.py`)
  - Analysis schema (`email_analysis.py`)
- **Configuration**:
  - `constants.py`: Email processing configuration
  - `catalog_constants.py`: Catalog system configuration
  - `librarian_constants.py`: Librarian-specific settings
- **Database**:
  - `db_email_store.db`: Main database for email storage and analysis
  - Schema defined by SQLAlchemy models in `models/`

## Prerequisites
1. Python 3.12.8 or higher
2. Gmail API credentials (`credentials.json`) from Google Cloud Console
3. Anthropic API key for Claude-3

## Setup Instructions
1. Clone the repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install project in development mode:
   ```bash
   # This installs the project as an editable package,
   # making it available in your Python path
   python3 -m pip install -e .
   ```
5. Install dependencies: `pip install -r requirements.txt`
6. Set up environment variables:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```
7. Place your Gmail API `credentials.json` in the project root

## Development Setup
The project uses setuptools for package management. The `setup.py` file defines:
- Project metadata
- Dependencies
- Package structure

This setup ensures that:
- All project modules are importable
- Dependencies are properly tracked
- Database migrations can find model definitions
- Tests can import project modules

To make changes to the project structure or dependencies:
1. Update `setup.py` with new requirements or packages
2. Reinstall in development mode: `python3 -m pip install -e .`

## Configuration
The project uses a modular configuration system with separate constants files for each major component:

- `constants.py`: Email processing configuration
  - API settings for email analysis
  - Email database configuration
  - Email processing parameters
  - Logging and metrics settings

- `catalog_constants.py`: Catalog system configuration
  - Database settings for catalog
  - Semantic analysis parameters
  - API settings for semantic matching
  - Error message templates

- `librarian_constants.py`: Librarian-specific settings

Each component's constants are isolated to prevent confusion and maintain clear boundaries between different parts of the system. To modify settings:

1. Identify the relevant constants file for your component
2. Update the appropriate configuration section
3. Changes will be automatically reflected in that component

See the individual constants files for detailed configuration references.

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

### Core Components
- `/models` - SQLAlchemy models and database schemas
- `/utils` - Shared utility functions and helpers
- `/tests` - Test suite and test data
- `/docs` - Project documentation and guides
- `/scripts` - Shell scripts for deployment, testing, and maintenance
- `/infrastructure` - Infrastructure as code (CloudFormation)
- `/shared_lib/`: Shared libraries used across the codebase
  - Must be referenced by multiple application files
  - Contains utilities, constants, and helpers
  - Not for standalone scripts or development tools
  - Example: database_session_util.py used by apps and services

### Active Content
- `/docs` - Current documentation only
  - Design decisions
  - Guides and standards
  - Living documentation

### Historical Reference
- `/archive` - Historical content (see [Archiving Guide](docs/archiving.md))
  - Past versions
  - Superseded content
  - Clear naming convention
  - Single location for all archives

### Data Protection
- `/backup` - Disaster recovery only (see [Backup Guide](docs/backup.md))
  - Follows 3-2-1 backup strategy
  - Copies of active files
  - Not for archival purposes

## Data Flow Architecture

Our project follows a strict data flow hierarchy to ensure consistency across all layers:

1. **External APIs as Source of Truth**
   - External APIs (e.g., Gmail API) define the canonical data formats
   - API documentation is referenced in model docstrings
   - API field types and constraints are preserved

2. **SQLAlchemy Models Mirror APIs**
   - Models strictly match API data types (e.g., string IDs from Gmail)
   - Additional fields follow API patterns
   - Models document their API alignment
   - See `models/email.py` for an example

3. **Database Schema Aligns to Models**
   - Migrations ensure database matches model definitions
   - Schema tests (`tests/test_schema.py`) verify alignment
   - Type mismatches are fixed via migrations
   - No direct database manipulation

4. **Application Code Follows Schema**
   - Code expects types defined in schema
   - Type hints reflect database types
   - Tests validate type consistency
   - Schema changes require code updates

This hierarchy ensures data consistency:
```
External APIs (source of truth) 
  → SQLAlchemy Models 
    → Database Migrations 
      → Application Code
```

Each layer is validated:
- Schema tests check model-database alignment
- Model tests verify field types
- Integration tests confirm API compatibility

## Documentation
- [Database Design](docs/database-design.md): Complete database documentation
- [API Usage](docs/api-usage.md): Guidelines for using external APIs
- [Development Guide](docs/development.md): Setup and development practices

## Development Standards

- Follow the code standards in `docs/code-standards.md`
- Pay special attention to SQLAlchemy model standards to avoid common issues:
  - Use absolute imports for models (`from models.email import Email`)
  - Use fully qualified paths in relationships (`relationship("models.email.Email", ...)`)
  - Follow type hint guidelines for SQLAlchemy 2.0

## File Management

### Archival Process
When archiving files (e.g., deprecated code, old configurations):

1. Create a date-based backup directory if it doesn't exist:
   ```bash
   mkdir -p backup/YYYYMMDD
   ```

2. Copy the file to the backup directory with appropriate extension:
   - `.bak` for general backups
   - `.mock` for test files
   - Original extension for database files
   ```bash
   cp file.py backup/YYYYMMDD/file.py.bak
   ```

3. Remove the original file using git:
   ```bash
   git rm file.py
   ```

4. Commit both the backup and removal:
   ```bash
   git commit -m "chore: archive file.py

   - Moved to backup/YYYYMMDD/file.py.bak
   - [Reason for archival]"
   ```

This process ensures:
- No code is permanently lost
- Changes are properly tracked
- Backups are organized by date
- Files can be restored if needed

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

## Schema Management
See [Database Design](docs/database-design.md) for complete documentation on:
- Database schema and design decisions
- ID handling and validation
- Migration procedures
- Data type choices

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

## Testing

We use integration tests that validate functionality against the actual Gmail API. This ensures our code works correctly in real-world conditions. Key test areas include:

- Gmail API authentication
- Label operations
- Email fetching and filtering
- Email processing and storage

For detailed testing information, see [Testing Documentation](docs/testing.md).

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

## File Naming Conventions
1. **Application Files**
   - Main apps: `app_*.py` (e.g., `app_email_analyzer.py`)
   - Models: `model_*.py` (e.g., `model_email.py`)
   - Tests: `test_*.py` (e.g., `test_email_analyzer.py`)

2. **Database Files**
   - Main database: `db_email_store.db`
   - Never use generic names like `emails.db`

## Documentation
- Project overview and quick start (README.md)
- Development roadmap (PROJECT_PLAN.md)
- Design decisions and architecture (docs/design-decisions.md)
- Session workflow guide (docs/session-workflow.md)
- Project guidelines (docs/contributing.md)
