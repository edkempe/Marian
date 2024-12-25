# ADR 001: SQLAlchemy Models as Source of Truth

## Status
Accepted (2024-12-25)

## Context
The project needs a clear, authoritative source of truth for database schema and data models. We evaluated two approaches:
1. Schema-first: Using SQL schema files and documentation as source of truth
2. Model-first: Using SQLAlchemy models as source of truth

## Decision
We will use SQLAlchemy models as the primary source of truth for our data model, supported by alembic migrations for schema tracking.

### Implementation
1. Primary Sources:
   - Schema Definition: SQLAlchemy models in `models/`
   - Configuration: `constants.py`
   - Schema History: Alembic migrations

2. Models Location:
   ```
   models/
   ├── base.py          # Base model configuration
   ├── email.py         # Email and thread models
   ├── catalog.py       # Catalog models
   └── email_analysis.py # Analysis models
   ```

3. Documentation Strategy:
   - Reference models directly instead of duplicating schema
   - Use model docstrings for field documentation
   - Keep migration history for schema changes

## Rationale
Analysis of the codebase shows heavy reliance on SQLAlchemy features:

1. Type Safety:
   ```python
   # Type checking and validation
   id: Mapped[str] = Column(Text, primary_key=True)
   thread_id: Mapped[str] = Column(Text, nullable=False)
   ```

2. Relationship Management:
   ```python
   # Automatic relationship handling
   tags: Mapped[List["Tag"]] = relationship(
       "Tag",
       secondary="catalog_tags",
       back_populates="items"
   )
   ```

3. Test Integration:
   - Models used extensively in test fixtures
   - Type checking in tests
   - Relationship validation

4. Application Usage:
   - ORM features used throughout apps
   - Consistent interface across codebase
   - Type-safe queries

## Consequences

### Positive
1. Type safety at runtime
2. Automated relationship management
3. Integration with test infrastructure
4. Single source of truth in code
5. Migration tracking through alembic

### Negative
1. Learning curve for SQLAlchemy
2. Additional abstraction layer
3. Need to maintain migrations

### Mitigations
1. Document model usage patterns
2. Keep models simple and focused
3. Use alembic for migration management

## Related
- Previous schema documentation in `database_schema.md` (to be archived)
- Alembic migration scripts
- Model test files
