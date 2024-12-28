# Session Management Guide

## Session Documentation Standards

### Naming Convention
- Format: `session_log_YYYY-MM-DD.md`
- Example: `session_log_2024-12-27.md`
- Each day has a single log file
- Multiple sessions on the same day are added chronologically with timestamps

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
└── session_logs/
    ├── README.md           # This guide
    ├── SESSION_TEMPLATE.md # Template for new sessions
    └── session_log_YYYY-MM-DD.md  # Daily session logs
