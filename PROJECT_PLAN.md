# Marian: Jexi's Catalog Management Branch

## Core Development Principles

### Data Model as Single Source of Truth
The SQLAlchemy models in `models/` serve as the authoritative source of truth for all development (see [ADR001](archive/ARCHIVED_20241225_1105_ADR001_SQLAlchemy_Models.md)):

#### Source of Truth Hierarchy
1. **SQLAlchemy Models**: Primary source for schema
   - `models/email.py`: Email and thread schema
   - `models/catalog.py`: Catalog item schema
   - `models/email_analysis.py`: Analysis schema
   
2. **Configuration**: Source for runtime values
   - `constants.py`: Global configuration
   - `catalog_constants.py`: Catalog-specific settings

3. **Migrations**: Schema history
   - Alembic migration scripts
   - Generated from model changes
   - Track schema evolution

All development must:
- Align with SQLAlchemy models
- Use constants.py for configuration
- Track schema changes via migrations
- Keep documentation in sync with models

This principle ensures:
1. Type-safe data handling
2. Consistent schema across codebase
3. Tracked schema evolution
4. Maintainable relationships

### Necessary and Sufficient
Our primary development principle is to maintain only what is necessary and sufficient:
- Every file, folder, and document must justify its existence
- Prefer flatter organization structures over deep hierarchies
- Consolidate related information rather than fragmenting across files
- Remove anything that doesn't directly serve the project's goals
- Minimize navigation complexity by keeping related items together

This principle ensures:
1. Easier information discovery
2. Reduced cognitive load
3. Better maintainability
4. Clear organization
5. Efficient workflows

Examples of applying this principle:
1. **Documentation**: Keep all core documentation in root directory
2. **Backlog Management**: Single BACKLOG.md file instead of multiple workstream files
3. **Configuration**: Centralized constants.py for all settings
4. **Code Organization**: Flat module structure where possible

### Incremental Development
The project follows a strict "one small step at a time" approach:
- Make small, focused changes
- Test and verify each change before proceeding
- Document changes as they are made
- Avoid combining multiple changes in one step
- Get confirmation before proceeding to next step

This principle ensures:
1. Changes are easily reviewable
2. Problems are caught early
3. Documentation stays current
4. Project history remains clear
5. Easier rollback if needed

## Branch Overview
Marian is a branch of the Jexi AI personal assistant project, focused on catalog management and information organization. As Jexi's librarian, Marian aims to:
1. Organize information through an intelligent catalog system
2. Enable natural language interaction for information retrieval
3. Maintain high standards of data privacy and security

## Project Plan Objectives

This restructuring plan aims to:
1. Create a maintainable and scalable branch structure
2. Promote code reuse and prevent duplication with other Jexi branches
3. Establish clear guidelines for contributors and AI assistants
4. Maintain clear separation between branches while enabling integration
5. Ensure comprehensive and accessible documentation
6. Preserve all existing functionality while improving organization

## 1. Project Structure Overview

```
marian/
├── src/                    # Source code
│   ├── core/              # Core shared libraries
│   │   ├── anthropic.py
│   │   ├── database.py
│   └── libs/              # Domain-specific shared libraries
│   │   ├── analysis/
│   │   ├── chat/
│   │   └── storage/
│   ├── catalog/           # Catalog-specific modules
│   └── chat/              # Chat-specific modules
├── data/                  # All data storage
│   ├── db/               # Database files
│   │   ├── primary/      # Main database files
│   │   └── backup/       # Database backups
│   ├── migrations/       # Database migrations
│   └── schema/          # Database schema definitions
├── docs/                 # Documentation
│   ├── getting-started/
│   ├── guides/
│   ├── architecture/
│   ├── development/
│   └── sessions/        # Session management
└── tests/               # Test files organized by module
```

## 2. Documentation Reorganization

### New Documentation Structure
```
/
├── README.md                     # Project overview and quick start
├── LIBRARIAN_GUIDE.md           # Core catalog operations
├── AI_SESSION_GUIDE.md          # AI interaction guidelines
├── SETUP_GUIDE.md               # Environment setup
├── BACKUP_GUIDE.md              # Backup procedures
├── ARCHIVE_GUIDE.md             # Archive standards
├── CODE_STANDARDS.md            # Development standards
├── TESTING_GUIDE.md             # Testing procedures
└── DATABASE_SCHEMA.md           # Data model reference
```

### Documentation Content Organization

#### Core Documentation
- Project overview and quick start (README.md)
  - Installation prerequisites
  - Basic configuration
  - Documentation index
  - Component overview
- Development roadmap (PROJECT_PLAN.md)
  - Project principles
  - Architecture decisions
  - Development standards
- Unified project backlog (BACKLOG.md)
  - Single source of truth for all workstreams
  - Current sprint items
  - Prioritized by workstream
  - Clear dependency tracking
  - Completed items history

#### Process Guides
Located in `/docs`:
- Librarian functionality (LIBRARIAN_GUIDE.md)
  - Core catalog operations
  - Usage guidelines
  - Best practices
- AI session management (AI_SESSION_GUIDE.md)
  - Session protocols
  - AI interaction guidelines
  - Error handling
- Environment setup (SETUP_GUIDE.md)
  - Installation steps
  - Configuration guide
  - Troubleshooting
- Backup procedures (BACKUP_GUIDE.md)
  - Backup strategies
  - Recovery procedures
  - Verification steps
- Archive standards (ARCHIVE_GUIDE.md)
  - Archival policies
  - File organization
  - Retention guidelines

#### Development Standards
Located in `/docs`:
- Code standards (CODE_STANDARDS.md)
  - Python style guidelines
  - Documentation requirements
  - Code review checklist
  - PR templates
- Testing procedures (TESTING_GUIDE.md)
  - Test organization
  - Coverage requirements
  - Test patterns
  - Integration test guidelines
- Database schema (DATABASE_SCHEMA.md)
  - Data model implementation
  - Component interactions
  - Security considerations
- Session workflow (CHAT_START.md, CHAT_CLOSE.md)
  - Starting a session
  - Development guidelines
  - Closing procedures
  - Progress tracking
  - Real-time documentation
  - Task management

#### Session Documentation
Located in `/docs/sessions`:
- One file per development session
- Standardized naming: YYYYMMDD_HHMM.md
- Tracks decisions and progress
- Historical record keeping
  - Session logs
  - Decision records
  - Change history

### Documentation Standards
1. **File Naming**
   - Use UPPERCASE for root-level guides
   - Clear, descriptive names
   - Consistent suffixes (_GUIDE.md, _STANDARDS.md)

2. **Content Structure**
   - Clear table of contents
   - Consistent heading hierarchy
   - Cross-references to related docs
   - Code examples where relevant

3. **Maintenance**
   - Regular reviews
   - Keep content current
   - Archive outdated content
   - Track documentation changes

## 3. Code Organization

### Shared Libraries
- Move external service integrations to `src/core/`
- Domain-specific shared code to `src/libs/`
- Clear import conventions and documentation

### Application Modules
- Group related functionality
- Clear separation of concerns
- Consistent module structure

## 4. Data Management

### Database Organization
- All databases in `data/db/primary/`
- Automated backups in `data/db/backup/`
- Clear separation of data and code
- Organized migrations and schemas

### Configuration Updates
```python
# config/database.py example
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data'
DB_DIR = DATA_DIR / 'db' / 'primary'

DATABASE_PATHS = {
    'catalog': DB_DIR / 'catalog.db',
    'prompts': DB_DIR / 'prompts.db'
}
```

## 5. Session Management

### Single Source of Truth
- Consolidated session management in `docs/sessions/README.md`
- Standardized templates for session start/end
- Organized session history

### Session Documentation
- Real-time session notes in `active/`
- Archived sessions by date
- Consistent format and structure

## 6. Implementation Plan

### Phase 1: Documentation
1. Create new documentation structure
2. Migrate existing docs to new locations
   - Move troubleshooting content to guides
   - Consolidate coding standards
   - Organize testing documentation
3. Update cross-references
4. Archive old documentation files
5. Implement new documentation features:
   - Troubleshooting database
   - Code standards compliance checks
   - Test coverage reporting

### Phase 2: Code Reorganization
1. Create new directory structure
2. Move shared libraries to appropriate locations
3. Reorganize application modules
4. Update import statements

### Phase 3: Data Management
1. Set up new data directory structure
2. Migrate database files
3. Update configuration
4. Implement backup system

### Phase 4: Testing
1. Verify all imports work
2. Run test suite
3. Update CI/CD if needed
4. Document any issues

## 7. Guidelines

### Code Changes
- No functionality removal without approval
- Maintain all existing features
- Keep all tests and documentation
- Preserve error handling and logging

### Documentation
- Keep README.md focused and clear
- Move detailed docs to appropriate sections
- Maintain cross-references
- Update as code changes

### Best Practices
- Clear separation of concerns
- Consistent naming conventions
- Comprehensive documentation
- Regular backups of data

## 8. Next Steps

1. Review and approve plan
2. Create implementation timeline
3. Assign responsibilities
4. Begin with documentation phase
5. Regular progress reviews

## 9. Success Metrics

- All existing functionality preserved
- Improved code organization
- Clearer documentation structure
- Simplified session management
- Robust data organization
- Passing test suite
- No regression issues

## 10. Additional Considerations

### Version Control
```
docs/development/
├── version_control/
│   ├── branching_strategy.md
│   ├── release_process.md
│   └── pr_guidelines.md
```
- Git workflow documentation
- Release versioning guidelines
- PR templates and processes
- Changelog management
- Tag conventions

### Environment Management
```
docs/deployment/
├── environments/
│   ├── development.md
│   ├── staging.md
│   └── production.md
└── configuration/
    ├── env_variables.md
    └── secrets_management.md
```
- Environment setup guides
- Configuration management
- Secrets handling
- Environment validation

### API Documentation
```
docs/api/
├── versions/
│   └── v1/
├── authentication.md
└── guidelines.md
```
- API versioning strategy
- Endpoint documentation
- Schema definitions
- Authentication flows
- Rate limiting

### Monitoring and Security
```
docs/operations/
├── monitoring/
│   ├── logging.md
│   ├── metrics.md
│   └── alerts.md
└── security/
    ├── best_practices.md
    ├── authentication.md
    └── encryption.md
```
- Logging standards
- Monitoring setup
- Security guidelines
- Encryption practices
- Alert management

### Performance and Optimization
```
docs/performance/
├── benchmarks/
├── optimization_guide.md
└── caching_strategy.md
```
- Performance standards
- Optimization guidelines
- Resource management
- Caching policies

### Backup and Recovery
```
docs/operations/
└── disaster_recovery/
    ├── backup_policy.md
    ├── recovery_procedures.md
    └── verification.md
```
- Backup procedures
- Recovery guides
- Data migration
- Verification processes

### Dependency Management
```
docs/development/
└── dependencies/
    ├── update_policy.md
    ├── security_scanning.md
    └── compatibility.md
```
- Update policies
- Security scanning
- Version management
- Compatibility tracking

## 11. Implementation Phases

### Phase 5: Operations Setup
1. Implement monitoring
2. Set up backup systems
3. Configure environments
4. Establish security practices

### Phase 6: Performance Optimization
1. Establish benchmarks
2. Implement monitoring
3. Optimize critical paths
4. Document best practices

### Phase 7: API and Documentation
1. Document API endpoints
2. Set up API versioning
3. Create authentication docs
4. Establish rate limiting

## 12. Maintenance Guidelines

### Regular Reviews
- Monthly security audits
- Quarterly dependency updates
- Performance review cycles
- Documentation freshness checks

### Update Procedures
- Version update process
- Configuration changes
- Security patches
- Documentation updates

### Monitoring and Alerts
- System health checks
- Performance thresholds
- Security monitoring
- Backup verification

## Project Management

#### Workstream Organization
The project is organized into three main workstreams:
1. **Email Processing**: Email retrieval, analysis, and storage
2. **Catalog/Librarian**: Information organization and retrieval
3. **Program Management**: Standards, processes, and coordination across workstreams

#### Program Management Focus
- Development standards and best practices
- Documentation organization and quality
- Cross-workstream coordination
- Process improvement and standardization
- Quality assurance practices
- Technical debt management
- Development workflow optimization

#### Backlog Management
- Single unified backlog in BACKLOG.md
- Organized by workstream for clarity
- Maintains clear priorities across workstreams
- Tracks dependencies between components
- Preserves historical record of completed items

This approach:
- Reduces navigation complexity
- Maintains single source of truth
- Provides clear project overview
- Simplifies priority management
- Facilitates cross-workstream coordination

## 13. Organizational Principles

### Core Development Guidelines

#### Code Reuse First
1. **Before Creating New Code**
   - Search existing codebase using semantic search
   - Review shared libraries in `src/core` and `src/libs`
   - Check utility functions in `utils/`
   - Review related modules for similar functionality

2. **Documentation Review Process**
   - Check existing documentation for solutions
   - Review architectural decisions for context
   - Understand existing patterns and practices
   - Verify no existing solution before creating new

3. **Library Usage**
   - Prefer existing project libraries over new dependencies
   - Use established project utilities
   - Extend existing functionality rather than duplicate
   - Document any gaps in existing libraries

#### Component Organization
1. **Shared Code Placement**
   ```
   src/
   ├── core/              # Fundamental shared libraries
   │   ├── anthropic.py   # External service clients
   │   ├── database.py    # Database utilities
   └── libs/              # Domain-specific shared code
       ├── analysis/      # Analysis utilities
       ├── chat/          # Chat functionality
       └── storage/       # Storage utilities
   ```

2. **When to Create New Components**
   - Functionality needed across multiple domains
   - Clear separation from existing components
   - Well-defined interface and purpose
   - No suitable existing component

3. **Component Documentation**
   - Clear usage examples
   - API documentation
   - Integration guidelines
   - Dependency information

### Guidelines for Contributors

#### Before Making Changes
1. **Research Phase**
   - Review project documentation
   - Search existing codebase
   - Check shared libraries
   - Understand domain separation

2. **Planning Phase**
   - Identify reuse opportunities
   - Document intended changes
   - Review with maintainers
   - Consider impact on existing code

3. **Implementation Phase**
   - Use existing patterns
   - Follow code standards
   - Update documentation
   - Add tests for new code

#### For AI Assistants/Co-pilots
1. **Code Search Protocol**
   - Use semantic search first
   - Check related files
   - Review shared utilities
   - Examine test files for examples

2. **Documentation Protocol**
   - Review all relevant docs
   - Check architectural decisions
   - Understand domain boundaries
   - Follow existing patterns

3. **Implementation Protocol**
   - Prioritize code reuse
   - Maintain domain separation
   - Follow project structure
   - Document decisions

### Domain Organization

#### Catalog Domain
```
src/catalog/
├── core/           # Catalog-specific core functionality
├── search/         # Search components
└── interactive/    # Interactive features
```

### Documentation Organization
```
/
├── README.md                     # Project overview and quick start
├── LIBRARIAN_GUIDE.md           # Core catalog operations
├── AI_SESSION_GUIDE.md          # AI interaction guidelines
├── SETUP_GUIDE.md               # Environment setup
├── BACKUP_GUIDE.md              # Backup procedures
├── ARCHIVE_GUIDE.md             # Archive standards
├── CODE_STANDARDS.md            # Development standards
├── TESTING_GUIDE.md             # Testing procedures
└── DATABASE_SCHEMA.md           # Data model reference
```

### Documentation Priorities
1. **Root Level**
   - Critical process documents
   - Main entry points
   - AI interaction guidelines

2. **Docs Directory**
   - Detailed documentation
   - Technical guides
   - Historical records

3. **Session Management**
   - AI_SESSION_GUIDE.md as primary reference
   - Session logs in docs/sessions/
   - Clear templates and procedures

### Reuse Checklist

#### Before Creating New Code
- [ ] Searched codebase for similar functionality
- [ ] Reviewed shared libraries
- [ ] Checked utility functions
- [ ] Examined related modules
- [ ] Documented why new code is needed

#### Before Adding Dependencies
- [ ] Verified no existing solution
- [ ] Checked shared libraries
- [ ] Reviewed current dependencies
- [ ] Documented necessity

#### When Extending Functionality
- [ ] Identified relevant existing code
- [ ] Understood current patterns
- [ ] Documented integration points
- [ ] Updated related documentation

### Maintenance Guidelines

1. **Regular Reviews**
   - Identify duplicate code
   - Consolidate similar functionality
   - Update documentation
   - Maintain component registry

2. **Documentation Updates**
   - Keep examples current
   - Update usage guidelines
   - Document new patterns
   - Maintain reuse guides

3. **Component Registry**
   - Track shared components
   - Document capabilities
   - Monitor usage patterns
   - Identify consolidation opportunities
