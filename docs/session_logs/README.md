# Session Logs Guide

**Version:** 1.0.1  
**Status:** Authoritative

> Comprehensive guide for maintaining consistent, detailed session logs that track development progress and decisions.

## Quick Reference
```bash
# Create today's session log
cp ../templates/session.md session_log_$(date +%Y-%m-%d).md

# List today's changes
grep "$(date +%H:%M)" session_log_$(date +%Y-%m-%d).md

# Find sessions about a topic
grep -r "topic" .

# Count sessions this month
ls -1 session_log_$(date +%Y-%m)*.md | wc -l
```

Common operations:
- Create new session log
- Add entry to existing log
- Find related sessions
- Review recent changes

## Overview
- **Purpose**: Track development progress
- **Stability**: Stable
- **Maintenance**: Active daily
- **Format**: Markdown files

---

## Directory Structure
```
/docs/session_logs/
├── README.md                     # This guide
├── session_log_YYYY-MM-DD.md    # Daily session logs
└── archive/                     # Archived logs
```

## Core Components

1. **Session Log Files**
   - Purpose: Daily development tracking
   - Format: `session_log_YYYY-MM-DD.md`
   - Example: `session_log_2024-12-28.md`

2. **Session Structure**
   ```markdown
   # Session Log YYYY-MM-DD
   
   ## Session Overview
   - Start: HH:MM [Timezone]
   - Focus: Brief description
   
   ## Progress Log
   1. HH:MM [Timezone]
      - Action taken
      - Implementation details
      - File changes
   ```

---

## Session Guidelines

### Required Sections
1. **Session Overview**
   - Date and timezone
   - Focus/Purpose
   - Related backlog items

2. **Progress Log**
   - Timestamped entries
   - Specific actions taken
   - File changes made

3. **Issues and Blockers**
   - Current blockers
   - Workarounds applied
   - Dependencies needed

4. **Next Steps**
   - Future tasks
   - Pending decisions
   - Required follow-ups

### Best Practices

1. **Real-time Updates**
   - Log changes as they happen
   - Include error messages
   - Document decisions made

2. **Clear Context**
   - Link to files changed
   - Reference backlog items
   - Note assumptions made

3. **Future-proofing**
   - Document workarounds
   - Note dependencies
   - Link related sessions

---

## Session Workflows

### Starting a Session
1. Check for existing log
   ```bash
   ls session_log_$(date +%Y-%m-%d).md
   ```

2. Create if needed
   ```bash
   cp ../templates/session.md session_log_$(date +%Y-%m-%d).md
   ```

3. Add session header
   ```markdown
   ## Session N - HH:MM [Timezone]
   - Focus: Brief description
   - Goals: Clear objectives
   ```

### During Session
1. Log changes promptly
2. Include file links
3. Note blockers
4. Update backlog

### Closing Session
1. Summarize changes
2. List next steps
3. Update backlog
4. Link new docs

---

## Related Documentation
- Parent: `../README.md` - Documentation root
- `../templates/session.md` - Session template
- `../dev-checklist.md` - Development procedures

## Version History
- 1.0.1: Added quick reference, improved workflows
- 1.0.0: Initial session log guide
