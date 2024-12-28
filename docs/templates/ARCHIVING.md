# Archiving Guide

**Version:** 1.0.1  
**Status:** Authoritative

> Master template and guidelines for archiving content in the Marian project.

## Overview

### Archive Locations

1. **Code Archives**
   - `/src/archive` - Source code files
   - `/tests/archive` - Test files and fixtures
   - `/scripts/archive` - Utility scripts
   - `/config/archive` - Configuration files

2. **Documentation Archives**
   - `/docs/archive` - General documentation
   - `/docs/adr/archive` - Architecture Decision Records

Each location maintains its own README following this template.

### Common Standards

1. **Naming Convention**
   ```
   ARCHIVED_YYYYMMDD_HHMM_filename.ext
   ```
   - Timestamp in UTC
   - Original filename preserved
   - Original extension preserved

2. **Archive Process**
   1. Identify content to archive
   2. Choose appropriate archive location:
      - Source code → `/src/archive`
      - Tests → `/tests/archive`
      - Scripts → `/scripts/archive`
      - Configs → `/config/archive`
      - Documentation → `/docs/archive`
      - ADRs → `/docs/adr/archive`
   3. Add ARCHIVED prefix with timestamp
   4. Move to appropriate location
   5. Update any references
   6. Document in session log

3. **Organization**
   - Flat directory structure within each archive
   - No subdirectories
   - Chronological by archive date

### What to Archive

1. **Source Code** (`/src/archive`)
   - Superseded implementations
   - Old class/function versions
   - Deprecated features
   - Refactored code

2. **Tests** (`/tests/archive`)
   - Old test cases
   - Superseded fixtures
   - Deprecated test utilities

3. **Scripts** (`/scripts/archive`)
   - Old automation scripts
   - Deprecated tools
   - One-off utilities

4. **Configs** (`/config/archive`)
   - Old configuration files
   - Deprecated settings
   - Previous environments

5. **Documentation** (`/docs/archive`)
   - Superseded documentation
   - Old specifications
   - Past design decisions
   - Obsolete guides

6. **ADRs** (`/docs/adr/archive`)
   - Superseded decisions
   - Updated architectures
   - Historical context

### What NOT to Archive
- Backups (use `/backup`)
  - Current file copies
  - Active database snapshots
  - System configurations
  - Follow 3-2-1 backup strategy
- Temporary files (delete these)
- Generated files (regenerate when needed)
- Database files (use `/backup`)
- Current documentation versions

## Archive vs Backup
- **Archive**: Historical reference
  - Old versions
  - Superseded content
  - Past decisions
  - Manual process
  - No retention policy
  - Purpose: Historical context and reference

- **Backup**: Disaster recovery
  - Current file copies
  - Active database snapshots
  - System configurations
  - Automated process
  - Follows 3-2-1 backup strategy:
    1. Keep 3 copies of data
    2. Store on 2 different media types
    3. Keep 1 copy offsite
  - Purpose: Data recovery and business continuity

## Implementation

Each archive location implements these guidelines through a README.md that:
1. References this template
2. Provides location-specific quick reference
3. Details domain-specific guidelines
4. Maintains consistent structure

## Maintenance

1. **Archive Cleanup**
   - Annual review of archives
   - Remove truly obsolete content
   - Update references

2. **Documentation Updates**
   - Keep this template current
   - Update archive READMEs
   - Maintain consistency

## References
- `/src/archive/README.md` - Source code archive implementation
- `/tests/archive/README.md` - Test archive implementation
- `/scripts/archive/README.md` - Script archive implementation
- `/config/archive/README.md` - Configuration archive implementation
- `/docs/archive/README.md` - Documentation archive implementation
- `/docs/adr/archive/README.md` - ADR archive implementation
