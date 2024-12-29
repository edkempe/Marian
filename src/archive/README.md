# Source Code Archive

**Version:** 1.0.0  
**Status:** Authoritative  
**Template:** [../../docs/templates/ARCHIVING.md](../../docs/templates/ARCHIVING.md)

> Archive of superseded source code, maintaining project history while keeping active codebase clear.

## Quick Reference
```bash
# Archive a source file
mv old_code.py ARCHIVED_$(date +%Y%m%d_%H%M)_old_code.py

# Find archived code by content
grep -r "search_term" .

# List recent archives
ls -lt | head
```

## Overview
- **Purpose**: Store superseded source code
- **Stability**: Stable
- **Maintenance**: Active
- **Python**: Multiple versions (see individual files)

---

## Directory Structure
```
/src/archive/
├── README.md                           # This file
└── ARCHIVED_YYYYMMDD_HHMM_*.py        # Archived Python files
```

## Archive Guidelines

1. **What to Archive**
   - Superseded implementations
   - Old class/function versions
   - Deprecated features
   - Refactored code

2. **When to Archive**
   - Major refactoring
   - Breaking changes
   - Deprecated features
   - Code restructuring

3. **Archive Process**
   - Add ARCHIVED prefix with timestamp
   - Move to `/src/archive`
   - Update any imports/references
   - Note archival in session log

4. **Archive Organization**
   - Flat directory structure
   - No subdirectories
   - Chronological by archive date

## Version History
- 1.0.0: Initial version - Source code archive setup
