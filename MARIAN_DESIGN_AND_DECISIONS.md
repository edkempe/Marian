# Architectural Decisions

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

## Future Considerations
1. Migration strategy for timestamp fields if/when changing from 32-bit
2. Archival strategy for very old soft-deleted items
3. Performance optimization for queries with many soft-deleted items
