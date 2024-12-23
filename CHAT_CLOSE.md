# Closing a Development Session

## Important Guidelines
1. Once the closing process begins:
   - DO NOT make any new code changes
   - DO NOT attempt to fix issues discovered during closing
   - Instead, document all issues in NEXT_SESSION.md and BACKLOG.md
   - Revert any changes made during the closing process

2. If issues are discovered:
   - Add them to the "Issues and Blockers" section in NEXT_SESSION.md
   - Add corresponding tasks to BACKLOG.md with appropriate priority
   - Document any temporary workarounds or important context

## Session Summary Template
```markdown
## Session Summary [DATE]

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
```

## Pre-Close Checklist

### 1. Documentation Updates
- [ ] Update NEXT_SESSION.md
  - Add recent changes
  - Document current state
  - List issues and blockers
  - Define next steps
- [ ] Update BACKLOG.md
  - Add new tasks discovered
  - Update priorities
  - Add technical debt items

### 2. Git Status
- [ ] Review uncommitted changes
- [ ] Commit or revert changes
- [ ] Push final commits

### 3. Final Review
- [ ] All files saved
- [ ] All changes committed
- [ ] Documentation updated
- [ ] Next steps clear

## Updating NEXT_SESSION.md

### Command to Generate Changes Summary
```bash
# Get recent changes
git log --oneline -n 5

# Get modified files
git diff --name-status HEAD~1

# Update documentation
python chat_session_manager.py close
```

## Common Close-out Commands
```bash
# Format code
black .

# Run type checks
mypy .

# Run tests
python -m pytest

# Check git status
git status

# View changes
git diff

# Commit changes
git add .
git commit -m "type: description"

# Push changes
git push origin main

# Update documentation
python update_docs.py  # if available
```

## Final Message Template
```
Session completed! Here's a summary:

1. Completed Tasks:
   - [List tasks]

2. Changes Made:
   - [List significant changes]

3. Next Steps:
   - [List immediate next steps]

4. Updated Documentation:
   - NEXT_SESSION.md
   - [Other docs]

All changes have been committed and pushed. The project is ready for the next session.
```
