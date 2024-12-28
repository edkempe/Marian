# Development Session Checklists

**Version:** 1.0.4
**Status:** Authoritative source for all development session procedures

> **IMPORTANT**: This document is the authoritative source for development session procedures. For session log standards and procedures, see [Session Logs Guide](session_logs/README.md). All other documentation provides supporting details and context.

## Related Documentation

### Core Documents
- This checklist (`dev-checklist.md`) - Authoritative source for session procedures
- [Session Logs Guide](session_logs/README.md) - Authoritative source for session log standards
- [AI Guidelines](ai-guidelines.md) - AI-specific development guidelines
- [Session Workflow Guide](session-workflow.md) - Detailed workflow examples
- [Session Logs Guide](session_logs/README.md) - Session logging standards

### Supporting Documentation
- [Project Guidelines](contributing.md) - Code standards and contribution guidelines
- [Setup Guide](setup.md) - Environment setup and configuration
- [Project Design Decisions](design-decisions.md) - Architecture and technical decisions
- [Backlog](backlog.md) - Task tracking and prioritization
- [Tools and Scripts](#tools-and-scripts) - Automation and utility scripts

### Tools and Scripts
- `chat_session_manager.py` - Automates session documentation
  - Used for session start: `python chat_session_manager.py start`
  - Used for session close: `python chat_session_manager.py close`

## Starting a New Session

### 1. Initial Setup
- [ ] Review this checklist completely
- [ ] Review `docs/contributing.md` completely
- [ ] Review `README.md` for project overview
- [ ] Check `setup.md` for environment requirements
- [ ] Review `docs/backlog.md` for current tasks and priorities
- [ ] Review most recent session log in `docs/session_logs/` for context
- [ ] Review recent git history for context

### 2. Environment Verification
- [ ] Activate virtual environment: `source venv/bin/activate`
- [ ] Verify all prerequisites are met
- [ ] Check all required credentials are in place
- [ ] Verify environment configuration
- [ ] Check Python version matches requirements (3.12.8+)

### 3. Session Documentation
- [ ] Follow [Session Logs Guide](session_logs/README.md) for all session logging
- [ ] Document session objectives
- [ ] Start running log with timestamps
- [ ] Reference relevant `docs/backlog.md` items being worked on

### 4. Code State Check
- [ ] Check git status for pending changes
- [ ] Review modified files
- [ ] Check branch status
- [ ] Note any pending tasks or blockers
- [ ] Review recent commit messages for context

### 5. Testing Status
- [ ] Run test suite: `python -m pytest`
- [ ] Note any failing tests
- [ ] Check test coverage
- [ ] Review test requirements
- [ ] Verify Gmail API authentication status

## Ending a Session

### 1. Pre-Close Verification
- [ ] Stop all development work
- [ ] Run `git status` to check uncommitted changes
- [ ] Run test suite: `python -m pytest`
- [ ] Generate test coverage report: `pytest --cov`
- [ ] Document any failing tests

### 2. Session Metrics
- [ ] Review recent changes: `git log --oneline -n 5`
- [ ] Check file changes: `git diff --name-status HEAD~1`
- [ ] Check for new dependencies: Compare `requirements.txt`
- [ ] Document any API or schema changes

### 3. Documentation Updates
- [ ] Update `docs/backlog.md`
  - Add incomplete tasks
  - Update completed task status
  - Add newly discovered tasks
  - Update task priorities if needed
  - Document any blockers or dependencies
- [ ] Update session log in `docs/session_logs/session_log_YYYY-MM-DD.md`
  - List completed tasks
  - Document code changes
  - Note environment changes
  - List issues and blockers
  - Document testing status
  - Record technical decisions
  - Include any security considerations
  - Link to relevant backlog items
- [ ] Run automated close: `python chat_session_manager.py close`

### 4. Final Verification
- [ ] Verify all changes are committed
- [ ] Run final test suite
- [ ] Push changes to repository
- [ ] Ensure backlog is up to date with current status

### 5. Environment Cleanup
- [ ] Save all files
- [ ] Format code: `black .`
- [ ] Run type checks: `mypy .`
- [ ] Clear any temporary files
- [ ] Document any environment changes made
- [ ] Verify no sensitive data in logs or temporary files

## Version History
- 1.0.4: Update version, clarify documentation hierarchy, point to session_logs/README.md as authoritative for session logging
- 1.0.3: Update version, add clear references to all related docs, organize documentation into Core and Supporting categories
- 1.0.2: Add review of previous session logs to initial setup
- 1.0.1: Remove NEXT_SESSION.md references, strengthen backlog integration
- 1.0.0: Initial authoritative checklist
