# Project Setup Guide

## Prerequisites
1. Python 3.12.8 or higher
2. Gmail API credentials (`credentials.json`) from Google Cloud Console
3. Anthropic API key for Claude-3

## Initial Setup
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

## Test Environment Setup
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

## Configuration System
The project uses a modular configuration system:

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

## Troubleshooting Common Setup Issues
If you encounter issues during setup:
1. Check Python version compatibility
2. Verify all environment variables are set
3. Ensure credentials files are in correct locations
4. Validate database initialization
5. Check API access and permissions
