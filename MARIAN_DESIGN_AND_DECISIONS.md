# Architectural Decisions

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

## Catalog System Design

### 1. Soft Delete Implementation (2024-12-24)
- **Decision**: Implemented soft delete for both catalog items and tags
- **Context**: Need to preserve historical data while allowing items/tags to be "deleted"
- **Implementation**:
  - Added `deleted` (INTEGER) flag to both tables
  - Added `archived_date` (INTEGER) for tracking when items were soft deleted
  - Items marked as deleted are filtered out of active queries
  - Relationships and tags are preserved but hidden when parent item is deleted
- **Consequences**:
  - Can restore deleted items with full history
  - Slightly more complex queries to filter deleted items
  - Additional storage space used for deleted items

### 2. Timestamp Storage (2024-12-24)
- **Decision**: Store all timestamps as INTEGER Unix timestamps
- **Context**: SQLite lacks native date/timestamp type
- **Implementation**:
  - Using INTEGER type for all date fields
  - Storing UTC Unix timestamps (seconds since epoch)
  - Default values use `strftime('%s', 'now')`
  - Python code uses `datetime.utcnow().timestamp()`
- **Advantages**:
  - Efficient storage and comparison
  - No timezone ambiguity (all UTC)
  - Easy sorting
  - Simple arithmetic operations on dates
- **Known Issues**:
  - Year 2038 problem for 32-bit systems (tracked in TODO.md)
  - Need to convert for human-readable display

### 3. Database Schema Design
- **Decision**: Maintain original table names for consistency
- **Tables**:
  - `catalog_items`: Main catalog entries
  - `tags`: Tag definitions
  - `catalog_tags`: Many-to-many relationships
  - `relationships`: Item relationships
  - `chat_history`: Interaction logs
- **Fields Added**:
  - `deleted` (INTEGER)
  - `archived_date` (INTEGER)
  - `created_date` (INTEGER)
  - `modified_date` (INTEGER)

### 4. Testing Strategy
- **Decision**: Comprehensive lifecycle testing
- **Test Coverage**:
  1. Tag creation and application
  2. Tag renaming
  3. Soft deletion of tags
  4. Tag restoration
  5. Multiple tag removal
  6. Item soft deletion
  7. Item restoration
  8. Archive date verification
  9. Visibility checks for deleted items/tags
  10. Cleanup and verification

### 5. Duplicate Handling (2024-12-24)

#### Item Duplicates
1. Case-Insensitive Matching
   - **Decision**: Enforce case-insensitive uniqueness for titles
   - **Implementation**:
     - Using SQLite COLLATE NOCASE
     - Database-level UNIQUE constraints
   - **Consequences**:
     - Prevents confusion with similar titles
     - Slight performance impact on large datasets

2. Archived Items
   - **Decision**: Check archived items before allowing duplicates
   - **Implementation**:
     - Query includes deleted=1 items
     - Prompt for restoration if found
   - **Consequences**:
     - Better data consistency
     - More complex item creation logic

#### Tag Duplicates
1. Case-Insensitive Tags
   - **Decision**: Enforce case-insensitive uniqueness for tag names
   - **Implementation**:
     - UNIQUE constraint with COLLATE NOCASE
     - Preserve case of first occurrence
   - **Consequences**:
     - Consistent tag naming
     - No duplicate tags with different cases

2. Archived Tags
   - **Decision**: Allow restoration of archived tags
   - **Implementation**:
     - Check for archived tags during creation
     - Offer restoration workflow
   - **Consequences**:
     - Better tag reuse
     - More complex tag creation logic

### 6. Interface Design
1. Operation Modes
   - **Decision**: Separate test and interactive modes
   - **Implementation**:
     - Default test mode in main script
     - Separate interactive script
   - **Consequences**:
     - Cleaner separation of concerns
     - Better user experience for each mode

2. Error Handling
   - **Decision**: Comprehensive error messages and suggestions
   - **Implementation**:
     - Specific error types
     - Restoration suggestions
     - Clear user guidance
   - **Consequences**:
     - Better user experience
     - More maintainable error handling

## Future Considerations
1. Migration strategy for timestamp fields if/when changing from 32-bit
2. Archival strategy for very old soft-deleted items
3. Performance optimization for queries with many soft-deleted items
4. Implementation of fuzzy matching for similar items
5. Tag hierarchy and relationship system
6. Bulk operations for tags and items
7. Backup and restore functionality
8. Performance benchmarks and optimization
