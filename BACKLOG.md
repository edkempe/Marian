# Marian Development Backlog

## High Priority

### Schema Validation and Testing
**Status**: In Progress
**Priority**: Highest
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

### Code DRY (Don't Repeat Yourself) Review
**Status**: Planned  
**Priority**: High  
**Description**: Review and refactor code to eliminate duplication and improve maintainability.

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

## Medium Priority

### Documentation Updates
**Status**: Pending
**Priority**: Medium
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

## Low Priority
