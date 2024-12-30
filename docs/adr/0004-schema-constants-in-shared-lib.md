# 4. Schema Constants in Shared Library

Date: 2024-12-29

## Status

Accepted

## Context

We had schema-related constants (column sizes, default values, validation rules) duplicated between the models layer and shared library layer. This created maintenance issues and potential inconsistencies. The problem arose because:

1. Both layers needed access to these constants
2. Following our layered architecture principles:
   - Shared library (lower layer) cannot import from models (higher layer)
   - Models can import from shared library
3. We needed to maintain a single source of truth for these constants
4. We wanted to avoid violating our layering principles

## Decision

We decided to:

1. Move all schema-related constants to a new file `shared_lib/schema_constants.py`
2. Have the models layer import these constants from the shared library
3. Remove duplicated constants from the models layer

This decision was made because:

1. These constants are truly "shared" resources that don't contain model-specific logic
2. They are configuration values rather than business logic
3. Placing them in the shared layer maintains proper dependency direction
4. It provides a single source of truth while following architectural principles

Example of the new structure:
```python
# shared_lib/schema_constants.py
COLUMN_SIZES = {
    "EMAIL_LABELS": 500,
    "EMAIL_SUBJECT": 500,
    ...
}

# models/email.py
from shared_lib.schema_constants import COLUMN_SIZES

class Email(Base):
    subject = Column(String(COLUMN_SIZES["EMAIL_SUBJECT"]))
    ...
```

## Consequences

### Positive

1. Single source of truth for schema constants
2. Eliminates code duplication
3. Easier maintenance - changes only need to be made in one place
4. Follows proper layering principles
5. Makes schema-related constants easily accessible to all layers
6. Improves consistency across the codebase

### Negative

1. Schema-related constants are now separated from their primary usage in models
2. Developers need to know to look in shared_lib for schema constants
3. Risk of shared_lib becoming a "catch-all" for constants if not properly managed

### Neutral

1. Need to be disciplined about what belongs in schema_constants.py
2. May need to further organize constants if the file grows too large

## Notes

- We should maintain clear documentation about where schema constants live
- We should periodically review schema_constants.py to ensure it only contains truly shared constants
- Future schema-related constants should be added to this file rather than creating new locations

## References

- [Layered Architecture Pattern](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch01.html)
- [DRY (Don't Repeat Yourself) Principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
