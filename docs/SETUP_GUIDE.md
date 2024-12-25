# Marian Setup Guide

## Prerequisites
- Python 3.8 or higher
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
The project uses a .env file for configuration. If you don't have one:
```bash
# Copy example environment file (if you don't have a .env file)
cp .env.example .env

# Edit .env with your settings:
# - ANTHROPIC_API_KEY
# - Database paths
# - Gmail API credentials
# - Other configurations
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

### 7. Test Setup
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
- Refer to `BACKLOG.md` for task tracking
