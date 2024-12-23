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

2. `NEXT_SESSION.md`
   - Recent changes and progress
   - Current state of the project
   - Suggested next steps

3. `guidelines.md`
   - Project guidelines and constraints
   - Code style preferences
   - Security requirements

4. `BACKLOG.md`
   - Prioritized task list
   - Implementation details
   - Dependencies between tasks

## Pre-Development Checklist

### 1. Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Verify Python version
python --version

# Check installed packages
pip list
```

### 2. Repository Status
```bash
# Check git status
git status

# Pull latest changes
git pull origin main

# View recent commits
git log -n 5 --oneline
```

### 3. Project Structure Review
```bash
# View directory structure
tree -L 2 -I 'venv|__pycache__|*.pyc'

# Check core files
ls -la *.py
ls -la models/
ls -la database/
```

### 4. Database Status
```bash
# Check database files
ls -la *.db

# Verify database connections
python -c "from database.config import get_email_session, get_analysis_session; print('Database connections OK')"
```

### 5. Code Review Checks
- [ ] Review any open pull requests
- [ ] Check for pending code reviews
- [ ] Look for TODO comments in recent changes
- [ ] Verify test coverage for recent changes

### 6. Documentation Sync
- [ ] Verify README.md is up to date
- [ ] Check NEXT_SESSION.md reflects latest changes
- [ ] Review BACKLOG.md for task priorities
- [ ] Update documentation if needed

### 7. Development Tools
- [ ] IDE/Editor configuration
- [ ] Linter settings
- [ ] Debugger setup
- [ ] API keys and credentials

## After Checks
1. Confirm understanding of current state
2. Outline implementation plan for chosen task
3. Create new branch if needed
4. Start development with clear objectives

## End of Session
1. Update NEXT_SESSION.md
2. Commit all changes with clear messages
3. Push to remote repository
4. Document any new tasks in BACKLOG.md

## Common Commands
```bash
# Activate environment
source venv/bin/activate

# Run analysis viewer
python analysis_viewer.py --timeframe today --detail normal

# Run tests
python -m pytest

# Format code
black .

# Check types
mypy .
```
