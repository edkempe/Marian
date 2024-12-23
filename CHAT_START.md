# Starting a New Development Session

## Message Template
```
Hi! Let's continue working on Marian. Here's what I'd like to focus on today:

[Brief description of your chosen task]

Please review the project documentation and perform the standard checks as outlined in CHAT_START.md.
```

## Key Documents to Review
1. `README.md`
   - Project overview and purpose
   - Core features and functionality
   - Tech stack and dependencies

2. `SETUP.md`
   - Complete setup instructions
   - Environment configuration
   - Development workflow
   - Common issues and solutions

3. `NEXT_SESSION.md`
   - Recent changes and progress
   - Current state of the project
   - Suggested next steps

4. `guidelines.md`
   - Project guidelines and constraints
   - Code style preferences
   - Security requirements

5. `BACKLOG.md`
   - Prioritized task list
   - Implementation details
   - Dependencies between tasks

## Pre-Development Checklist

### 1. Review Previous Sessions
- Check recent session summaries in `docs/sessions/`
- Review NEXT_SESSION.md from last session
- Pay special attention to:
  - Issues and blockers from last session
  - Incomplete tasks
  - Environment changes
  - Testing status
  - Recent schema modifications
  - API integration updates

### 2. Environment Verification
```bash
# Verify virtual environment is activated
which python  # Should point to venv/bin/python

# Check Python version and packages
python --version
pip list

# Verify environment variables
python -c "import os; print('ANTHROPIC_API_KEY:', bool(os.getenv('ANTHROPIC_API_KEY')))"
```

### 3. Repository Status
```bash
# Check git status
git status

# Pull latest changes
git pull origin main

# View recent commits
git log -n 5 --oneline
```

### 4. Code Quality Tools
```bash
# Run pre-commit hooks
pre-commit run --all-files

# Format code
black .

# Run type checks
mypy .
```

### 5. Project Structure Review
```bash
# View directory structure
tree -L 2 -I 'venv|__pycache__|*.pyc'

# Check core files
ls -la *.py
ls -la models/
ls -la database/
ls -la tests/
```

### 6. Database Status
```bash
# Check database files
ls -la *.db

# Verify database connections
python -c "from database.config import get_email_session, get_analysis_session; print('Database connections OK')"
```

### 7. Test Suite
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.
```

### 8. Code Review Checks
- [ ] Review any open pull requests
- [ ] Check for pending code reviews
- [ ] Look for TODO comments in recent changes
- [ ] Verify test coverage for recent changes

### 9. Documentation Sync
- [ ] Verify README.md is up to date
- [ ] Check NEXT_SESSION.md reflects latest changes
- [ ] Review BACKLOG.md for task priorities
- [ ] Update documentation if needed

### 10. Development Tools
- [ ] IDE/Editor configuration
- [ ] Linter settings (see .pre-commit-config.yaml)
- [ ] Debugger setup
- [ ] API keys and credentials (check .env)

## After Checks
1. Confirm understanding of current state
2. Outline implementation plan for chosen task
3. Create new branch if needed
4. Start development with clear objectives

## End of Session
1. Update NEXT_SESSION.md
2. Run pre-commit hooks on changes
3. Commit with clear messages
4. Push to remote repository
5. Document any new tasks in BACKLOG.md

## Common Commands
```bash
# Activate environment
source venv/bin/activate

# Run analysis viewer
python analysis_viewer.py --timeframe today --detail normal

# Run tests
python -m pytest

# Format and check code
pre-commit run --all-files

# Check types
mypy .

# View setup instructions
cat SETUP.md
```

## Troubleshooting
If you encounter any issues, refer to:
1. `docs/troubleshooting.md` - Comprehensive troubleshooting guide
2. `SETUP.md` - Common setup and environment issues
3. `.env.example` - Required environment variables

For quick environment reset:
```bash
deactivate  # Exit current venv
source venv/bin/activate  # Reactivate venv
pip install -r requirements.txt  # Reinstall dependencies
```
