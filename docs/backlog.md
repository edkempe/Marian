# Marian Development Backlog

**Version:** 1.0.0
**Status:** Source of truth for project tasks and priorities
**Note:** Prototype and experimental features have been moved to [backlog_prototypes.md](./backlog_prototypes.md)

## High Priority

### Security and Authentication
1. [ ] **Implement ADR-0008: Secure Token Storage**
   - Status: Backlog
   - Priority: Medium
   - Description: Migrate token storage from pickle to JSON format with keyring-based encryption. Implement token rotation, secure deletion, and system keychain integration.
   - Dependencies: None
   - ADR: [ADR-0008](adr/0008-secure-token-storage.md)

### Code Organization
1. [ ] **Implement ADR-0009: Constants Consolidation**
   - Status: Proposed
   - Priority: High
   - Description: Consolidate constants into a hierarchical structure under shared_lib/constants/. Create clear separation between configuration and constants.
   - Dependencies: None
   - ADR: [ADR-0009](adr/0009-constants-consolidation.md)

### Documentation and Standards
1. [ ] Update component-specific README files
   - Status: Not Started
   - Priority: High
   - Description: Each component directory needs a unique README that describes its specific purpose and contents
   - Dependencies: None
   - Estimated Time: 1-2 sessions

2. [ ] Create ADR Index and Hierarchy
   - Status: Not Started
   - Priority: High
   - Description: Create a comprehensive index of all ADRs with clear categorization and relationships
   - Key Areas:
     - Create `adr_index.md` with categorized listing
     - Document ADR relationships and dependencies
     - Add status tracking for each ADR
     - Create visualization of ADR hierarchy
   - Dependencies: None
   - Estimated Time: 1 session
   - Notes: Will help track architectural decisions and their impacts

3. [ ] Fix failing tests and dependencies
   - Status: Not Started
   - Priority: High
   - Description: Resolve missing dependencies (bs4, networkx, pkg_resources) and DEFAULT_MODEL import issues
   - Dependencies: None
   - Estimated Time: 1 session

4. [ ] Clean up Python package metadata
   - Status: Not Started
   - Priority: High
   - Description: Resolve duplicate egg-info directories and ensure proper package structure
   - Dependencies: None
   - Estimated Time: 1 session

5. [ ] Set up proper test data module
   - Status: Not Started
   - Priority: High
   - Description: Create dedicated test data module with versioned test files, fix test_data package structure, and set up semantic_test_data module
   - Dependencies: None
   - Estimated Time: 1-2 sessions
   - Subtasks:
     - [ ] Add version tracking for test files
     - [ ] Create test data documentation

6. [ ] Regular Documentation Consistency Check
   - Status: Not Started
   - Priority: High
   - Description: Set up recurring task to validate documentation consistency
   - Dependencies: None
   - Estimated Time: Recurring (Weekly)
   - Subtasks:
     - [ ] Run test_doc_hierarchy.py to validate documentation structure
     - [ ] Check for content inconsistencies between related documents
     - [ ] Verify cross-references are valid and up-to-date
     - [ ] Review HTML reports in reports/testing/
     - [ ] Update documentation if issues found
   - Success Criteria:
     - All documentation tests pass
     - No content inconsistencies found
     - Cross-references are valid
     - HTML reports show no warnings

7. [ ] Standardize Path and File Operations
   - Status: Not Started
   - Priority: High
   - Description: Refactor codebase to use consistent path and file operation libraries
   - Dependencies: None
   - Estimated Time: 2-3 sessions
   - Subtasks:
     - [ ] Audit current usage of os.path, open(), and file operations
     - [ ] Convert file path operations to pathlib.Path
     - [ ] Convert file operations to use shutil where appropriate
     - [ ] Update documentation to reflect standardized approach
     - [ ] Add utility functions for common file operations
   - Files Needing Updates:
     - app_email_self_log.py: file writing
     - asset_catalog_service.py: path normalization
     - scripts/init_db.py: path handling
     - scripts/generate_report.py: file operations
     - scripts/populate_asset_catalog.py: file operations
     - tests/: multiple test files with file operations
   - Success Criteria:
     - All file paths use pathlib.Path
     - File operations use appropriate shutil functions
     - Consistent error handling across file operations
     - Updated documentation reflecting best practices
     - All tests pass with new implementations

8. [ ] Review and optimize development tool usage
   - Status: Not Started
   - Priority: Medium
   - Description: Comprehensive review of development tools (Pylint, Marshmallow, etc.) to ensure optimal usage and configuration
   - Key Areas:
     - Pylint configuration and custom rules
     - Marshmallow schema implementation
     - Test framework organization
     - Code quality metrics
   - Dependencies: None
   - Estimated Time: 2-3 sessions
   - ADR: [ADR-0017](adr/0017-utils-tools-organization.md)

### Schema Validation and Testing
**Status**: In Progress
**Priority**: Highest
**Workstream**: Email Processing
**Description**: Validate and test recent schema changes across the application.

#### Technical Details
1. Database Schema Testing
   - Verify new field names in all operations
   - Test timezone handling
   - Validate label history schema
   - Create database migration plan
   - Test CC/BCC field storage and retrieval
   - Validate migrations with existing data

2. Component Integration
   - Update affected components
   - Test email retrieval with new schema
   - Verify date/time handling
   - Update documentation
   - Test CC/BCC handling in email analysis
   - Verify CC/BCC display in reports

### Email Processing Improvements
**Status**: In Progress
**Priority**: High
**Workstream**: Email Processing
**Description**: Enhance email processing with new fields and validation

#### Technical Details
1. CC/BCC Implementation
   - Test with real Gmail messages
   - Verify storage and retrieval
   - Handle empty fields correctly
   - Update processing logic
   - Add field validation
   - Test edge cases

2. Email Analysis Enhancement
   - Add CC/BCC to priority scoring
   - Include CC/BCC in analysis output
   - Update report formatting
   - Add CC/BCC filtering options
   - Test with various email formats

3. Documentation Updates
   - Document CC/BCC field usage
   - Update schema documentation
   - Add migration guidelines
   - Update API documentation
   - Document testing procedures

### Session Management Testing
**Status**: In Progress
**Priority**: High
**Workstream**: Program Management
**Description**: Ensure robust testing and validation of session management functionality

#### Testing Tasks
- [ ] Test and refine chat session workflow
  - Test session_manager.py functionality
  - Validate start/close procedures
  - Verify documentation updates
  - Test environment checks
  - Add any missing checks or features
  - Document best practices learned

#### Improvements Needed
- [ ] Fix python command handling in chat_session_manager.py
  - Handle both 'python' and 'python3' commands
  - Add fallback mechanism
  - Document required Python version

- [ ] Improve test execution and reporting
  - Add proper error handling for missing test directory
  - Show test coverage when available
  - Report specific test failures

- [ ] Enhance BACKLOG.md parsing
  - Better task extraction
  - Priority level awareness
  - Task status tracking

- [ ] Add environment section to session reports
  - Python version
  - Key package versions
  - Database status
  - API configurations

### Session Management
**Status**: In Progress
**Priority**: High
**Workstream**: Program Management
**Description**: Implement standardized session workflow and documentation

#### Implementation Tasks
- [ ] Update chat_session_manager.py for new workflow
  - [ ] Create session summaries in docs/sessions/
  - [ ] Use standardized file naming (session_YYYYMMDD_HHMM.md)
  - [ ] Include timezone in timestamps
  - [ ] Implement session summary template
  - [ ] Add session file cleanup/archival

#### Validation Tasks
- [ ] Add session summary validation
  - [ ] Check required sections
  - [ ] Validate timestamps
  - [ ] Verify file location

#### Documentation Tasks
- [ ] Improve session documentation
  - [ ] Update workflow documentation
  - [ ] Add file naming conventions
  - [ ] Document archival process

### Database Documentation and Schema
**Status**: In Progress
**Priority**: High
**Workstream**: Program Management
**Description**: Comprehensive database documentation and schema improvements

#### Technical Details
1. Documentation Improvements
   - [ ] Move schema documentation from models to docs/database_design.md
   - [ ] Create ERD diagram
   - [ ] Document validation rules
   - [ ] Add migration guide
   - [ ] Document test data management

2. Schema Improvements
   - [ ] Migrate TEXT fields to JSON type
     - Change analysis fields from TEXT to JSON
     - Add data migration script
     - Add JSON validation
     - Update tests
   - [ ] Standardize date handling
     - Review action_deadline field type
     - Change Email model date fields to DateTime(timezone=True)
     - Create consistent date handling strategy

3. Schema Optimization
   - [ ] Add indexes for common queries
   - [ ] Consider partitioning by date
   - [ ] Measure and optimize performance

#### Success Criteria
- Complete and accurate documentation
- Consistent schema design
- Proper data type usage
- Optimized performance

### Setup Script Creation
**Status**: Planned
**Priority**: High
**Workstream**: Program Management
**Description**: Create a comprehensive setup script to automate environment, credentials, and database initialization.

#### Technical Details
1. Environment Setup
   - Create virtual environment
   - Install required packages from requirements.txt
   - Set up environment variables

2. Credentials Management
   - Set up secure credential storage
   - Configure Gmail API credentials
   - Configure Anthropic API key
   - Add template .env file

3. Database Initialization
   - Create SQLite databases if not exist
   - Initialize database schemas
   - Add sample data for testing
   - Create backup/restore utilities

#### Implementation Steps
1. Create setup.py script
2. Add environment validation
3. Add credential configuration
4. Add database initialization
5. Add setup verification tests
6. Create documentation

### Database Session Management Refactor
**Status**: Planned
**Priority**: High
**Workstream**: Program Management
**Description**: Implement a scalable database session management system to handle multiple databases efficiently.

#### Technical Details
1. Create `DatabaseSessions` class in `database/config.py`
   - Lazy session factory initialization
   - Context managers for single and multiple sessions
   - Centralized configuration management

#### Benefits
- More scalable as we add new databases
- Consistent session management across codebase
- Better resource management
- Easier to maintain and extend

#### Implementation Steps
1. Create new configuration system
2. Implement `DatabaseSessions` class
3. Update existing code to use new system
4. Add tests for session management
5. Document usage patterns

#### Code Example
```python
class DatabaseSessions:
    def __init__(self):
        self._sessions = {}

    @contextmanager
    def get_session(self, db_name: str):
        # Get single database session
        pass

    @contextmanager
    def with_sessions(self, *db_names: str):
        # Get multiple database sessions
        pass
```

#### Migration Strategy
1. Create new system alongside existing code
2. Gradually migrate one file at a time
3. Run both systems in parallel during transition
4. Remove old system once migration is complete

### Database Code Consolidation
**Status**: In Progress
**Priority**: High
**Workstream**: Program Management
**Description**: Complete the consolidation of database-related code and update imports.

#### Technical Details
1. Update Remaining Import References
   - app_get_mail.py
   - app_email_analyzer.py
   - analysis_viewer.py
   - utils/util_db_init.py
   - utils/util_schema_verify.py
   - utils/util_test_data.py
   - tests/test_email_analysis.py
   - app_email_reports.py

2. Archive Old Files
   - Create backup/20241225 directory
   - Move utils/database.py to backup
   - Move database/config.py to backup
   - Remove empty directories if applicable

3. Test Database Functionality
   - Verify all database operations still work
   - Run the test suite
   - Test database initialization
   - Test session management

**Session Reference**: 2024-12-25-09-34

### Constants Consolidation
**Status**: Planned
**Priority**: High
**Workstream**: Program Management
**Description**: Consolidate all constants files into a single source of truth.

#### Technical Details
1. Review and Compare Constants
   - config/constants.py
   - constants.py
   - catalog_constants.py
   - Any other constant definitions

2. Plan Consolidation
   - Identify overlapping constants
   - Create unified constant structure
   - Document any branch-specific constants

3. Implement Changes
   - Create consolidated constants file
   - Update all imports
   - Archive old constant files
   - Test all functionality

**Session Reference**: 2024-12-25-09-34

### Code DRY (Don't Repeat Yourself) Review
**Status**: Planned
**Priority**: High
**Workstream**: Program Management
**Description**: Review and refactor code to eliminate duplication and improve maintainability, following our necessary and sufficient principle.

#### Areas to Review
1. Email Analysis Logic
   - Check for duplicate analysis code between files
   - Consolidate common email processing functions
   - Create shared utilities for email data transformation

2. Database Queries
   - Look for repeated query patterns
   - Create reusable query builders
   - Consolidate similar database operations

3. Report Generation
   - Review duplicate report formatting code
   - Create shared report templates
   - Consolidate common data aggregation logic

#### Implementation Steps
1. Audit codebase for duplicated logic
2. Identify common patterns and functionality
3. Create shared utilities and helper functions
4. Refactor code to use shared components
5. Add tests for shared functionality

#### Benefits
- Easier maintenance
- Reduced bug surface area
- More consistent behavior
- Better code reusability

### Model Improvements

#### Email Analysis Model
- [ ] Improve type safety and documentation
  - Add specific type hints for JSON columns
  - Make nullable status explicit
  - Document type constraints and validation rules
  - Priority: Low

- [ ] Standardize date handling
  - Review action_deadline field type (DateTime vs String from API)
  - Change Email model date field from TEXT to DateTime(timezone=True)
  - Create consistent date handling strategy
  - Priority: Low

- [ ] Future JSON Type Migration
  - Plan migration of TEXT fields to JSON type
  - Create data migration script
  - Add validation for JSON format
  - Update tests
  - Priority: Low - after validation improvements

#### Schema Management
- [ ] Implement model-first approach
  - Use models as single source of truth
  - Generate schema migrations from models using Alembic autogenerate
  - Priority: Medium

### Domain Constants Refinement
1. Move email analysis validation constants to domain_constants.py:
   ```python
   ANALYSIS_VALIDATION = {
       'PRIORITY_SCORE': {'MIN': 1, 'MAX': 5},
       'TEXT_LENGTH': {'MIN': 1, 'MAX': 10000},
       'CONFIDENCE_SCORE': {'MIN': 0.0, 'MAX': 1.0}
   }
   ```
   - Rationale: Consolidate domain rules in a single location
   - Impact: Improves maintainability and consistency
   - Dependencies: None
   - Priority: Medium

2. Move sentiment types to domain constants:
   ```python
   ANALYSIS_SENTIMENT_TYPES = {
       'POSITIVE': 'positive',
       'NEGATIVE': 'negative',
       'NEUTRAL': 'neutral'
   }
   ```
   - Rationale: Centralize all domain enums
   - Impact: Better type safety and validation
   - Dependencies: None
   - Priority: Medium

3. Add relationship validation in AssetDependency model:
   ```python
   @validates('relation_type')
   def validate_relation_type(self, key, value):
       # Validate relationship types based on source and target asset types
       # using RELATIONSHIP_RULES from domain_constants
   ```
   - Rationale: Enforce relationship rules at the model level
   - Impact: Prevents invalid relationships between assets
   - Dependencies: None
   - Priority: High

### Database
- [x] Fix ID type mismatch (Completed 2024-12-23)
  - Changed to TEXT type for email_id and thread_id
  - Added validation in models and handlers
  - Updated test data to use realistic Gmail IDs

- [ ] Database Documentation Improvements
  - Move schema documentation from models to docs/database_design.md
  - Add ERD diagram
  - Document validation rules
  - Add migration guide
  - Priority: High

- [ ] Add Database Validation Tests
  - Test ID validation
  - Test foreign key constraints
  - Test data type constraints
  - Priority: Medium

### Database Improvements
- [ ] Migrate TEXT fields to JSON type
  - Change analysis fields from TEXT to JSON type
  - Fields to update:
    - category
    - action_type
    - key_points
    - people_mentioned
    - links_found
    - links_display
    - full_api_response
  - Add data migration script
  - Add validation for JSON format
  - Update tests
  - Priority: Low

### Database Cleanup
- [ ] Legacy Component Cleanup
  - Remove email_triage table
  - Archive old analysis database
  - Update documentation
  - Priority: Low

- [ ] Batch Processing Implementation
  - Track batch_id and processing_status
  - Handle retries and error states
  - Migrate from email_triage approach
  - Priority: Medium

- [ ] Schema Optimization
  - Add indexes for common queries
  - Consider partitioning by date
  - Measure and optimize performance
  - Priority: Low

### Testing Infrastructure
- [ ] Fix failing tests after schema changes
  - [ ] Update test database setup
  - [ ] Fix column name mismatches
  - [ ] Update mock data and API responses

- [ ] Improve test data management
  - [ ] Create reusable test fixtures
  - [ ] Add database setup helpers
  - [ ] Improve test isolation
- [ ] Add integration tests for email processing workflow
- [ ] Add performance tests for database operations

### Documentation
- [ ] Document new database schema
- [ ] Update API documentation
- [ ] Add migration guide for schema changes
- [ ] Document test data management
- [ ] Make documentation DRY
  - Review all documentation for redundancy
  - Move common information to central location
  - Update references to point to central docs
  - Priority: High

### Code Quality
- [ ] Improve Gmail API Data Validation
  - Add GmailMessageValidator for API responses
  - Add GmailHeaderValidator for message headers
  - Add type validation for all fields
  - Add size limits and content validation
  - Add proper error handling and logging
  - Update lib_gmail.py to use validators
  - Add tests for validation
  - Priority: High

### Implement 3-2-1 Backup Strategy
**Status**: Planned
**Priority**: Medium-High
**Workstream**: Program Management
**Description**: Implement comprehensive 3-2-1 backup strategy for critical data, complementing GitHub code backup.

#### Technical Details
1. Local Backups (Copy 1)
   - Implement daily local snapshots
   - Set up rotation policy
   - Monitor storage usage
   - Automate cleanup

2. External Drive Backups (Copy 2)
   - Define external backup procedure
   - Implement verification
   - Document recovery steps
   - Set up notifications

3. Cloud Backups (Copy 3 - Offsite)
   - Select cloud provider
   - Implement secure transfer
   - Set up encryption
   - Monitor costs

4. Automation
   - Create backup scripts
   - Set up scheduling
   - Implement monitoring
   - Add error reporting

5. Documentation
   - Update BACKUP_GUIDE.md
   - Create recovery playbook
   - Document verification steps
   - Add troubleshooting guide

#### Success Criteria
- 3 copies of all critical data
- 2 different storage types
- 1 offsite copy
- Automated verification
- Documented recovery process

#### Dependencies
- Storage requirements analysis
- Cloud provider selection
- Security review
- Cost assessment

#### Notes
- GitHub handles code backup
- Focus on database and config files
- Consider privacy requirements
- Monitor storage costs

### Check Backup Storage Requirements (2024-01-05)
**Status**: Planned
**Priority**: High
**Workstream**: Program Management
**Description**: Analyze storage requirements for 30-day backup retention policy.

#### Technical Details
1. Storage Analysis
   - Measure current daily backup size
   - Project 30-day requirements
   - Include database growth estimates
   - Account for WAL files

2. Impact Assessment
   - Calculate total storage needs
   - Evaluate compression options
   - Consider cleanup automation
   - Review retention policy

3. Recommendations
   - Storage capacity planning
   - Compression strategy
   - Cleanup automation
   - Policy adjustments if needed

#### Success Criteria
- Clear storage requirements
- Compression recommendations
- Automated cleanup plan
- Sustainable retention policy

#### Dependencies
- 30 days of backup data
- Database growth metrics
- Storage monitoring tools

#### Notes
- Check Jan 5, 2024
- Consider both local and offsite storage
- Include all database files (*.db, *.db-wal, *.db-shm)
- Factor in pre-change backups

### Catalog System
The Catalog system is a dedicated sub-domain for managing and organizing information through interactive chat.

### Catalog System Core Components
**Status**: In Progress
**Priority**: High
**Workstream**: Catalog/Librarian
**Description**: Implement core catalog system functionality

#### Technical Details
1. Interactive Chat System
- [x] Basic chat loop structure
- [ ] Claude AI integration for natural language processing
- [ ] Command parsing and routing
- [ ] Interactive and CLI modes
- [ ] Chat history logging
- [ ] Context management between chat sessions

2. Database Infrastructure
- [ ] Catalog table for storing information items
- [ ] Tags system for categorization
- [ ] Relationships between items
- [ ] Version history tracking
- [ ] Search indexing
- [ ] Integration with email database

3. Information Management
- [ ] Add new items to catalog
- [ ] Update existing items
- [ ] Delete items (with soft delete option)
- [ ] Tag management
- [ ] Bulk operations
- [ ] Import/export functionality

4. Search and Retrieval
- [ ] Full-text search
- [ ] Tag-based filtering
- [ ] Semantic search using embeddings
- [ ] Related items discovery
- [ ] Search result ranking
- [ ] Query suggestions

5. Integration Features
- [ ] Email-to-catalog conversion
- [ ] Link with email analysis results
- [ ] Extract entities from emails
- [ ] Connect related information across sources
- [ ] Export to various formats

#### Success Criteria
- All core components implemented and tested
- Integration with email system working
- Search functionality performing well
- User-friendly interaction model
- Proper error handling and logging

#### Dependencies
- Email system integration points
- Database schema finalization
- AI model selection and integration
- Search infrastructure setup

### Catalog Implementation Phases
**Status**: In Progress
**Priority**: High
**Workstream**: Catalog/Librarian
**Description**: Phased implementation plan for catalog system

#### Phase 1: Foundation (Current)
- [x] Set up project structure
- [x] Design database schema
- [ ] Implement basic chat interface
- [ ] Create logging system
- [ ] Add basic CRUD operations

#### Phase 2: Core Features
- [ ] Implement tag system
- [ ] Add search functionality
- [ ] Create item relationships
- [ ] Develop CLI commands
- [ ] Add bulk operations

#### Phase 3: AI Integration
- [ ] Integrate Claude for chat
- [ ] Add semantic search
- [ ] Implement auto-tagging
- [ ] Add context awareness
- [ ] Create smart suggestions

#### Phase 4: Email Integration
- [ ] Link with email database
- [ ] Convert emails to catalog items
- [ ] Extract entities from emails
- [ ] Create relationship mapping
- [ ] Implement cross-referencing

#### Phase 5: Advanced Features
- [ ] Add version history
- [ ] Implement export formats
- [ ] Create visualization tools
- [ ] Add batch processing
- [ ] Implement advanced search

#### Technical Requirements

1. Configuration
- [x] Separate catalog constants from main project
- [x] Define semantic analysis parameters
- [x] Configure database settings
- [x] Set up error message templates
- [ ] Add configuration validation
- [ ] Support environment overrides

2. Database
- Use existing SQLite infrastructure
- Add new tables for catalog items
- Maintain referential integrity
- Support full-text search
- Handle concurrent access

3. API Design
- RESTful interface for CLI
- Websocket for interactive chat
- Structured response format
- Error handling
- Rate limiting

4. Security
- Input validation
- Data sanitization
- Access control
- Secure storage
- Audit logging

5. Testing Strategy
- Unit tests for core functions
- Integration tests for database
- End-to-end chat tests
- Performance benchmarks
- Security testing

6. Documentation
- API documentation
- User guides
- Development setup
- Configuration
- Best practices

#### Future Enhancements
- Web interface
- Mobile app integration
- Real-time collaboration
- Machine learning models
- External API integrations

#### Dependencies
- Existing email processing system
- Claude API
- SQLite database
- Python standard library
- Testing framework

### Catalog System Timestamp Migration (Year 2038)
**Status**: Planned
**Priority**: High
**Workstream**: Catalog/Librarian
**Description**: Address the Year 2038 problem for timestamp storage in catalog system

#### Technical Details
1. Timestamp Storage Assessment
   - Evaluate current INTEGER storage on target systems (32-bit vs 64-bit)
   - Plan migration strategy to 64-bit timestamps if needed
   - Add tests to verify date handling beyond 2038
   - Document timestamp handling approach

2. Implementation Plan
   - Design schema migration strategy
   - Create database migration scripts
   - Update application code for new timestamp format
   - Add conversion utilities for existing data

3. Testing & Validation
   - Add edge case tests for timestamp handling
   - Test date operations beyond 2038
   - Verify data integrity after migration
   - Performance testing with new format

### Catalog System Performance Optimization
**Status**: Planned
**Priority**: Medium
**Workstream**: Catalog/Librarian
**Description**: Optimize performance for soft-deleted items and archival operations

#### Technical Details
1. Query Optimization
   - Index planning for soft-deleted queries
   - Evaluate query performance with large datasets
   - Consider partitioning strategy for archived items
   - Optimize tag relationship queries

2. Data Management
   - Implement archival strategy for old soft-deleted items
   - Add bulk restore functionality
   - Add date-based cleanup for very old soft-deleted items
   - Optimize storage for archived data

3. Feature Enhancements
   - Add date range filtering for archived items
   - Implement audit log for soft delete/restore operations
   - Add batch operations for soft delete/restore
   - Enhance restoration of items with complex tag relationships

4. Documentation
   - Add timestamp handling guide for developers
   - Document query patterns for soft-deleted items
   - Create maintenance guide for archived data
   - Update schema documentation

### Catalog System Fixes
**Status**: Planned
**Priority**: High
**Workstream**: Catalog/Librarian
**Description**: Fix critical issues identified in catalog system testing.

#### Technical Details
1. Anthropic API Integration
   - Debug NoneType error in API response handling
   - Implement proper error handling for API calls
   - Add retry logic for failed API calls
   - Add logging for API interactions

2. Archived Item Handling
   - Review and fix exception handling logic
   - Implement proper validation for archived items
   - Add test cases for edge cases
   - Update documentation

3. Semantic Matching
   - Debug semantic similarity detection
   - Improve matching algorithm
   - Add test cases with varied content
   - Document matching criteria

**Session Reference**: 2024-12-25-08-46

### Project Structure Simplification
**Status**: Planned
**Priority**: High
**Workstream**: Program Management
**Description**: Implement "necessary and sufficient" principle across project structure.

#### Technical Details
1. Documentation Consolidation
   - Review all documentation files for overlap
   - Identify core information that must be preserved
   - Create plan for consolidating into fewer files
   - Ensure no context or important information is lost

2. Directory Structure Flattening
   - Audit current directory structure
   - Identify opportunities to reduce hierarchy
   - Plan migration to flatter structure
   - Update all affected file paths

3. Jexi Branch Organization
   - Document branch relationship (Marian as Jexi branch)
   - Establish clear boundaries between branches
   - Define shared vs. branch-specific components
   - Create guidelines for when to branch vs. share code

**Session Reference**: 2024-12-25-08-57

## Documentation Review Tasks
**Status**: New
**Priority**: High
**Workstream**: Program Management
**Description**: Review and improve documentation for clarity, accuracy, and completeness.

#### Tasks
- [ ] Review archived testing guides
  - Review ARCHIVED_20241227_1514_testing-guide.jexi.bak
  - Review ARCHIVED_20241227_1512_testing-guide.md
  - Compare with current testing-guide.md
  - Identify any valuable content not carried forward
  - Update current guide if needed
  - Context: Ensure no critical testing information was lost during guide updates
  - Priority: Medium
  - Dependencies: None
- [ ] Review Data Storage and Schema section for potential consolidation
  - Context: Follow-up from documentation cleanup
  - Consider merging implementation details with storage considerations
- [ ] Add implementation examples for key features
  - Context: Make documentation more practical
  - Include code snippets for common operations
- [ ] Review other documentation files for duplicate sections
  - Context: Continue documentation cleanup effort
  - Apply same principles used in MARIAN_DESIGN_AND_DECISIONS.md
- [ ] Implement documentation directory structure reorganization
  - Create new documentation sections:
    - `/docs/guides/` for detailed how-to guides
    - `/docs/reference/` for reference documentation
    - `/docs/decisions/` for Architecture Decision Records (ADRs)
  - Move existing files to appropriate sections
  - Update all cross-references and links
  - Verify documentation navigation remains intuitive
  - Priority: Low
  - Dependencies: None
  - Context: Final phase of documentation standardization project

## Medium Priority


### Process Improvements
**Status**: Planned
**Priority**: Medium
**Workstream**: Program Management
**Description**: Improve development workflow processes

#### Session Types Classification
Consider implementing different session types to optimize the development workflow:

1. **Full Sessions**
   - Major code changes
   - Database changes
   - New features
   - Complex refactoring

2. **Light Sessions**
   - Documentation updates
   - Minor bug fixes
   - Simple refactoring
   - Configuration changes

3. **Emergency Sessions**
   - Critical bug fixes
   - Security patches
   - Production issues

Benefits:
- More efficient use of development time
- Clearer expectations for each type of change
- Better handling of urgent issues

**Session Reference**: 2024-12-25-09-51

### Documentation Updates
**Status**: Pending
**Priority**: Medium
**Workstream**: Program Management
**Description**: Update documentation to reflect recent schema changes.

#### Areas to Update
1. API Documentation
   - Document new field names
   - Update examples
   - Add timezone handling guidelines

2. Database Schema
   - Document new schema
   - Add migration guidelines
   - Update field descriptions

### Process Automation
**Status**: New
**Priority**: Medium
**Workstream**: Program Management
**Description**: Automate routine development and documentation tasks

#### Documentation Automation
- [ ] Create automated documentation checks
  - [ ] Link validation
  - [ ] Format consistency
  - [ ] File naming conventions
  - [ ] Cross-reference verification

#### Session Management Automation
- [ ] Implement session tools
  - [ ] Session creation automation
  - [ ] Backlog item extraction
  - [ ] Action item tracking
  - [ ] Session summary generation

#### Metrics and Reporting
- [ ] Add development metrics tracking
  - [ ] Session productivity metrics
  - [ ] Documentation health metrics
  - [ ] Backlog progress tracking
  - [ ] Test coverage trends

### Semantic Search Improvements

#### 1. Improve Semantic Ranking for Advanced vs Basic Content
**Priority**: High
**Complexity**: Medium
**Impact**: Better search results for tutorial/guide content
**Tag**: semantic-ranking

**Problem**:
Current semantic search doesn't reliably rank advanced content higher than basic content for the same topic.

**Example**:
- Query: "python class tutorial"
- Expected: "Python OOP Guide" should rank higher than "Python Beginner's Class"

**Attempted Solution**:
- Used prompt engineering to guide Claude's scoring
- Added explicit scoring guidelines in the prompt
- Added examples of expected ranking

**Key Learnings**:
1. Simple prompt engineering isn't sufficient for reliable ranking
2. Need explicit content level metadata
3. May need separate scoring logic for tutorials/guides

**Next Steps**:
1. Add content level metadata to `CatalogItem` (e.g., "beginner", "advanced")
2. Implement separate scoring logic for tutorial content
3. Consider weighted scoring combining semantic and metadata factors

#### 2. Improve Short-form Content Matching
**Priority**: Medium
**Complexity**: Low
**Impact**: Better handling of abbreviations and compound concepts
**Tag**: semantic-short-form

**Problem**:
Short-form matching isn't reliably handling compound concepts and technical abbreviations.

**Example**:
- Query: "web api endpoints" should match item with title "api"
- Current behavior: No match found

**Potential Solutions**:
1. Add special handling for common technical abbreviations
2. Maintain a mapping of compound concepts to their components
3. Consider token-based matching for short queries

**Next Steps**:
1. Create a mapping of common technical abbreviations and their expansions
2. Implement token-based matching for compound queries
3. Add test cases for common technical abbreviations

### Prompt Version Tracking
**Status**: Backlogged
**Priority**: Low
**Workstream**: Email Processing
**Description**: System for tracking and managing different versions of prompts used in email analysis.

#### Technical Details
- Track which prompt version was used for each email analysis
- Enable comparison of analysis results between prompt versions
- Support A/B testing of prompt improvements

#### Implementation Notes
- Initial prototype used mock testing (now archived)
- Related archived files:
  - `archive/ARCHIVED_20241226_1716_test_version_tracking.py`
  - `archive/ARCHIVED_20241226_1712_test_util.py`
  - `archive/ARCHIVED_20241225_1807_broken_test_util.py`

#### Dependencies
- Database schema changes
- UI modifications for version management
- Testing infrastructure for prompt comparison

#### Action Items
- [ ] Design prompt versioning schema
- [ ] Implement version management system
- [ ] Create UI for managing prompt versions
- [ ] Add metrics for version comparison
- [ ] Build A/B testing framework

{{ ... }}

## Version History
- 1.0.0: Initial backlog covering Email Processing, Catalog/Librarian, and Program Management workstreams

## Documentation Tasks

### Session Log Format Migration
**Priority**: Medium
**Status**: Not Started
**Added**: 2024-12-28

#### Description
Create script to migrate existing session logs to new format (`session_log_YYYY-MM-DD.md`) and update all related documentation and scripts.

#### Requirements
1. Create migration script to:
   - Rename existing files to new format
   - Merge multiple sessions from same day
   - Preserve all content and timestamps
2. Update documentation:
   - README.md
   - dev-checklist.md
   - SESSION_TEMPLATE.md
   - Any other references
3. Update scripts:
   - chat_session_manager.py
   - Any other related scripts
4. Test all changes thoroughly

#### Acceptance Criteria
- [ ] All session logs follow new naming convention
- [ ] Multiple sessions per day are properly merged
- [ ] All documentation consistently references new format
- [ ] chat_session_manager.py works with new format
- [ ] No broken links or references

#### Notes
- Current format is inconsistent (mix of timestamps and dates)
- New format will be `session_log_YYYY-MM-DD.md`
- Multiple sessions in a day will be separated by timestamps
- Need to handle existing 2024-12-27.md format file

### Testing
1. Add schema validation tests:
   ```python
   def test_schema_matches_migrations():
       """Ensure SQLAlchemy models match migration schema."""
       # Create DB from migrations
       migration_engine = create_engine('sqlite:///:memory:')
       with migration_engine.connect() as conn:
           for statement in latest_migration.upgrade():
               conn.execute(statement)

       # Create DB from models
       model_engine = create_engine('sqlite:///:memory:')
       Base.metadata.create_all(model_engine)

       # Compare schemas
       migration_inspector = inspect(migration_engine)
       model_inspector = inspect(model_engine)

       # Compare tables
       assert set(migration_inspector.get_table_names()) == \
              set(model_inspector.get_table_names())

       # Compare columns, constraints, indexes
       for table in migration_inspector.get_table_names():
           migration_cols = {c['name']: c for c in
                           migration_inspector.get_columns(table)}
           model_cols = {c['name']: c for c in
                        model_inspector.get_columns(table)}
           assert migration_cols == model_cols
   ```
   - Rationale: Catch model-migration mismatches early
   - Impact: Prevents schema drift and deployment issues
   - Dependencies: None
   - Priority: High

### Test Infrastructure Documentation
**Status**: Not Started
**Priority**: High
**Workstream**: Program Management
**Description**: Create comprehensive documentation for the test infrastructure.

#### Technical Details
1. Create tests/README.md
   - [ ] Document test organization and structure
   - [ ] Explain fixture hierarchy and usage
   - [ ] Document test data fixtures
   - [ ] Provide examples of common test patterns
   - [ ] Include guidelines for adding new tests
   - [ ] Document test database setup and teardown
   - [ ] Explain schema validation approach
   - [ ] List test categories (unit, integration, etc.)

2. Benefits
   - Easier onboarding for new developers
   - Consistent test patterns across codebase
   - Better test maintenance
   - Clear guidelines for test creation

3. Success Criteria
   - README.md is created and comprehensive
   - All test fixtures are documented
   - Test patterns are clearly explained
   - Documentation is reviewed and approved
   - Existing tests follow documented patterns

{{ ... }}

## Security
- [ ] Enhance security testing: Add Safety, detect-secrets, and OWASP dependency checks (see ADR-0006)

{{ ... }}
