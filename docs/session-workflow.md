# Marian Development Session Workflow

**Version:** 1.0.1
**Status:** Supporting documentation for development session procedures

> **Documentation Role**: This document provides detailed workflow examples and context. For authoritative session procedures, see [Development Session Checklist](dev-checklist.md). For AI-specific guidelines, see [AI Guidelines](ai-guidelines.md).

## Related Documentation
- [Development Session Checklist](dev-checklist.md) - Authoritative source for all development procedures
- [AI Guidelines](ai-guidelines.md) - AI-specific development guidelines
- [Session Logs Guide](session_logs/README.md) - Session logging standards

## Critical Guidelines

### Project Standards
Before starting any development work, you MUST:
1. Review and understand ALL project guidelines in `docs/contributing.md`
2. Acknowledge and commit to following these standards
3. Ensure all work adheres to these guidelines throughout the session

### Key Documents
1. `docs/contributing.md` (REQUIRED FIRST)
   - Project guidelines and constraints
   - Code style preferences
   - Security requirements
   - Development standards

2. `docs/backlog.md`
   - Source of truth for tasks and priorities
   - Implementation details
   - Dependencies between tasks

3. `README.md`
   - Project overview and purpose
   - Core features and functionality
   - Tech stack and dependencies

4. `setup.md`
   - Complete setup instructions
   - Environment configuration
   - Development workflow
   - Common issues and solutions

## Session Workflow

### 1. Starting a Session

#### Environment Setup
```bash
# 1. Activate environment
source venv/bin/activate

# 2. Verify environment
python --version  # Should be 3.12.8+
pip install -r requirements.txt

# 3. Run session start checks
python chat_session_manager.py start

# 4. Review current state
git log --oneline -n 5  # Review recent changes
cat docs/backlog.md     # Review current priorities

# 5. Review previous session
ls -lt docs/session-logs/ | head -n 2  # Find most recent session log
cat docs/session-logs/[most_recent_session].md  # Review previous session details
```

#### Pre-Development Checklist
1. **Environment Verification**
   - Ensure all prerequisites are met
   - Verify environment is properly configured
   - Check all required credentials are in place
   - Test environment readiness

2. **Documentation Review**
   - Check for outdated docs
   - Review API changes
   - Note needed updates
   - Check migration guides

3. **Testing Status**
   - Run test suite
   - Note any failing tests
   - Check test coverage
   - Review test requirements

#### Example Start Message
```
Hi! Let's continue working on Marian. Here's what I'd like to focus on today:

I want to implement the setup script for automating environment and database initialization.
This corresponds to the "Setup Script Creation" task in backlog.md under the Program Management workstream.
Based on the previous session log, this will build on the database schema work that was completed.

Please review the project documentation and perform the standard checks as outlined in dev-checklist.md.
```

### 2. During Development

#### Commit Message Examples
```bash
# Feature addition
git commit -am "feat: add database initialization to setup script

- Add SQLite database creation
- Add schema initialization
- Add test database setup
- Add environment variable handling"

# Bug fix
git commit -am "fix: correct session handling in email analyzer

- Fix connection leak in session management
- Add proper error handling
- Update tests to verify fix"

# Documentation
git commit -am "docs: update API documentation

- Add endpoint descriptions
- Update request/response examples
- Document error codes
- Add usage examples"

# Multiple changes
git commit -am "refactor: improve database operations

- Replace raw SQL with SQLAlchemy
- Add proper session management
- Improve error handling
- Update tests"
```

#### Development Guidelines
1. Make Small Incremental Changes
   - Focus on one issue at a time
   - Only make necessary changes
   - Avoid making unrelated modifications
   - Test and verify each change before moving to the next

2. Document All Significant Changes
   - Update session log with decisions
   - Note any deviations from plan
   - Record troubleshooting steps
   - Document API or schema changes

### 3. Closing a Session

#### Important Guidelines
1. Once the closing process begins:
   - DO NOT make any new code changes
   - DO NOT attempt to fix issues discovered during closing
   - Document all issues in `docs/backlog.md`
   - Revert any changes made during the closing process

2. If issues are discovered:
   - Add them to the backlog with appropriate priority
   - Document any temporary workarounds or important context
   - Include relevant technical details and impact

#### Final Checks
```bash
# 1. Run code quality checks
black .
mypy .

# 2. Run tests
python -m pytest
pytest --cov  # Get coverage report

# 3. Gather session metrics
git log --oneline -n 5  # Recent changes
git diff --name-status HEAD~1  # Changed files

# 4. Check dependencies
pip freeze > requirements.txt.new
diff requirements.txt requirements.txt.new

# 5. Update documentation
# Update backlog.md with task status and new items
vim docs/backlog.md

# 6. Generate session documentation
python chat_session_manager.py end

# 7. Final verification
git status  # Check for uncommitted changes
python -m pytest  # Verify tests still pass
git add .
git commit -am "chore: update session documentation"
git push origin main
```

#### Session Log Template
When creating `docs/session-logs/session-YYYYMMDD-HHMM.md`:
```markdown
## Session Summary YYYY-MM-DD HH:MM TZ

### Completed Tasks
- [List of completed tasks with PR/commit references]

### Code Changes
- [List of modified files with brief descriptions]
- [Any new files or deleted files]
- [Database schema changes]

### Environment Changes
- [New dependencies added]
- [Configuration changes]
- [Database migrations]

### Issues and Blockers
- [Any unresolved issues]
- [Technical debt introduced]
- [Dependencies on other tasks]

### Testing Status
- [Tests added/modified]
- [Test coverage changes]
- [Manual testing performed]

### Technical Decisions
- [Key decisions made during the session]
- [Rationale behind important changes]
- [Alternative approaches considered]
```

#### Example Close Message
```
Session completed! Here's a summary:

1. Completed Tasks:
   - Implemented database initialization in setup script (Program Management/Setup Script Creation)
   - Added schema creation functionality
   - Updated documentation

2. Changes Made:
   - Created setup_db.py
   - Modified database/config.py
   - Updated README.md with setup instructions

3. Backlog Updates:
   - Marked "Database Initialization" as complete
   - Added new task for credential management
   - Updated priority of environment configuration
   - Added note about potential security improvements

4. Updated Documentation:
   - Updated backlog.md with current status
   - Added database schema documentation
   - Updated setup instructions in README.md
   - Created session summary in docs/session-logs/session-YYYYMMDD-HHMM.md

All changes have been committed and pushed. The project is ready for the next session.
```

## Common Commands

### Environment Management
```bash
# Python/Pip
python --version
pip install -r requirements.txt
pip freeze > requirements.txt

# Virtual Environment
source venv/bin/activate
deactivate

# Database
alembic upgrade head
alembic history
```

### Testing
```bash
# Run all tests
python -m pytest

# Run specific test
python -m pytest -v tests/specific_test.py

# Get coverage
pytest --cov
```

### Git Operations
```bash
# Status and History
git status
git branch
git log --oneline -n 5

# Changes
git diff
git add .
git commit -am "type: description"
git push origin main
```

## Troubleshooting
If you encounter issues during development:

1. Check Common Resources:
   - `docs/troubleshooting.md` - Comprehensive guide
   - `setup.md` - Environment issues
   - `.env.example` - Configuration reference

2. Common Issues:
   - Environment activation problems
   - Missing credentials
   - Database connection issues
   - Test failures

3. Getting Help:
   - Check error logs
   - Review documentation
   - Search commit history
   - Document steps taken

## Best Practices

1. **Documentation Updates**
   - Keep backlog.md current with task status
   - Update README.md for new features
   - Maintain clear commit messages
   - Link session work to backlog items

2. **Code Quality**
   - Run formatters before commits
   - Maintain test coverage
   - Follow project guidelines

3. **Session Management**
   - Start with clear objectives from backlog
   - Document decisions and changes
   - Update backlog with current status
   - Link all work to backlog items

4. **Version Control**
   - Regular, small commits
   - Clear commit messages
   - Push changes frequently

## Version History
- 1.0.0: Initial consolidated workflow documentation, merging content from CHAT_START.md and CHAT_CLOSE.md
- 1.0.1: Updated version and status, added clear references to authoritative and related docs, added Related Documentation section
