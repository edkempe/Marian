# Starting a New Development Session

> **IMPORTANT**: The [Development Session Checklist](DEV_SESSION_CHECKLIST.md) is the authoritative source for development session procedures. This document provides additional context and detailed explanations for the checklist items.

## CRITICAL: Review and Understand Project Guidelines
Before starting any development work, you MUST:
1. Review and understand ALL project guidelines in `docs/GUIDELINES.md`
2. Acknowledge and commit to following these standards
3. Ensure all work adheres to these guidelines throughout the session

## Message Template
```
Hi! Let's continue working on Marian. Here's what I'd like to focus on today:

[Brief description of your chosen task]

Please review the project documentation and perform the standard checks as outlined in CHAT_START.md.
```

## Key Documents to Review
1. `docs/GUIDELINES.md` (REQUIRED FIRST)
   - Project guidelines and constraints
   - Code style preferences
   - Security requirements
   - Development standards
   - These guidelines are mandatory and must be followed

2. `README.md`
   - Project overview and purpose
   - Core features and functionality
   - Tech stack and dependencies

3. `SETUP_GUIDE.md`
   - Complete setup instructions
   - Environment configuration
   - Development workflow
   - Common issues and solutions

4. `docs/BACKLOG.md`
   - Prioritized task list
   - Implementation details
   - Dependencies between tasks

## Pre-Development Checklist
1. **Verify Development Environment**
   - Ensure all prerequisites are met (see [SETUP_GUIDE.md](SETUP_GUIDE.md))
   - Verify environment is properly configured
   - Check all required credentials are in place
   - Test environment is ready for development

2. **Start Session Log**
   - Create new log file: docs/sessions/YYYY-MM-DD-HH-MM.md
   - Record session focus and objectives
   - Start running log with timestamps
   - Track all significant actions and decisions

3. **Review Current State**
   - Check git status for any pending changes
   - Review modified files list
   - Note any pending tasks or blockers

4. **Code Review**
   - Check git status
   - Review uncommitted changes
   - Note modified files
   - Check branch status

5. **Testing Status**
   - Run test suite
   - Note any failing tests
   - Check test coverage
   - Review test requirements

6. **Documentation**
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
2. `SETUP_GUIDE.md` - Common setup and environment issues
3. `.env.example` - Required environment variables
