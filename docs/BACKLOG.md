# Marian Development Backlog

## Workstreams Overview
### Email Processing
**Status**: Active
**Focus**: Email retrieval, analysis, and storage
**Current Priority**: Schema validation and testing
**Objective**: Build robust email processing infrastructure for information extraction and analysis

### Catalog/Librarian
**Status**: Active
**Focus**: Information organization and retrieval
**Current Priority**: Interactive chat system development
**Objective**: Create an intelligent catalog system that enables interactive information management through natural language conversations, helping organize, retrieve, and maintain a knowledge base of resources and information while leveraging the email processing infrastructure

### Program Management
**Status**: Active
**Focus**: Standards, processes, and coordination
**Current Priority**: Documentation restructuring
**Objective**: Establish and maintain development standards, documentation, and processes that promote quality, maintainability, and cross-workstream coordination

## High Priority

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

### Email Processing Prototype
**Status**: In Progress
**Priority**: Highest
**Workstream**: Email Processing
**Description**: Implement a working prototype for email retrieval and processing workflow.

#### Technical Details
1. Email Retrieval
   - Implement Gmail API connection
   - Add batch retrieval of messages
   - Handle rate limiting
   - Store raw messages in database

2. Email Processing
   - Parse email content and metadata
   - Extract key fields (subject, sender, date, body)
   - Handle different email formats
   - Process attachments flag
   - Basic error handling

3. Testing & Validation
   - Add integration tests
   - Test with various email formats
   - Validate data storage
   - Monitor API usage

#### Success Criteria
- Can retrieve emails from Gmail
- Successfully stores in database
- Handles common email formats
- Basic error handling in place
- Reasonable performance with batches

#### Implementation Steps
1. Complete Gmail API integration
2. Implement message retrieval
3. Add database storage
4. Add basic processing
5. Add error handling
6. Test with real data

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
- [ ] Update chat_session_manager.py for new workflow
  - [ ] Create session summaries in docs/sessions/
  - [ ] Use standardized file naming (session_YYYYMMDD_HHMM.md)
  - [ ] Include timezone in timestamps
  - [ ] Implement session summary template
  - [ ] Add session file cleanup/archival
- [ ] Add session summary validation
  - [ ] Check required sections
  - [ ] Validate timestamps
  - [ ] Verify file location
- [ ] Improve session documentation
  - [ ] Update workflow documentation
  - [ ] Add file naming conventions
  - [ ] Document archival process

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

### Code Quality Improvements
**Status**: Planned
**Priority**: Medium
**Workstream**: Program Management
**Description**: Evaluate and implement code quality tools

#### Code Quality Tool Options

1. **Code Formatting**
Consider implementing automated code formatting using black:
- Consistent code style across the project
- Eliminates style debates
- Automated formatting during pre-commit
- Most opinionated option, least configuration needed

2. **Linting with Flake8**
Alternative or complement to black:
- Combines PyFlakes, pycodestyle, and Mccabe
- More flexible than black (configurable rules)
- Catches logical errors (unused imports, undefined variables)
- Style checking (PEP 8 compliance)
- Code complexity checks
- Can be used alongside black or as an alternative

3. **Static Type Checking**
Consider implementing mypy for type checking:
- Catch type-related errors before runtime
- Better code documentation through type hints
- Improved IDE support
- Can be used with either formatting solution

**Implementation Considerations**:
1. Tool Selection:
   - Choose between black (strict) vs flake8 (flexible) for style
   - Can use flake8 with black if only using it for logical errors
   - mypy is complementary to either choice

2. Adoption Strategy:
   - Start with new code only
   - Gradually add to existing code
   - Focus on critical paths first
   - Add CI/CD integration later

3. Dependencies:
   - Complete code organization improvements first
   - Align with necessary and sufficient principle
   - Consider impact on development velocity

**Session Reference**: 2024-12-25-10-02

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
All tasks and features related to the Catalog system are tracked in [CATALOG_BACKLOG.md](CATALOG_BACKLOG.md).

### Email Processing
{{ ... }}

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

## Prototypes Status and Plans

### Active Prototypes
- [ ] proto_gmail_operations.py
  - Status: Active, needed for future features
  - Contains: Email creation, sending, draft management
  - Next steps: Integrate into main app when email sending is needed
  - Priority: Medium

- [ ] proto_google_keep.py
  - Status: Active, for future integration
  - Contains: Google Keep API authentication and basic operations
  - Next steps: Use as foundation for Keep integration
  - Priority: Low

- [ ] proto_inspect_prompts.py
  - Status: Active, needs update
  - Contains: Prompt performance monitoring and inspection
  - Next steps: Update to work with new storage system
  - Priority: Medium
  - See monitoring section for detailed plans

### Future Features from Prototypes
- [ ] Prompt Version Management (from proto_prompt_manager.py)
  - Version history tracking with active/inactive states
  - Script/purpose/task organization
  - Performance metrics tracking
  - JSON schema validation for prompts
  - Priority: Medium
  - Dependencies: Updated storage system

- [ ] Gmail Operations Integration
  - Move operations from proto_gmail_operations.py to main app
  - Features to add:
    - Email composition and sending
    - Draft management
    - Rich text email support
  - Priority: Medium
  - Dependencies: None

- [ ] Google Keep Integration
  - Use proto_google_keep.py as foundation
  - Features to add:
    - Note creation and management
    - Label synchronization
    - Content search
  - Priority: Low
  - Dependencies: None

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

### Documentation Improvements
**Status**: In Progress
**Priority**: Medium
**Workstream**: Program Management
**Added**: 2024-12-24
**Session**: 2024-12-24-22-42

#### Tasks
- [ ] Review Data Storage and Schema section for potential consolidation
  - Context: Follow-up from documentation cleanup
  - Consider merging implementation details with storage considerations
- [ ] Add implementation examples for key features
  - Context: Make documentation more practical
  - Include code snippets for common operations
- [ ] Review other documentation files for duplicate sections
  - Context: Continue documentation cleanup effort
  - Apply same principles used in MARIAN_DESIGN_AND_DECISIONS.md

### Code Organization and Technical Debt
**Status**: In Progress
**Priority**: Medium
**Workstream**: Program Management
**Description**: Address technical debt and improve code organization.

#### Technical Details
1. Review and Organize Prototype Files
- **Status**: Not Started
- **Priority**: Medium
- **Description**: Review prototype files to determine which are still needed for future development and which are obsolete.
- **Files to Review**:
  - `proto_gmail_operations.py`: Gmail API operations prototypes
  - `proto_google_keep.py`: Google Keep integration prototype
  - `proto_inspect_prompts.py`: Prompt inspection utilities
  - `proto_prompt_manager.py`: Prompt management system prototype
  - `proto_read_gmail.py`: Gmail reading functionality prototype
- **Action Items**:
  - [ ] Review each file's functionality and current usage
  - [ ] Identify which features have already been implemented in production code
  - [ ] Document which prototypes are still needed for future features
  - [ ] Create tasks for implementing needed features
  - [ ] Archive obsolete prototypes
- **Dependencies**: None
- **Notes**: 
  - Keep files that will be useful for upcoming features
  - Document any valuable patterns or approaches before archiving files
  - Consider moving active prototypes to a dedicated prototypes/ directory

### Documentation and Process Management
**Status**: New
**Priority**: High
**Workstream**: Program Management
**Description**: Improve documentation management and session workflows

#### Session Management Improvements
- [ ] Standardize Session Types
  - Define criteria for Full, Light, and Emergency sessions
  - Document requirements for each session type
  - Create templates for each type
  - Add validation checks for session type compliance

- [ ] Session Log Integration
  - [ ] Create automated validation for session log format
  - [ ] Develop tools for extracting action items to backlog
  - [ ] Implement cross-referencing between sessions and backlog
  - [ ] Add session summary generation

#### Documentation Management
- [ ] Version Control and Review Process
  - [ ] Establish version tracking for documentation files
  - [ ] Define documentation review cycles
  - [ ] Create changelog requirements
  - [ ] Set up automated consistency checks

- [ ] Archival Procedures
  - [ ] Define standard process for deprecating files
  - [ ] Create archival checklist
  - [ ] Implement archival tracking system
  - [ ] Add validation for proper archival execution

#### Backlog Management
- [ ] Create backlog item lifecycle process
  - [ ] Define status transitions
  - [ ] Add priority adjustment guidelines
  - [ ] Create workstream assignment rules
  - [ ] Implement regular backlog review schedule

### Testing Infrastructure
**Status**: New
**Priority**: High
**Workstream**: Program Management
**Description**: Enhance testing coverage and reporting

#### Test Coverage Improvements
- [ ] Implement test coverage reporting
  - [ ] Set up coverage measurement tools
  - [ ] Define coverage targets by component
  - [ ] Create coverage report templates
  - [ ] Add coverage tracking over time

#### Test Expansion
- [ ] Anthropic Library Testing
  - [ ] Create comprehensive test plan for test_anthropic_lib.py
  - [ ] Add integration tests
  - [ ] Implement mock responses
  - [ ] Add error condition testing

- [ ] JSON Processing Testing
  - [ ] Expand test_json_extraction.py coverage
  - [ ] Add edge case tests
  - [ ] Implement performance tests
  - [ ] Add validation testing

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

### Chat Interface Implementation
**Status**: New
**Priority**: High
**Workstream**: Catalog/Librarian
**Description**: Implement the basic chat interface for the catalog system

#### Core Components
1. Natural Language Processing
   - [ ] Implement intent detection
     - Identify search queries
     - Detect add/update/delete operations
     - Handle system commands
     - Parse complex queries
   - [ ] Add entity extraction
     - Extract dates and time ranges
     - Identify tags and categories
     - Parse item attributes
     - Handle multiple entities per query

2. Query Processing
   - [ ] Enhance semantic search
     - Implement relevance ranking
     - Add fuzzy matching
     - Handle synonyms and related terms
     - Support compound queries
   - [ ] Add result filtering
     - Filter by date ranges
     - Filter by tags
     - Filter by status
     - Support multiple filters

3. Response Generation
   - [ ] Implement structured responses
     - Create consistent response format
     - Add support for rich text
     - Include metadata in responses
     - Handle multi-item responses
   - [ ] Add error handling
     - Create user-friendly error messages
     - Add suggestion for corrections
     - Handle edge cases gracefully
     - Provide clear next steps

4. User Interface
   - [ ] Enhance command-line interface
     - Add command history
     - Implement tab completion
     - Add syntax highlighting
     - Support multiline input
   - [ ] Improve user experience
     - Add progress indicators
     - Implement pagination
     - Add help system
     - Support command aliases

#### Integration Points
1. Database Integration
   - [ ] Optimize queries
   - [ ] Add connection pooling
   - [ ] Implement caching
   - [ ] Add transaction management

2. Logging System
   - [ ] Add structured logging
   - [ ] Implement query logging
   - [ ] Add performance metrics
   - [ ] Create debug logging

3. Claude AI Integration
   - [ ] Optimize prompt engineering
   - [ ] Add response caching
   - [ ] Implement rate limiting
   - [ ] Add fallback handling

#### Success Criteria
- Natural language queries are correctly interpreted
- Search results are relevant and ranked appropriately
- Response times are under 2 seconds for most operations
- Error messages are clear and actionable
- User interface is intuitive and responsive

#### Dependencies
- Claude AI API access
- Database schema implementation
- Logging system setup
- Configuration management

#### Implementation Order
1. Basic query processing
2. Simple response generation
3. Core UI improvements
4. Enhanced NLP features
5. Advanced filtering
6. Performance optimizations

### Critical Tasks

### Chat Log Retention System [HIGH PRIORITY]
**Due: 2024-01-08**
The chat logs are a critical system component that require careful management:

1. Storage Requirements Analysis:
   - [ ] Analyze chat log growth rate over 2 weeks
   - [ ] Calculate average log entry size
   - [ ] Project storage needs for 1 year
   - [ ] Define retention period requirements

2. Retention Policy Implementation:
   - [ ] Design tiered storage system:
     - Hot storage: Recent logs (last 30 days)
     - Warm storage: Medium-term logs (last 90 days)
     - Cold storage: Archive (older than 90 days)
   - [ ] Implement automatic archival system
   - [ ] Add compression for archived logs
   - [ ] Create cleanup policy for old archives

3. Monitoring and Alerts:
   - [ ] Add storage usage monitoring
   - [ ] Implement early warning system for storage limits
   - [ ] Create dashboard for log statistics
   - [ ] Set up alerts for failed archival operations

4. Backup Integration:
   - [ ] Include chat logs in regular backup schedule
   - [ ] Verify backup integrity
   - [ ] Test restoration procedures
   - [ ] Document recovery process

### Immediate Actions
- [ ] **URGENT: Review chat log storage on 2024-01-08**
  - Check storage usage
  - Analyze growth rate
  - Assess immediate storage needs
  - Report findings in session log

### Testing Framework
- [ ] **CRITICAL: Remove Mock Email Processor and Simplify Testing**
  - Current Usage:
    - `utils/util_test_data.py` contains mock data and processor
    - Used only in `tests/test_version_tracking.py`
    - Provides `EmailProcessor`, `load_test_fixtures`, `generate_test_data`
  - Required Changes:
    - Remove `utils/util_test_data.py` entirely
    - Update `test_version_tracking.py` to use Gmail API test mode
    - Replace mock `EmailProcessor` with real email processing
    - Remove test data generation in favor of real test emails
  - Benefits:
    - More reliable tests that match production behavior
    - Simpler test setup and maintenance
    - Better test coverage of actual functionality
  - Impact: Improves test reliability and maintainability
  - Dependencies: None
  - Estimated time: 1-2 days

### Email Processing
{{ ... }}

### Documentation
- [ ] **Standardize Session File Naming**
  - Current inconsistent formats:
    - `session_YYYYMMDD_HHMM.md`
    - `YYYY-MM-DD-HH-MM.md`
    - `YYYYMMDD_HHMM.md`
  - Standardize on format: `session_YYYYMMDD_HHMM.md`
  - Rename existing files to match standard
  - Update SESSION_TEMPLATE.md to document naming convention
  - Impact: Improves organization and searchability
  - Dependencies: None
  - Estimated time: 30 minutes

### Email Processing
{{ ... }}

### Infrastructure
- [ ] **CRITICAL: Implement Daily Backup System**
  - Create automated backup script for:
    - All database files (*.db)
    - Email analysis data
    - Configuration files
  - Features needed:
    - Daily scheduled runs
    - Compression and encryption
    - Version retention policy
    - Error notification system
    - Backup verification
  - Store backups in dedicated backup/ directory
  - Add backup status to monitoring
  - Impact: Prevents data loss and enables recovery
  - Dependencies: None
  - Estimated time: 1 day

### Monitoring and Debugging
- [ ] Add logging for email processing failures
- [ ] Create dashboard for system health metrics
- [ ] Add monitoring for API rate limits
- [ ] Update proto_inspect_prompts.py to work with new prompt storage system
  - Currently uses SQLite but should be updated to current storage
  - Keep existing functionality:
    - Tabulated overview of all prompts
    - Version history tracking
    - Usage statistics (times used, confidence, response times)
    - Failure rate monitoring
  - Add new features:
    - Export/import of prompt configurations
    - Performance comparison between prompt versions
    - Integration with logging system

### Documentation Review Tasks
**Status**: New
**Priority**: High
**Workstream**: Program Management
**Description**: Review and improve documentation for clarity, accuracy, and completeness.

#### Technical Details
1. **Documentation Review**
   - Review all documentation files for clarity and accuracy
   - Check for outdated information and update accordingly
   - Ensure consistency in formatting and style

2. **Documentation Improvements**
   - Add implementation examples for key features
   - Include code snippets for common operations
   - Review other documentation files for duplicate sections
   - Apply same principles used in MARIAN_DESIGN_AND_DECISIONS.md

3. **Documentation Validation**
   - Validate documentation against current codebase
   - Ensure documentation covers all critical components
   - Add documentation for new features and changes

#### Success Criteria
- All documentation reviewed and updated
- No outdated information
- Consistent formatting and style
- Clear and accurate documentation
- Complete coverage of critical components

#### Dependencies
- None

#### Notes
- Review all documentation files
- Update documentation to reflect recent changes
- Ensure documentation is accurate and complete
- Follow documentation guidelines and principles

### Code Organization and Technical Debt
**Status**: In Progress
**Priority**: Medium
**Workstream**: Program Management
**Description**: Address technical debt and improve code organization.

#### Technical Details
1. Review and Organize Prototype Files
- **Status**: Not Started
- **Priority**: Medium
- **Description**: Review prototype files to determine which are still needed for future development and which are obsolete.
- **Files to Review**:
  - `proto_gmail_operations.py`: Gmail API operations prototypes
  - `proto_google_keep.py`: Google Keep integration prototype
  - `proto_inspect_prompts.py`: Prompt inspection utilities
  - `proto_prompt_manager.py`: Prompt management system prototype
  - `proto_read_gmail.py`: Gmail reading functionality prototype
- **Action Items**:
  - [ ] Review each file's functionality and current usage
  - [ ] Identify which features have already been implemented in production code
  - [ ] Document which prototypes are still needed for future features
  - [ ] Create tasks for implementing needed features
  - [ ] Archive obsolete prototypes
- **Dependencies**: None
- **Notes**: 
  - Keep files that will be useful for upcoming features
  - Document any valuable patterns or approaches before archiving files
  - Consider moving active prototypes to a dedicated prototypes/ directory

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

### Documentation Improvements
**Status**: In Progress
**Priority**: Medium
**Workstream**: Program Management
**Added**: 2024-12-24
**Session**: 2024-12-24-22-42

#### Tasks
- [ ] Review Data Storage and Schema section for potential consolidation
  - Context: Follow-up from documentation cleanup
  - Consider merging implementation details with storage considerations
- [ ] Add implementation examples for key features
  - Context: Make documentation more practical
  - Include code snippets for common operations
- [ ] Review other documentation files for duplicate sections
  - Context: Continue documentation cleanup effort
  - Apply same principles used in MARIAN_DESIGN_AND_DECISIONS.md

### Code Organization and Technical Debt
**Status**: In Progress
**Priority**: Medium
**Workstream**: Program Management
**Description**: Address technical debt and improve code organization.

#### Technical Details
1. Review and Organize Prototype Files
- **Status**: Not Started
- **Priority**: Medium
- **Description**: Review prototype files to determine which are still needed for future development and which are obsolete.
- **Files to Review**:
  - `proto_gmail_operations.py`: Gmail API operations prototypes
  - `proto_google_keep.py`: Google Keep integration prototype
  - `proto_inspect_prompts.py`: Prompt inspection utilities
  - `proto_prompt_manager.py`: Prompt management system prototype
  - `proto_read_gmail.py`: Gmail reading functionality prototype
- **Action Items**:
  - [ ] Review each file's functionality and current usage
  - [ ] Identify which features have already been implemented in production code
  - [ ] Document which prototypes are still needed for future features
  - [ ] Create tasks for implementing needed features
  - [ ] Archive obsolete prototypes
- **Dependencies**: None
- **Notes**: 
  - Keep files that will be useful for upcoming features
  - Document any valuable patterns or approaches before archiving files
  - Consider moving active prototypes to a dedicated prototypes/ directory

### Documentation and Process Management
**Status**: New
**Priority**: High
**Workstream**: Program Management
**Description**: Improve documentation management and session workflows

#### Session Management Improvements
- [ ] Standardize Session Types
  - Define criteria for Full, Light, and Emergency sessions
  - Document requirements for each session type
  - Create templates for each type
  - Add validation checks for session type compliance

- [ ] Session Log Integration
  - [ ] Create automated validation for session log format
  - [ ] Develop tools for extracting action items to backlog
  - [ ] Implement cross-referencing between sessions and backlog
  - [ ] Add session summary generation

#### Documentation Management
- [ ] Version Control and Review Process
  - [ ] Establish version tracking for documentation files
  - [ ] Define documentation review cycles
  - [ ] Create changelog requirements
  - [ ] Set up automated consistency checks

- [ ] Archival Procedures
  - [ ] Define standard process for deprecating files
  - [ ] Create archival checklist
  - [ ] Implement archival tracking system
  - [ ] Add validation for proper archival execution

#### Backlog Management
- [ ] Create backlog item lifecycle process
  - [ ] Define status transitions
  - [ ] Add priority adjustment guidelines
  - [ ] Create workstream assignment rules
  - [ ] Implement regular backlog review schedule

### Testing Infrastructure
**Status**: New
**Priority**: High
**Workstream**: Program Management
**Description**: Enhance testing coverage and reporting

#### Test Coverage Improvements
- [ ] Implement test coverage reporting
  - [ ] Set up coverage measurement tools
  - [ ] Define coverage targets by component
  - [ ] Create coverage report templates
  - [ ] Add coverage tracking over time

#### Test Expansion
- [ ] Anthropic Library Testing
  - [ ] Create comprehensive test plan for test_anthropic_lib.py
  - [ ] Add integration tests
  - [ ] Implement mock responses
  - [ ] Add error condition testing

- [ ] JSON Processing Testing
  - [ ] Expand test_json_extraction.py coverage
  - [ ] Add edge case tests
  - [ ] Implement performance tests
  - [ ] Add validation testing

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