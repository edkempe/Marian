# Marian Setup Guide

## Prerequisites
- Python 3.12.8 or higher
- Gmail API credentials (`credentials.json`) from Google Cloud Console
- Anthropic API key for Claude-3
- pip (Python package installer)
- git

## Initial Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Marian
```

### 2. Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

### 3. Package Installation
```bash
# Install package in development mode
pip install -e .

# Install all requirements
pip install -r requirements.txt
```

### 4. Environment Configuration
The project uses both environment variables and a modular configuration system:

#### Environment File Setup
1. Copy the example environment file:
```bash
cp docs/examples/.env.example .env
```

2. Edit `.env` with your settings:
- ANTHROPIC_API_KEY
- Database paths
- Gmail API credentials paths
- Logging configuration
- Analysis settings

See `docs/examples/.env.example` for all available options and descriptions.

#### Environment Variables
Required environment variables must be set before running the application:
```bash
# API Keys
export ANTHROPIC_API_KEY=your_api_key_here

# Database Paths (if different from defaults in .env)
export DB_EMAIL_PATH=path/to/email.db
export DB_ANALYSIS_PATH=path/to/analysis.db
export DB_LABEL_HISTORY_PATH=path/to/labels.db

# Gmail API Paths (if different from defaults)
export GMAIL_CREDENTIALS_PATH=path/to/credentials.json
export GMAIL_TOKEN_PATH=path/to/token.pickle

# Logging
export LOG_LEVEL=INFO
export LOG_FILE=path/to/log/file
```

#### Core Configuration Files
- `constants.py`: Email processing configuration
  - API settings for email analysis
  - Email database configuration
  - Email processing parameters
  - Logging and metrics settings

- `catalog_constants.py`: Catalog system configuration
  - Database settings for catalog
  - Semantic analysis parameters
  - API settings for semantic matching

- `librarian_constants.py`: Librarian-specific settings

#### Gmail API Setup
1. Place your Gmail API credentials:
```bash
cp path/to/your/credentials.json config/credentials.json
```

2. First-time authentication:
```bash
python app_get_mail.py --auth-only
```

3. Verify token creation:
```bash
ls -l config/token.pickle  # Should exist after authentication
```

### 5. Database Initialization
```bash
# Initialize databases
python init_db.py
```

### 6. Code Quality Tools
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### 7. Test Environment Setup
#### Gmail API Authentication
- Valid Gmail credentials required in `config/credentials.json`
- Valid token required in `config/token.pickle`
- Run `python app_get_mail.py` first to authenticate
- Token must be refreshed when expired
- Tests will stall if authentication is needed

#### Database Setup
- Email database must be initialized
- Label database must be synced
- Run `python app_get_mail.py --sync-labels` to initialize

#### Test Data Requirements
- Gmail account must have some emails
- Tests use real emails from the last 7 days
- Limited to small batches to prevent timeouts

### 8. Test Setup
```bash
# Create test databases
python -m pytest --setup-only
```

## Verification

### 1. Check Environment
```bash
# Verify Python version
python --version

# Check installed packages
pip list
```

### 2. Test Database Connections
```bash
python -c "from database.config import get_email_session, get_analysis_session; print('Database connections OK')"
```

### 3. Run Tests
```bash
python -m pytest
```

## Troubleshooting Common Setup Issues
If you encounter issues during setup:
1. Check Python version compatibility
2. Verify all environment variables are set
3. Ensure credentials files are in correct locations
4. Validate database initialization
5. Check API access and permissions

For detailed troubleshooting steps, see `docs/troubleshooting.md`.

## Common Issues and Solutions

### Import Errors
If you encounter import errors when running tests or scripts:
1. Ensure you're in the virtual environment
2. Verify the package is installed in development mode
3. Check PYTHONPATH includes the project root

### Database Errors
1. Check if database files exist in the correct locations
2. Verify permissions on database files
3. Run `init_db.py` if databases are missing

### API Key Issues
1. Ensure .env file exists with required keys
2. Check key format and validity
3. Verify environment variables are loaded

## Development Workflow

### 1. Starting a New Session
```bash
# Activate environment
source venv/bin/activate

# Pull latest changes
git pull origin main

# Update dependencies if needed
pip install -r requirements.txt
```

### 2. Before Committing
```bash
# Format code
black .

# Run tests
python -m pytest

# Check types
mypy .
```

### 3. After Development
```bash
# Update documentation if needed
# Update NEXT_SESSION.md
# Commit changes with clear messages
```

## Additional Resources
- See `README.md` for project overview
- Check `CHAT_START.md` for session workflow
- Review `CODE_STANDARDS.md` for coding standards
- Refer to `docs/BACKLOG.md` for task tracking
