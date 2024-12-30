# Closing a Development Session

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

### 1. Code Quality
- [ ] Run linter and type checks
```bash
black .
mypy .
```
- [ ] Run all tests
```bash
python -m pytest
```
- [ ] Review TODOs added during session

### 2. Documentation Updates
- [ ] Update docstrings for new/modified functions
- [ ] Update README.md if features added
- [ ] Add/update API documentation
- [ ] Review/update BACKLOG.md

### 3. Git Cleanup
- [ ] Review uncommitted changes
- [ ] Squash/rebase if needed
- [ ] Push all changes
```bash
git status
git push origin main
```

### 4. Update NEXT_SESSION.md
```bash
# Get recent changes for NEXT_SESSION.md
git log --oneline -n 5
git diff --name-status HEAD~1

# Run chat session manager to update documentation
python chat_session_manager.py close
```

Update the following sections:
1. Recent Changes
   - Code changes
   - New features
   - Refactoring

2. Current State
   - Branch status
   - Test status
   - Known issues

3. High Priority Tasks
   - Next steps
   - Blocked tasks
   - Technical debt

4. Environment
   - New dependencies
   - Configuration changes
   - Required setup

### 5. Final Checks
- [ ] All files saved
- [ ] All changes committed
- [ ] All changes pushed
- [ ] Environment documented
- [ ] Next steps clear

## Updating NEXT_SESSION.md

### Command to Generate Changes Summary
```bash
# Create changes summary
echo "## Recent Changes" > changes.tmp
git log --pretty=format:"- %s" -n 5 >> changes.tmp
echo -e "\n\n## Modified Files" >> changes.tmp
git diff --name-status HEAD~5 >> changes.tmp
```

### Template for NEXT_SESSION.md Update
```markdown
# Starting Point for Next Session

## Recent Changes
[Auto-generated from git log]

## Current State
- Branch: [current branch]
- Tests: [passing/failing]
- Coverage: [percentage]
- Environment: [any changes]

## High Priority Tasks
1. [Next immediate task]
   - Implementation details
   - Dependencies
   - Acceptance criteria

2. [Following tasks]
   - Priority order
   - Blocked/unblocked status

## Next Steps Suggestions
1. [Specific next implementation]
2. [Required preparation]
3. [Alternative paths]

## Environment
- New dependencies: [list]
- Configuration changes: [list]
- Database changes: [list]

## Important Files
- [List of key files modified]
- [New files added]
- [Files pending review]
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
