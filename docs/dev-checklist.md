# Development Session Checklists

**Version:** 1.0.2
**Status:** Authoritative source for all development session procedures

> **IMPORTANT**: This document is the authoritative source for development session procedures. While other documentation may provide additional context and details, this checklist must be followed for all development sessions.

## Related Documentation

### Primary Documents
- This checklist (`dev-checklist.md`) - Authoritative source for session procedures
- `docs/BACKLOG.md` - Source of truth for tasks and priorities
- `docs/session_logs/YYYY-MM-DD.md` - Individual session logs

### Supporting Documents
- `docs/SESSION_WORKFLOW.md` - Detailed explanations and examples for all session procedures
- `docs/GUIDELINES.md` - Project guidelines and standards
- `docs/BACKLOG.md` - Task tracking and prioritization
- `docs/DESIGN_DECISIONS.md` - Architecture and design context

### Tools and Scripts
- `chat_session_manager.py` - Automates session documentation
  - Used for session start: `python chat_session_manager.py start`
  - Used for session close: `python chat_session_manager.py close`

## Starting a New Session

### 1. Initial Setup
- [ ] Review this checklist completely
- [ ] Review `docs/GUIDELINES.md` completely
- [ ] Review `README.md` for project overview
- [ ] Check `SETUP_GUIDE.md` for environment requirements
- [ ] Review `docs/BACKLOG.md` for current tasks and priorities
- [ ] Review most recent session log in `docs/session_logs/` for context
- [ ] Review recent git history for context

### 2. Environment Verification
- [ ] Activate virtual environment: `source venv/bin/activate`
- [ ] Verify all prerequisites are met
- [ ] Check all required credentials are in place
- [ ] Verify environment configuration
- [ ] Check Python version matches requirements (3.12.8+)

### 3. Session Documentation
- [ ] Create new session log: `docs/session_logs/YYYY-MM-DD.md`
- [ ] Document session objectives
- [ ] Start running log with timestamps
- [ ] Reference relevant `BACKLOG.md` items being worked on

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
- [ ] Update `docs/BACKLOG.md`
  - Add incomplete tasks
  - Update completed task status
  - Add newly discovered tasks
  - Update task priorities if needed
  - Document any blockers or dependencies
- [ ] Create session log in `docs/session_logs/YYYY-MM-DD.md`
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
- 1.0.2: Add review of previous session logs to initial setup
- 1.0.1: Remove NEXT_SESSION.md references, strengthen backlog integration
- 1.0.0: Initial authoritative checklist
