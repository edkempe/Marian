# Development Session Checklists

**Version:** 1.0.0
**Status:** Authoritative source for all development session procedures

> **IMPORTANT**: This document is the authoritative source for development session procedures. While other documentation may provide additional context and details, this checklist must be followed for all development sessions.

## Starting a New Session

### 1. Initial Setup
- [ ] Review this checklist completely
- [ ] Review `docs/GUIDELINES.md` completely
- [ ] Review `README.md` for project overview
- [ ] Check `SETUP_GUIDE.md` for environment requirements
- [ ] Review `docs/BACKLOG.md` for current tasks

### 2. Environment Verification
- [ ] Activate virtual environment: `source venv/bin/activate`
- [ ] Verify all prerequisites are met
- [ ] Check all required credentials are in place
- [ ] Verify environment configuration
- [ ] Check Python version matches requirements (3.12.8+)

### 3. Session Documentation
- [ ] Create new session log: `docs/sessions/YYYY-MM-DD-HH-MM.md`
- [ ] Document session objectives
- [ ] Start running log with timestamps
- [ ] Link to relevant `BACKLOG.md` items

### 4. Code State Check
- [ ] Check git status for pending changes
- [ ] Review modified files
- [ ] Check branch status
- [ ] Note any pending tasks or blockers
- [ ] Review NEXT_SESSION.md from previous session

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
- [ ] Update `docs/BACKLOG.md`
  - Add incomplete tasks
  - Update completed task status
  - Add newly discovered tasks
  - Update task priorities if needed
- [ ] Create session log in `docs/sessions/session_YYYYMMDD_HHMM.md`
  - List completed tasks
  - Document code changes
  - Note environment changes
  - List issues and blockers
  - Document testing status
  - Record technical decisions
  - Include any security considerations
- [ ] Run automated close: `python chat_session_manager.py close`
- [ ] Review and adjust NEXT_SESSION.md

### 4. Final Verification
- [ ] Verify all changes are committed
- [ ] Run final test suite
- [ ] Push changes to repository
- [ ] Document any remaining issues in NEXT_SESSION.md
- [ ] Ensure all sensitive data is properly secured

### 5. Environment Cleanup
- [ ] Save all files
- [ ] Format code: `black .`
- [ ] Run type checks: `mypy .`
- [ ] Clear any temporary files
- [ ] Document any environment changes made
- [ ] Verify no sensitive data in logs or temporary files

## Version History
- 1.0.0: Initial authoritative checklist
