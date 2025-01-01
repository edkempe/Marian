# 19. API-First Schema Design

Date: 2025-01-01

## Status

Accepted

## Revision History
1.0.0 (2025-01-01) @dev
- Initial version
- Migrated from database-design.md
- Added explicit API alignment principles

## Context

Our system heavily integrates with external APIs (particularly Gmail API) and needs to maintain data consistency between these APIs and our local database. We need a systematic approach to:

1. Handle external API data types and constraints
2. Maintain consistency between API and database schemas
3. Ensure reliable data mapping and transformation
4. Support schema evolution without breaking API compatibility

## Decision

We will implement an API-First Schema Design approach with the following principles:

### 1. External APIs as Source of Truth
- Field types must match API specifications exactly
- Field names preserve API conventions where possible
- Database constraints must reflect API limitations
- Example: Using string IDs because Gmail API uses string IDs

### 2. Model-Driven Schema
- SQLAlchemy models are the definitive schema definition
- Models must document API alignment through comments and types
- Additional fields must follow API naming patterns
- No schema changes allowed without corresponding model updates

### 3. Migration-Based Changes
- All schema changes require Alembic migrations
- Migrations must be tested against API data
- Changes must maintain backward compatibility
- Type changes must preserve data integrity

### 4. Schema Validation
- Runtime validation of API data against schema
- Pre-commit hooks to validate schema consistency
- Automated tests for API compatibility
- Regular schema audits against API documentation

## Consequences

### Positive
1. **Consistency**: Perfect alignment between API and database schemas
2. **Reliability**: Reduced data transformation errors
3. **Maintainability**: Clear source of truth for schema decisions
4. **Compatibility**: Better handling of API versioning
5. **Documentation**: Self-documenting through models and migrations

### Negative
1. **Flexibility**: Less freedom in schema design
2. **Complexity**: More validation and testing required
3. **Performance**: Potential overhead from string IDs vs integers

### Mitigation
1. Use views or computed columns for optimized queries
2. Implement caching for frequently accessed data
3. Maintain comprehensive API compatibility tests

## Technical Details

### Schema Definition Example
```python
class EmailMessage(Base):
    __tablename__ = 'email_messages'
    
    # Gmail API uses string IDs
    message_id = Column(String(GMAIL_ID_LENGTH), primary_key=True)
    
    # Preserve Gmail API field names
    thread_id = Column(String(GMAIL_ID_LENGTH), nullable=False)
    label_ids = Column(ARRAY(String(GMAIL_LABEL_LENGTH)))
    
    # Additional fields follow API patterns
    raw_size = Column(Integer, comment="Size in bytes, from Gmail API")
```

### Validation Rules
1. Primary keys must match API ID types
2. Nullable/required constraints must match API
3. String lengths must accommodate API maximums
4. Array types must match API collection formats

## Related Decisions
- [ADR-0003](0003-test-database-strategy.md): Database testing strategy
- [ADR-0004](0004-configuration-based-schema-definitions.md): Schema configuration system

## Notes
- Regular audits needed to catch API changes
- Consider automated schema comparison tools
- Document any deviations from API schema

## References
- [Gmail API Schema Reference](https://developers.google.com/gmail/api/reference/rest)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Migration Guide](https://alembic.sqlalchemy.org/)
