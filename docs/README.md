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

5. **Project Overview**
   - Purpose: High-level project introduction and setup
   - When to use: Starting point for new developers
   - Location: [Project README](../README.md)

## Documentation Index

### Core Documentation
- [AI Architecture](ai-architecture.md) - System architecture and AI components
- [AI Guidelines](ai-guidelines.md) - Guidelines for AI interaction
- [API Mappings](api_mappings.md) - API integration documentation
- [Backlog](backlog.md) - Project backlog and future work
- [Backup Guide](backup.md) - Backup procedures and policies
- [Code Standards](code-standards.md) - Coding standards and practices
- [Contributing Guide](contributing.md) - Contribution guidelines
- [Database Design](database-design.md) - Database schema and design
- [Design Decisions](design-decisions.md) - Key design decisions
- [Development Checklist](dev-checklist.md) - Development workflow checklist
- [Librarian](librarian.md) - Librarian component documentation
- [Project Checklist](project-checklist.md) - Project management checklist
- [Project Plan](project-plan.md) - Project roadmap and planning
- [Session Workflow](session-workflow.md) - AI session workflow guide
- [Setup Guide](setup.md) - Project setup instructions
- [Testing Guide](testing-guide.md) - Testing standards and procedures
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

### Component Documentation
- [Models README](../models/README.md) - Database models documentation
- [Services README](../services/README.md) - Service layer documentation
- [Shared Library README](../shared_lib/README.md) - Shared utilities documentation
- [Tests README](../tests/README.md) - Testing documentation
- [Migrations README](../migrations/README.md) - Database migrations documentation
- [Source README](../src/README.md) - Source code documentation
- [Backup README](../backup/README.md) - Backup procedures

### Architecture Decision Records (ADRs)

Key architectural decisions are documented in ADRs:

 - [ADR 0001: Layered Architecture](adr/0001-layered-architecture.md) - Core architecture decision
 - [ADR 0002: Minimal Security Testing](adr/0002-minimal-security-testing.md) - Security testing approach
 - [ADR 0003: Test Database Strategy](adr/0003-test-database-strategy.md) - Database testing strategy

See the [ADR README](adr/README.md) for more information about our ADR process.

### Session Logs
- [Session Log Index](session_logs/README.md) - Index of AI pair programming sessions
- [2024-12-27 Session](session_logs/2024-12-27.md)
- [2024-12-28 Session](session_logs/2024-12-28_session.md)
- [2024-12-28 Log](session_logs/session_log_2024-12-28.md)
- [Session 20241223_0916](session_logs/session_20241223_0916.md)
- [Session 20241223_0925](session_logs/session_20241223_0925.md)
- [Session 20241223_1148](session_logs/session_20241223_1148.md)
- [Session 20241223_1204](session_logs/session_20241223_1204.md)
- [Session 20241223_1258](session_logs/session_20241223_1258.md)
- [Session 20241223_1413](session_logs/session_20241223_1413.md)
- [Session 20241224_1210](session_logs/session_20241224_1210.md)
- [Session 20241224_1954](session_logs/session_20241224_1954.md)
- [Session 20241224_2042](session_logs/session_20241224_2042.md)
- [Session 20241224_2242](session_logs/session_20241224_2242.md)
- [Session 20241225_0846](session_logs/session_20241225_0846.md)
- [Session 20241225_0922](session_logs/session_20241225_0922.md)
- [Session 20241225_1005](session_logs/session_20241225_1005.md)
- [Session 20241225_1009](session_logs/session_20241225_1009.md)
- [Session 20241225_1236](session_logs/session_20241225_1236.md)
- [Session 20241225_2116](session_logs/session_20241225_2116.md)
- [Session 20241226_1236](session_logs/session_20241226_1236.md)
- [Session 20241226_1414](session_logs/session_20241226_1414.md)
- [Session 20241226_1614](session_logs/session_20241226_1614.md)
- [Session 20241226_1655](session_logs/session_20241226_1655.md)
- [Session 20241226_1823](session_logs/session_20241226_1823.md)
- [Session 20241226_2120](session_logs/session_20241226_2120.md)
- [Session 20241227_0607](session_logs/session_20241227_0607.md)
- [Session 20241227_1231](session_logs/session_20241227_1231.md)
- [Session 20241227_1235](session_logs/session_20241227_1235.md)
- [Session 20241227_1550](session_logs/session_20241227_1550.md)

### Templates
- [Templates Index](templates/README.md) - Documentation templates
- [Archiving Guide](templates/ARCHIVING.md) - File archival procedures
- [Directory README](templates/directory-readme.md) - Template for directory documentation
- [Session Template](templates/session.md) - Template for session logs

### Reminders
- [Storage Check](reminders/20240108_STORAGE_CHECK.md) - Storage usage monitoring

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
