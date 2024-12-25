# Session Management Guide

## Starting a Session

### Quick Start Template
```markdown
Hi! Let's continue working on Marian. Here's what I'd like to focus on today:

[Task description]

Guidelines to follow:
1. [Any specific guidelines for this session]
2. [Any specific constraints or requirements]
```

### Pre-Session Checklist
- [ ] Review NEXT_SESSION.md for context
- [ ] Check environment and dependencies
- [ ] Review relevant documentation
- [ ] Verify database state

## During the Session

### Session Notes Template
Create a new file: `sessions/YYYY-MM-DD-HH-MM.md`
```markdown
# Session Notes: YYYY-MM-DD HH:MM

## Objectives
- [List main objectives]

## Progress
- [Real-time updates]

## Decisions Made
- [Document key decisions]
```

## Closing a Session

### Quick Close Template
```markdown
Let's wrap up this session. Please:

1. Summarize the changes made
2. Document any pending items
3. Update NEXT_SESSION.md
```

### Close-out Checklist
- [ ] Commit all changes
- [ ] Update documentation
- [ ] Record issues in BACKLOG.md
- [ ] Create session summary

### Session Summary Template
```markdown
## Session Summary

### Completed Tasks
- [List completed items]

### Code Changes
- Modified files:
  - [file]: [description]
- New files:
  - [file]: [purpose]

### Environment Updates
- [ ] Dependencies added/updated
- [ ] Configuration changes
- [ ] Database changes

### Next Steps
- [Priority items for next session]
- [Known issues to address]
```

## Session Directory Structure
```
docs/
└── sessions/
    ├── README.md           # This guide
    ├── active/            # Current session notes
    │   └── YYYY-MM-DD.md
    └── archive/           # Past session summaries
        └── YYYY-MM/
            └── DD-HH-MM.md
```

## Best Practices
1. Always create a new session file
2. Keep real-time notes during session
3. Complete the close-out checklist
4. Archive session notes properly
