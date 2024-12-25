# Marian Project Restructuring Plan

## Project Objectives

Marian is an AI-powered email analysis and management system that aims to:
1. Process and analyze email communications using advanced language models
2. Extract meaningful insights and patterns from email content
3. Organize information through an intelligent catalog system
4. Enable natural language interaction for information retrieval
5. Maintain high standards of data privacy and security

## Project Plan Objectives

This restructuring plan aims to:
1. Create a maintainable and scalable project structure
2. Promote code reuse and prevent duplication
3. Establish clear guidelines for contributors and AI assistants
4. Maintain clear separation between domains while enabling integration
5. Ensure comprehensive and accessible documentation
6. Preserve all existing functionality while improving organization

## 1. Project Structure Overview

```
marian/
├── src/                    # Source code
│   ├── core/              # Core shared libraries
│   │   ├── anthropic.py
│   │   ├── gmail.py
│   │   └── database.py
│   ├── libs/              # Domain-specific shared libraries
│   │   ├── analysis/
│   │   ├── chat/
│   │   └── storage/
│   ├── email/             # Email-specific modules
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
docs/
├── getting-started/
│   ├── installation.md      # From SETUP.md
│   └── prerequisites.md
├── guides/
│   ├── librarian-guide.md   # From LIBRARIAN_GUIDE.md
│   ├── workflow.md          # From SESSION_WORKFLOW.md
│   └── troubleshooting.md   # Common issues and solutions
├── architecture/
│   ├── design-decisions.md  # From MARIAN_DESIGN_AND_DECISIONS.md
│   └── database-schema.md
├── development/
│   ├── guidelines.md
│   ├── backlog.md          # Merged from BACKLOG.md and CATALOG_BACKLOG.md
│   ├── code_standards.md   # Coding style and practices
│   └── testing.md         # Testing guidelines and patterns
└── sessions/
    ├── README.md           # Session management guide
    ├── active/            # Current session notes
    └── archive/           # Past session summaries
```

### Documentation Content Organization

#### Getting Started
- Installation prerequisites and steps
- Environment setup
- Initial configuration
- Quick start guide

#### Guides
- Librarian functionality and usage
- Workflow processes and best practices
- Comprehensive troubleshooting guide
  - Common issues and solutions
  - Debugging procedures
  - Environment-specific problems
  - Known limitations

#### Architecture
- System design decisions and rationale
- Database schema and evolution
- Component interactions
- Security considerations

#### Development
- Project guidelines and constraints
- Coding standards and style guide
  - Python style guidelines
  - Documentation requirements
  - Code review checklist
  - PR templates
- Testing framework and practices
  - Test organization
  - Coverage requirements
  - Test patterns
  - Integration test guidelines
- Backlog management
  - Task prioritization
  - Implementation details
  - Dependencies tracking

#### Sessions
- Standardized session management
- Real-time documentation
- Progress tracking
- Historical record keeping

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
    'email_store': DB_DIR / 'email_store.db',
    'email_analysis': DB_DIR / 'email_analysis.db',
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
   │   ├── gmail.py       # Core API integrations
   │   └── database.py    # Database utilities
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

#### Email Domain
```
src/email/
├── core/           # Email-specific core functionality
├── analysis/       # Analysis components
└── reporting/      # Report generation
```

#### Catalog Domain
```
src/catalog/
├── core/           # Catalog-specific core functionality
├── search/         # Search components
└── interactive/    # Interactive features
```

### Documentation Organization
```
docs/
├── getting-started/
│   ├── installation.md      # From SETUP.md
│   └── prerequisites.md
├── guides/
│   ├── librarian-guide.md   # From LIBRARIAN_GUIDE.md
│   └── workflow.md          # From SESSION_WORKFLOW.md
├── architecture/
│   ├── design-decisions.md  # From MARIAN_DESIGN_AND_DECISIONS.md
│   └── database-schema.md
├── development/
│   ├── guidelines.md
│   └── backlog.md          # Merged from BACKLOG.md and CATALOG_BACKLOG.md
└── sessions/               # Session logs and history only
    ├── active/            # Current session notes
    └── archive/           # Past session summaries

# Root-level critical documentation
- AI_SESSION_GUIDE.md      # Primary guide for AI interactions
- README.md                # Project overview
- PROJECT_PLAN.md          # This document
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
