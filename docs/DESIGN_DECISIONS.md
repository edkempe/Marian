# Marian Design and Decisions

## Decision Record Template
```markdown
### [Title] (YYYY-MM-DD)
**Decision**: [Brief description of the decision]

#### Context
- [Background information]
- [Current state]
- [Problem being solved]

#### Decision Factors
1. **[Factor 1]**
   - [Details]
   - [Impact]

2. **[Factor 2]**
   - [Details]
   - [Impact]

#### Impact
- [Expected outcomes]
- [Changes required]
- [Benefits]

#### Related Documents
- [Document links]
- [Related decisions]
```

## Documentation Organization Decisions

### Project Plan Document Structure (2024-12-24)
**Decision**: Keep organizational guidelines, principles, and implementation details consolidated in PROJECT_PLAN.md rather than splitting into separate documents.

#### Context
- Considered splitting PROJECT_PLAN.md content into separate documents:
  - Code reuse guidelines to `docs/development/reuse_guide.md`
  - Contributor guidelines to `docs/development/contributor_guide.md`
  - Domain organization to `docs/architecture/domain_organization.md`
  - Maintenance guidelines to `docs/development/maintenance.md`

#### Decision Factors
1. **AI Context and Comprehension**
   - AI models work better with consolidated, directly accessible information
   - Single document provides complete context for decision-making
   - Easier for AI to find and follow guidelines
   - Reduces risk of missing information

2. **Single Source of Truth**
   - Comprehensive reference in one location
   - Clear authority for organizational decisions
   - Reduced risk of inconsistency
   - Easier to maintain and update

3. **Implementation Clarity**
   - Guidelines directly connected to implementation details
   - Clear connection between principles and practice
   - Easier to enforce consistency
   - Better support for code reuse

#### Impact
- Better AI assistance in maintaining project structure
- More consistent implementation of guidelines
- Easier onboarding for new contributors
- More reliable code reuse

#### Related Documents
- PROJECT_PLAN.md
- docs/development/*
- docs/architecture/*

### AI Session Management Location (2024-12-24)
**Decision**: Create root-level AI_SESSION_GUIDE.md for primary AI interaction documentation, separate from session logs.

#### Context
- Previously had session management spread across multiple files:
  - CHAT_START.md
  - CHAT_CLOSE.md
  - SESSION_WORKFLOW.md
  - docs/sessions/README.md

#### Decision Factors
1. **Visibility**
   - AI assistants need immediate access to interaction guidelines
   - Root-level placement ensures high visibility
   - Clear separation between guidelines and logs

2. **Usability**
   - Single source of truth for AI interaction
   - Easy to find and reference
   - Comprehensive but focused content

3. **Maintainability**
   - Clear separation of concerns
   - Session logs separate from guidelines
   - Easier to update and maintain

#### Impact
- More consistent AI interactions
- Clearer session management
- Better organization of session history
- Improved documentation findability

#### Implementation
- Created root-level AI_SESSION_GUIDE.md for primary AI interaction documentation

#### Related Documents
- AI_SESSION_GUIDE.md
- docs/sessions/* (for logs only)

### Task Management Simplification (2024-12-24)
**Decision**: Remove NEXT_SESSION.md and enhance BACKLOG.md to handle immediate priorities.

## Catalog System Design Decisions

### Data Storage and Schema

#### Timestamps
- All timestamps are stored as INTEGER Unix timestamps in UTC
- This ensures consistent timezone handling and efficient storage
- Future consideration: Plan for Year 2038 problem on 32-bit systems

#### Unique Constraints
- Title and tag name uniqueness is enforced at the database level
- Case-insensitive comparison using SQLite's COLLATE NOCASE
- Prevents duplicate entries while maintaining data integrity

### Duplicate Handling

#### Item Duplicates
1. Case-Insensitive Matching
   - Titles are compared case-insensitively
   - Prevents confusion with similar titles like "MyItem" vs "myitem"

2. Archived Items
   - System detects if an item with same title exists but is archived
   - Prompts user to restore archived item instead of creating duplicate
   - Maintains historical data while preventing duplicates

#### Tag Duplicates
1. Case-Insensitive Tags
   - Tag names are unique regardless of case
   - System preserves the case of the first occurrence
   - Example: If "Documentation" exists, cannot add "documentation"

2. Archived Tags
   - System detects attempts to use archived tags
   - Offers restoration of archived tags
   - Prevents tag proliferation while maintaining consistency

### Archive System

#### Soft Delete Implementation
1. Deletion Strategy
   - Items and tags are never physically deleted by default
   - `deleted` flag (INTEGER) marks items as archived
   - `archived_date` (INTEGER) records when item was archived

2. Restoration Process
   - Archived items can be restored with original metadata
   - System prevents duplicate creation while items are archived
   - Maintains data history and prevents accidental data loss

#### Visibility Rules
1. Active Items
   - Only non-archived items appear in regular searches
   - Tags can only be applied to active items
   - Ensures clean user experience

2. Archived Items
   - Accessible through specific archive queries
   - Can be restored to active status
   - Maintains data history while keeping active data clean

### Interface Design

#### Operation Modes
1. Test Mode (Default)
   - Runs integration tests
   - Validates system integrity
   - Non-interactive operation

2. Interactive Mode
   - Separate script (app_catalog_interactive.py)
   - Command-line interface
   - User-friendly help system

#### Error Handling
1. User Feedback
   - Clear error messages for duplicate detection
   - Helpful suggestions for archived items
   - Guided restoration process

2. Data Integrity
   - Transaction-based operations
   - Proper cleanup in tests
   - Consistent state management

## Future Considerations
1. Migration strategy for timestamp fields if/when changing from 32-bit
2. Archival strategy for very old soft-deleted items
3. Performance optimization for queries with many soft-deleted items
4. Implementation of fuzzy matching for similar items
5. Tag hierarchy and relationship system
6. Bulk operations for tags and items
7. Backup and restore functionality
8. Performance benchmarks and optimization
