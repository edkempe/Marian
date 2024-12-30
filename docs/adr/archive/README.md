# ADR Archive

**Version:** 1.0.0
**Status:** Authoritative
**Template:** [../../templates/ARCHIVING.md](../../templates/ARCHIVING.md)

> Archive of superseded Architecture Decision Records (ADRs), maintaining decision history while keeping active ADRs clear.

## Quick Reference
```bash
# Archive an ADR
mv ADR001_old.md ARCHIVED_$(date +%Y%m%d_%H%M)_ADR001_old.md

# Find archived ADR by content
grep -r "decision" .

# List recent archives
ls -lt | head
```

## Overview
- **Purpose**: Store superseded ADRs
- **Stability**: Stable
- **Maintenance**: Active
- **Format**: Markdown

---

## Directory Structure
```
/docs/adr/archive/
├── README.md                                    # This file
└── ARCHIVED_YYYYMMDD_HHMM_ADR[0-9]*.md         # Archived ADRs
```

## Archive Guidelines

1. **What to Archive**
   - Superseded decisions
   - Updated architectures
   - Historical context
   - Old design choices

2. **When to Archive**
   - Architecture changes
   - Decision updates
   - Strategy shifts
   - Technology changes

3. **Archive Process**
   - Add ARCHIVED prefix with timestamp
   - Move to `/docs/adr/archive`
   - Update any references
   - Note archival in session log

4. **Archive Organization**
   - Flat directory structure
   - No subdirectories
   - Chronological by archive date

## Version History
- 1.0.0: Initial version - ADR archive setup
