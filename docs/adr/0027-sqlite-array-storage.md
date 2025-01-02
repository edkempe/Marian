# 27. SQLite Array Storage Strategy

Date: 2025-01-01

## Status

Accepted

## Context

SQLite does not natively support array data types, but our application needs to store array-like data (e.g., categories, key_points) in the database. We need a consistent strategy for handling array storage that:

1. Works with SQLite's limitations
2. Maintains data integrity
3. Provides good query performance
4. Is consistent across the application
5. Integrates well with SQLAlchemy

## Decision

We will store array data in SQLite using JSON columns. Specifically:

1. Use SQLAlchemy's `JSON` type for array columns
2. Store arrays as JSON arrays in the database
3. Handle serialization/deserialization in the model layer
4. Use JSON Schema for validation
5. Add appropriate indexes for query performance

Example implementation:
```python
from sqlalchemy import JSON
from sqlalchemy.orm import validates
import json

class EmailAnalysis(Base):
    categories = Column(JSON, nullable=True)
    key_points = Column(JSON, nullable=True)

    @validates("categories")
    def validate_categories(self, key, value):
        if value is not None:
            if not isinstance(value, list):
                raise ValueError("Categories must be a list")
            return json.dumps(value)
        return value

    @property
    def categories_list(self):
        return json.loads(self.categories) if self.categories else []
```

## Rationale

We chose JSON storage over alternatives because:

1. **Native SQLite Support**: SQLite has built-in JSON support and functions
2. **Flexibility**: JSON can store arrays of any size
3. **Query Support**: SQLite JSON functions allow querying array contents
4. **Type Safety**: Can validate data structure at the model layer
5. **Performance**: JSON storage is more efficient than string concatenation
6. **Standards**: JSON is a well-understood format with good tool support

## Consequences

### Positive

1. **Compatibility**: Works with SQLite's limitations
2. **Maintainability**: Clear, standard approach to array storage
3. **Performance**: Efficient storage and retrieval
4. **Flexibility**: Can store arrays of varying sizes
5. **Validation**: Can enforce data structure at model layer
6. **Query Support**: Can use SQLite JSON functions for queries

### Negative

1. **Complexity**: Need to handle serialization/deserialization
2. **Query Syntax**: JSON queries are more complex than native array operations
3. **Migration**: May need to migrate existing string-based arrays
4. **Indexing**: Need to carefully consider indexing strategy for JSON columns

## Implementation Notes

1. Always use SQLAlchemy's `JSON` type for array columns
2. Implement validation in model layer
3. Add helper properties for easy access to array data
4. Use JSON Schema for complex validation
5. Consider adding indexes for frequently queried array elements
6. Document JSON query patterns for developers

## Related Decisions

- [ADR-0003](./0003-test-database-strategy.md): Test Database Strategy
- [ADR-0004](./0004-configuration-based-schema-definitions.md): Configuration-Based Schema Definitions
