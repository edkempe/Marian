# Documentation Directory

**Version:** 1.0.0  
**Status:** Authoritative

> Central location for all project documentation, including guides, ADRs, and templates.

## Overview
- **Purpose**: Maintain comprehensive project documentation
- **Stability**: Stable
- **Maintenance**: Active
- **Python**: >= 3.12

## Directory Structure
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
│   ├── templates/         # Documentation templates
│   ├── testing-guide.md   # Testing standards and procedures
│   ├── session_logs/      # AI pair programming logs
│   └── README.md          # This file
└── backup/                # Backup files (not for archival)
```

## Core Components
1. **Architecture Decision Records**
   - Purpose: Document key architectural decisions
   - When to use: When making significant design choices
   - Location: `adr/` directory

2. **Document Templates**
   - Purpose: Ensure consistent documentation
   - When to use: When creating new documents
   - Location: `templates/` directory

3. **Documentation Hierarchy**
   - Purpose: Define structure and relationships
   - When to use: Understanding doc organization
   - Example: See `ai-architecture.md`

4. **Documentation Standards**
   - Purpose: Maintain consistency
   - When to use: Creating/updating docs
   - Example: See `code-standards.md`

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

## Related Documentation
- Parent: `../README.md` - Project root
- `ai-architecture.md` - Complete documentation hierarchy
- `code-standards.md` - Coding standards
- `testing-guide.md` - Testing practices
- `archive/README.md` - Documentation archive

## Version History
- 1.0.0 (2024-12-28): Initial documentation structure
  - Defined core documentation types
  - Added templates for consistency
  - Established ADR process
