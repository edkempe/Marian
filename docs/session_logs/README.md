# Session Management Guide

## Session Documentation Standards

### Naming Convention
- Format: `YYYY-MM-DD.md`
- Example: `2024-12-27.md`
- Each day should have a single session log file
- Multiple sessions on the same day are added chronologically to that day's file

### Required Structure
- Use the standard template from `SESSION_TEMPLATE.md`
- All sessions must include:
  1. Session Overview (date, time, focus)
  2. Clear, measurable goals
  3. Chronological progress log
  4. Issues and blockers section
  5. Next steps for future sessions

### Best Practices
1. **Real-time Updates**
   - Update progress log as actions are taken
   - Document issues as they are discovered
   - Record decisions when they are made

2. **Clarity and Context**
   - Link to relevant documentation
   - Reference specific file changes
   - Include error messages and outcomes

3. **Future-proofing**
   - Document assumptions made
   - Note any temporary workarounds
   - Link to related backlog items

## Starting a Session
1. Check if a log exists for today's date
2. If no log exists, copy `SESSION_TEMPLATE.md` with today's date
3. If log exists, append new session with timestamp separator
4. Fill in session overview and initial goals
5. Review previous session notes and backlog
6. Update progress log as work begins

## During the Session
- Keep progress log updated in chronological order
- Document all significant actions and findings
- Link to any new or modified files
- Record blockers and issues immediately

## Closing a Session
1. Ensure all sections are completed
2. Update backlog with new items
3. Document next steps clearly
4. Link to any created documentation
5. If multiple sessions in a day, ensure clear separation between sessions

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
