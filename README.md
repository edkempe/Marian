# Jexi Project

## Revision History
1.0.0 (2024-12-31) @dev
- Initial project setup
- Added core documentation
- Added minimalist ADR structure

## Overview

Jexi is an AI-powered email processing and analysis system that works alongside Marian, a specialized librarian AI that manages the Catalog system. The project uses a library-based architecture where:

- **Jexi** processes and analyzes emails, and can "check out" information it needs
- **Marian** acts as a librarian, maintaining metadata about where information is stored
- **The Catalog** is like a card catalog system - it doesn't store content, just references to where things are

### Components

1. **Jexi Core**: 
   - Email processing and analysis
   - Gmail integration
   - Can request and "check out" information through Marian
   - Uses the catalog but doesn't manage it

2. **Marian**: 
   - Acts as a librarian for the system
   - Maintains metadata about information location
   - Knows where everything is and how it relates
   - Maintains the source of truth hierarchy
   - Doesn't store content, only references to it

3. **The Catalog**:
   - Like a library's card catalog
   - Stores metadata, locations, and relationships
   - Contains references/pointers to actual content
   - Maps the knowledge landscape
   - Tracks hierarchies and dependencies

## Key Features
- Automated email analysis and categorization
- Smart priority scoring
- Catalog generation and management
- Integration with Gmail API
- Extensible analysis framework

## Quick Links
- [Project Checklist](docs/dev-checklist.md) - Development checklist
- [Testing Guide](docs/testing-guide.md) - Testing standards and procedures
- [Code Standards](docs/code-standards.md) - Coding conventions
- [Troubleshooting Guide](docs/troubleshooting.md) - Common issues and solutions
- [Session Logs](docs/session_logs/) - Development tracking
  - [Session Logs Guide](docs/session_logs/README.md) - Session logging standards
- [Contributing Guide](docs/contributing.md) - Development guidelines

## Getting Started
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables (see [Setup Guide](docs/setup.md))
4. Run tests: `python -m pytest tests/`

For detailed setup instructions, see the [Setup Guide](docs/setup.md).

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
  - `data/jexi.db`: Main database for email storage and analysis
  - Schema defined by SQLAlchemy models in `models/`

## Database Architecture

### Schema Management
The database schema is managed through a configuration-driven approach:

1. **Source of Truth**: `schema.yaml`
   - Defines all table structures
   - Specifies relationships and constraints
   - Single source of truth for database schema

2. **Code Generation**:
   - Models are generated from schema.yaml
   - Constants are generated for validation
   - Schema verification ensures integrity

3. **Database Structure**:
   - Single SQLite database: `data/jexi.db`
   - Unified session management
   - Clear table prefixes for logical separation

### Data Flow
```
schema.yaml (source of truth)
  → Generated Models & Constants
    → Database Schema
      → Application Code
```

### Database Files
- Main database: `data/jexi.db`
- Test database: `tests/test_data/test.db`

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

## Dependencies

Core dependencies:
- **sqlalchemy**: ORM and database management
- **pyyaml**: Schema configuration parsing
- **pytest**: Testing framework
- **google-api-python-client**: Gmail API integration
- **python-dotenv**: Environment configuration

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

### Application Utilities (`/utils/`)
Core utilities used throughout the application:

- **Date Utilities** (`date_utils.py`)
  ```python
  from utils.date_utils import format_iso_date, parse_iso_date
  
  # Format date to ISO string
  iso_date = format_iso_date(datetime.now())
  
  # Parse ISO date string
  date = parse_iso_date("2024-12-31T09:48:00")
  ```

- **String Utilities** (`string_utils.py`)
  ```python
  from utils.string_utils import camel_to_snake, snake_to_camel
  
  # Convert between cases
  snake = camel_to_snake("camelCase")  # -> "camel_case"
  camel = snake_to_camel("snake_case")  # -> "SnakeCase"
  ```

- **Email Utilities** (`email_utils.py`)
  ```python
  from utils.email_utils import parse_email_address, normalize_email
  
  # Parse email components
  local, domain = parse_email_address("user@example.com")
  
  # Normalize email address
  clean = normalize_email(" User@Example.COM ")
  ```

### Development Tools (`/tools/`)
Tools for development and maintenance:

- Documentation validators
- Build scripts
- Project standards

### Test Utilities (`/tests/utils/`)
Utilities specifically for testing:

- Database test helpers
- Email test fixtures
- Test constants

### Active Content
- `/docs` - Current documentation only
  - Design decisions
  - Guides and standards
  - Living documentation

### Historical Reference
- `/archive` - Historical content
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
The complete documentation is available in the [docs/](docs/) directory. Key documents include:

- [Setup Guide](docs/setup.md)
- [Development Standards](docs/code-standards.md)
- [Testing Guide](docs/testing-guide.md)
- [Database Design](docs/database-design.md)
- [Design Decisions](docs/design-decisions.md)
- [Contribution Guidelines](docs/contributing.md)
- [Development Checklist](docs/dev-checklist.md)
- [Session Workflow](docs/session-workflow.md)
- [Architecture Decisions](docs/adr/README.md)
- [Backup Guide](docs/backup.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Session Logs](docs/session_logs/)

See the [Documentation Index](docs/README.md) for a complete list of available documentation.

## Development Standards

- Follow the code standards in [Code Standards](docs/code-standards.md)
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
   - Log files stored in `logs/jexi.log`
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

For detailed testing information, see [Testing Guide](docs/testing-guide.md).

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

## External Tool Requirements

The project uses several external tools and services for development, testing, and runtime operations. For a complete list and rationale, see [ADR-0007: External Tool Integration](docs/adr/0007-external-tool-integration.md).

### Development Environment
- **Windsurf.ai**: Our primary IDE and AI copilot
  - Access via web browser at [windsurf.ai](https://windsurf.ai)
- **Git**: Version control
  ```bash
  brew install git
  ```
- **pre-commit**: Git hooks for code quality
  ```bash
  pip install pre-commit
  pre-commit install
  ```

### Build and Testing
- **pytest**: Test framework
  ```bash
  pip install pytest pytest-cov pytest-mock pytest-asyncio
  ```
- **bandit**: Security testing
  ```bash
  pip install bandit
  ```
- **rmlint**: Fast duplicate file detection
  ```bash
  # macOS
  brew install rmlint

  # Ubuntu/Debian
  sudo apt-get install rmlint

  # Fedora
  sudo dnf install rmlint
  ```

### Runtime Dependencies
- **SQLite**: Database (built into Python)
- **alembic**: Database migrations
  ```bash
  pip install alembic
  ```

### External Services
- **Gmail API**: Email integration
  - Requires OAuth 2.0 setup
  - See [Gmail API Setup Guide](docs/setup/gmail_api_setup.md)
- **Anthropic API**: AI processing
  - Requires API key
  - See [AI Integration Guide](docs/setup/ai_integration.md)

## File Naming Conventions
1. **Application Files**
   - Main apps: `app_*.py` (e.g., `app_email_analyzer.py`)
   - Models: `model_*.py` (e.g., `model_email.py`)
   - Tests: `test_*.py` (e.g., `test_email_analyzer.py`)

2. **Database Files**
   - Main database: `data/jexi.db`
   - Never use generic names like `emails.db`
