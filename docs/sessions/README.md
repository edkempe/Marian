# Session Management Guide

## Session Documentation Standards

### Naming Convention
- Format: `session_YYYYMMDD_HHMM.md`
- Example: `session_20241225_1009.md`

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
1. Copy `SESSION_TEMPLATE.md` with correct naming
2. Fill in session overview and initial goals
3. Review previous session notes and backlog
4. Update progress log as work begins

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
