# Code Archive

**Version:** 1.0.0  
**Status:** Authoritative

> Archive of superseded code, configurations, and non-documentation files, maintaining project history while keeping active codebase clear.

## Quick Reference
```bash
# Archive a Python file
mv old_code.py ARCHIVED_$(date +%Y%m%d_%H%M)_old_code.py

# Archive a config file
mv config.yaml ARCHIVED_$(date +%Y%m%d_%H%M)_config.yaml

# Find archived file by content
grep -r "search_term" .

# List recent archives
ls -lt | head
```

## Overview
- **Purpose**: Store superseded code and configs
- **Stability**: Stable
- **Maintenance**: Active
- **Python**: Multiple versions (see individual files)

---

## Directory Structure
```
/archive/
├── README.md                           # This file
├── ARCHIVED_YYYYMMDD_HHMM_*.py        # Python files
├── ARCHIVED_YYYYMMDD_HHMM_*.yaml      # Config files
├── ARCHIVED_YYYYMMDD_HHMM_*.sh        # Shell scripts
└── ARCHIVED_YYYYMMDD_HHMM_*.{ext}     # Other files
```

## Archive Guidelines

1. **What to Archive**
   - Superseded code files
   - Old configuration files
   - Deprecated scripts
   - Test files no longer needed
   - Database schemas
   - Build files

2. **When to Archive**
   - Major code refactoring
   - Configuration changes
   - System upgrades
   - Test suite updates
   - Schema migrations

3. **Naming Convention**
   - Format: `ARCHIVED_YYYYMMDD_HHMM_filename.ext`
   - Example: `ARCHIVED_20241228_0621_email_processor.py`
   - Keep original file extension
   - Use original filename in archive name

4. **Archive Process**
   - Add ARCHIVED prefix with timestamp
   - Move to `/archive`
   - Update any imports/references
   - Note archival in session log

5. **Archive Organization**
   - Flat directory structure
   - No subdirectories
   - Chronological by archive date
   - Original extensions preserved

---

## Security Notes
- Remove sensitive data before archiving
- Check for hardcoded credentials
- Verify no API keys or tokens
- Document any security-related changes

## Testing Impact
- Note any test dependencies
- Archive related test files together
- Document test coverage changes
- Keep test/code pairs together

---

## Related Documentation
- Parent: `../README.md` - Project root
- `../docs/archive/README.md` - Documentation archives
- `../docs/dev-checklist.md` - Development procedures

## Version History
- 1.0.0: Initial version - Code archive setup
