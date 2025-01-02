# ADR 0028: Database Consolidation

## Status
Accepted (2025-01-02)

## Context
Previously, our system used multiple SQLite databases (email.db, analysis.db, catalog.db) to store different types of data. This approach was initially chosen to provide isolation between different subsystems. However, this led to:
1. Increased complexity in database management
2. Difficulty in maintaining referential integrity across databases
3. Overhead in session management and connection handling
4. Complexity in migration management

## Decision
We will consolidate all databases into a single SQLite database (`jexi.db`) while maintaining the existing table structures and relationships. This includes:

1. Database Configuration:
   - Single database file: `data/jexi.db`
   - Unified connection settings in `database_settings.py`
   - Simplified session management

2. Schema Management:
   - Continue using `schema.yaml` as the source of truth
   - Generate models and constants from schema
   - Use direct schema verification instead of migrations
   - Remove Alembic-based migration system

3. Database Session:
   - Single database engine
   - Unified session factory
   - Consistent connection pool settings

## Consequences

### Positive
1. Simplified Database Management:
   - Single source of truth for data
   - Easier backup and restore
   - Simplified session management
   - Reduced configuration complexity

2. Better Data Integrity:
   - Foreign key constraints can be enforced across all tables
   - Transactions can span multiple tables
   - Consistent backup state

3. Improved Performance:
   - Reduced connection overhead
   - Single connection pool
   - Simplified query optimization

4. Simplified Development:
   - Clear data flow
   - Easier testing setup
   - Reduced cognitive load

### Negative
1. Less Isolation:
   - All data in one database
   - Potential for larger transaction scope
   - Need for careful access control

2. Migration Complexity:
   - One-time migration needed for existing data
   - Need to coordinate schema changes across all tables

### Mitigations
1. Use schema verification script to ensure database integrity
2. Maintain clear table prefixes for logical separation
3. Implement robust backup strategy
4. Use transaction management carefully

## Implementation Notes
1. Schema Source of Truth:
   ```
   schema.yaml → schema_constants.py + models/*.py → database
   ```

2. Database Initialization:
   ```python
   rebuild_db.py → verify_database_schema.py
   ```

3. Session Management:
   ```python
   database_settings.py → database_session_util.py → application code
   ```

## Related
- ADR 0004: Configuration-based Schema Definitions
- ADR 0005: Schema Configuration Management
