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
1. Review Recent Changes
   - Check NEXT_SESSION.md for latest updates
   - Review modified files list
   - Note any pending tasks or blockers

2. Environment Setup
   - Activate virtual environment
   - Install/update dependencies
   - Check database migrations
   - Verify test database

3. Code Review
   - Check git status
   - Review uncommitted changes
   - Note modified files
   - Check branch status

4. Testing Status
   - Run test suite
   - Note any failing tests
   - Check test coverage
   - Review test requirements

5. Documentation
   - Check for outdated docs
   - Review API changes
   - Note needed updates
   - Check migration guides

## Common Commands
```bash
# Environment
source venv/bin/activate
pip install -r requirements.txt

# Testing
python -m pytest
python -m pytest -v tests/specific_test.py

# Database
alembic upgrade head
alembic history

# Git
git status
git branch
git log --oneline -n 5
```

## Troubleshooting
If you encounter any issues, refer to:
1. `docs/troubleshooting.md` - Comprehensive troubleshooting guide
2. `SETUP.md` - Common setup and environment issues
3. `.env.example` - Required environment variables
