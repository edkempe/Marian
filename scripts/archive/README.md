# Scripts Archive

**Version:** 1.0.0  
**Status:** Authoritative  
**Template:** [Archiving Guide](/docs/templates/ARCHIVING.md)

> Archive of superseded scripts and utilities, maintaining script history while keeping active tools clear.

## Quick Reference
```bash
# Archive a script
mv old_script.sh ARCHIVED_$(date +%Y%m%d_%H%M)_old_script.sh

# Find archived script by content
grep -r "function_name" .

# List recent archives
ls -lt | head
```

## Overview
- **Purpose**: Store superseded scripts
- **Stability**: Stable
- **Maintenance**: Active
- **Languages**: Multiple (bash, python, etc.)

---

## Directory Structure
```
/scripts/archive/
├── README.md                           # This file
├── ARCHIVED_YYYYMMDD_HHMM_*.sh        # Archived shell scripts
├── ARCHIVED_YYYYMMDD_HHMM_*.py        # Archived Python scripts
└── ARCHIVED_YYYYMMDD_HHMM_*.{ext}     # Other script types
```

## Archive Guidelines

1. **What to Archive**
   - Old automation scripts
   - Deprecated tools
   - One-off utilities
   - Migration scripts

2. **When to Archive**
   - Tool updates
   - Process changes
   - Automation improvements
   - One-time scripts

3. **Archive Process**
   - Add ARCHIVED prefix with timestamp
   - Move to `/scripts/archive`
   - Update any references
   - Note archival in session log

4. **Archive Organization**
   - Flat directory structure
   - No subdirectories
   - Chronological by archive date

## Version History
- 1.0.0: Initial version - Scripts archive setup
