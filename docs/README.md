# Documentation Directory

**Version:** 1.0.1  
**Status:** Authoritative

> Central location for all project documentation, following a structured hierarchy to maintain clarity and avoid duplication.

## Quick Reference
```bash
# View documentation hierarchy
cat ai-architecture.md

# Find documentation by topic
grep -r "topic" .

# Create new documentation
cp templates/directory-readme.md new-doc.md

# Archive documentation
mv old-doc.md archive/ARCHIVED_$(date +%Y%m%d_%H%M)_old-doc.md
```

Common operations:
- View documentation hierarchy in `ai-architecture.md`
- Find specific documentation using grep
- Create new docs using templates
- Archive old documentation in `/docs/archive`

## Overview
- **Purpose**: Maintain project documentation
- **Stability**: Stable
- **Maintenance**: Active
- **Python**: N/A (Documentation only)

---

## Project Structure
```
/
├── src/                    # Source code
│   └── archive/           # Archived source code files
├── tests/                  # Test files
│   └── archive/           # Archived test files
├── scripts/                # Utility scripts
│   └── archive/           # Archived scripts
├── config/                 # Configuration files
│   └── archive/           # Archived configs
├── docs/                   # Documentation
│   ├── archive/           # Archived documentation
│   ├── adr/               # Architecture Decision Records
│   │   └── archive/       # Archived ADRs
│   └── templates/         # Documentation templates
└── backup/                # Backup files (not for archival)
```

## Core Components

1. **Documentation Hierarchy**
   - Purpose: Define structure and relationships
   - When to use: Understanding doc organization
   - Example: See `ai-architecture.md`

2. **Documentation Standards**
   - Purpose: Maintain consistency
   - When to use: Creating/updating docs
   - Example: See `code-standards.md`

---

## Development Guide

### Adding New Documentation
1. File Organization
   - Use appropriate template from `/templates`
   - Follow naming conventions
   - Place in correct directory

2. Documentation Requirements
   - Clear version and status
   - Purpose and scope
   - Related documentation links
   - Examples where applicable

3. Review Requirements
   - Technical accuracy
   - Completeness
   - Clarity and organization

### Modifying Existing Documentation
1. Change Process
   - Update version number
   - Note changes in version history
   - Archive old versions in `/archive` if major changes

2. Review Process
   - Check cross-references
   - Update related docs
   - Verify hierarchy integrity

---

## File Naming Conventions
- `README.md` - All uppercase (standard)
- Other docs - Kebab-case (e.g., `ai-guidelines.md`)
- Avoid redundant suffixes (e.g., `-guide`, `-manual`)
- Documentation archives: `ARCHIVED_YYYYMMDD_HHMM_{filename}.md` (in `/docs/archive`)
- Code archives: `ARCHIVED_YYYYMMDD_HHMM_{filename}` (in `/archive`)

## Documentation Principles

1. **Single Source of Truth**
   - Code is primary documentation
   - Active docs explain "why" not "how"
   - Tests show usage patterns

2. **Necessary and Sufficient**
   - No duplicate information
   - Reference don't repeat
   - Archive don't delete

3. **Living Documentation**
   - Update as code changes
   - Archive old versions in `/docs/archive`
   - Keep history in archive

---

## Related Documentation
- Parent: `../README.md` - Project root
- `ai-architecture.md` - Complete documentation hierarchy
- `code-standards.md` - Coding standards
- `testing-guide.md` - Testing practices
- `archive/README.md` - Documentation archive

## Version History
- 1.0.1: Clarified archive structure and separation
- 1.0.0: Initial authoritative version
