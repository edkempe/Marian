# Marian Development Session Workflow

## Example Session Workflow

### 1. Starting a Session

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Run session start checks
python chat_session_manager.py start

# 3. Review documentation
cat NEXT_SESSION.md
cat docs/sessions/session_YYYYMMDD_HHMM.md
```

Example chat start message:
```
Hi! Let's continue working on Marian. Here's what I'd like to focus on today:

I want to implement the setup script for automating environment and database initialization.

Please review the project documentation and perform the standard checks as outlined in CHAT_START.md.
```

### 2. During Development

Example commit messages:
```bash
# Feature addition
git commit -m "feat: add database initialization to setup script

- Add SQLite database creation
- Add table schema initialization
- Add test data population
- Update documentation"

# Bug fix
git commit -m "fix: correct session handling in email analyzer

- Fix connection leak in get_analysis_session
- Add proper error handling
- Add session cleanup"

# Documentation
git commit -m "docs: update API documentation

- Add endpoint descriptions
- Update response formats
- Add error handling details"
```

### 3. Closing a Session

```bash
# 1. Run final checks
black .
mypy .
python -m pytest

# 2. Generate session close documentation
python chat_session_manager.py close

# 3. Review and commit changes
git add .
git commit -m "chore: update session documentation"
git push origin main
```

Example chat close message:
```
Session completed! Here's a summary:

1. Completed Tasks:
   - Implemented database initialization in setup script
   - Added schema creation functionality
   - Updated documentation

2. Changes Made:
   - Created setup_db.py
   - Modified database/config.py
   - Updated README.md with setup instructions

3. Next Steps:
   - Add credential management to setup script
   - Implement environment configuration
   - Add more test cases

4. Updated Documentation:
   - NEXT_SESSION.md updated with latest changes
   - Added database schema documentation
   - Updated setup instructions in README.md
   - Created session summary in docs/sessions/session_YYYYMMDD_HHMM.md

All changes have been committed and pushed. The project is ready for the next session.
```

## Document Relationships

### CHAT_START.md
- Provides session start checklist
- Lists required documentation review
- Contains environment setup steps

### CHAT_CLOSE.md
- Provides session close checklist
- Templates for documentation updates
- Guidelines for git cleanup

### NEXT_SESSION.md
- Updated automatically by chat_session_manager.py
- Contains current project state
- Lists next priority tasks

### BACKLOG.md
- Project backlog and priorities

### chat_session_manager.py
- Automates documentation updates
- Performs environment checks
- Generates session summaries

## Best Practices

1. **Documentation Updates**
   - Keep NEXT_SESSION.md current
   - Update README.md for new features
   - Maintain clear commit messages

2. **Code Quality**
   - Run formatters before commits
   - Maintain test coverage
   - Follow project guidelines

3. **Session Management**
   - Start with clear objectives
   - Document decisions and changes
   - End with clear next steps

4. **Version Control**
   - Regular, small commits
   - Clear commit messages
   - Push changes frequently
