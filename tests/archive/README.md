# Test Archive

**Version:** 1.0.0  
**Status:** Authoritative  
**Template:** [Archiving Guide](/docs/templates/ARCHIVING.md)

> Archive of superseded test files and fixtures, maintaining test history while keeping active test suite clear.

## Quick Reference
```bash
# Archive a test file
mv old_test.py ARCHIVED_$(date +%Y%m%d_%H%M)_old_test.py

# Find archived test by content
grep -r "test_case" .

# List recent archives
ls -lt | head
```

## Overview
- **Purpose**: Store superseded test files
- **Stability**: Stable
- **Maintenance**: Active
- **Python**: Multiple versions (see individual files)

---

## Directory Structure
```
/tests/archive/
├── README.md                           # This file
├── ARCHIVED_YYYYMMDD_HHMM_*_test.py   # Archived test files
└── ARCHIVED_YYYYMMDD_HHMM_*.json      # Archived test fixtures
```

## Archive Guidelines

1. **What to Archive**
   - Old test cases
   - Superseded fixtures
   - Deprecated test utilities
   - Test data no longer needed

2. **When to Archive**
   - Test refactoring
   - API changes
   - Feature removal
   - Test strategy updates

3. **Archive Process**
   - Add ARCHIVED prefix with timestamp
   - Move to `/tests/archive`
   - Update any imports/references
   - Note archival in session log

4. **Archive Organization**
   - Flat directory structure
   - No subdirectories
   - Chronological by archive date

## Version History
- 1.0.0: Initial version - Test archive setup
