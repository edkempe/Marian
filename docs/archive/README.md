# Documentation Archive

**Version:** 1.0.1
**Status:** Authoritative
**Template:** See [../templates/ARCHIVING.md](../templates/ARCHIVING.md) for archiving guidelines.

> Archive of superseded documentation files, maintaining project history while keeping active documentation clear.

## Quick Reference
```bash
# Archive a document
mv old-doc.md ARCHIVED_$(date +%Y%m%d_%H%M)_old-doc.md

# Find archived document by topic
grep -r "topic" .

# List recent archives
ls -lt | head
```

## Overview
- **Purpose**: Store superseded documentation
- **Stability**: Stable
- **Maintenance**: Active
- **Python**: N/A (Documentation only)

---

## Archive Guidelines

1. **When to Archive**
   - Major document revisions
   - Superseded documentation
   - Obsolete but historically relevant docs
   - Documentation restructuring

2. **Naming Convention**
   - Format: `ARCHIVED_YYYYMMDD_HHMM_filename.md`
   - Example: `ARCHIVED_20241228_0621_testing-guide.md`
   - Keep original file extension
   - Use original filename in archive name

3. **Archive Process**
   - Add ARCHIVED prefix with timestamp
   - Move to `/docs/archive`
   - Update any references
   - Note archival in session log

4. **Archive Organization**
   - Flat directory structure
   - No subdirectories
   - Chronological by archive date
   - Original filenames preserved

---

## Related Documentation
- Parent: `../README.md` - Documentation directory
- `../templates/README.md` - Documentation templates
- `../../archive/README.md` - Code and config archives

## Version History
- 1.0.0: Initial version - Documentation archive setup
- 1.0.1: Updated header to reference archiving template
