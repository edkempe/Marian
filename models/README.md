# Marian Models

**Version:** 1.1.0  
**Status:** Authoritative

> SQLAlchemy models and domain constants for the Marian project.

## Overview

This package defines the core domain models and business rules for Marian. It follows Domain-Driven Design principles with a clear hierarchy of truth:

```
core_constants.py  (Domain Rules)
       ↓
models/*.py       (Implementation)
       ↓
constants.py      (Configuration)
```

## Quick Reference

```python
from models.core_constants import AssetType, ItemStatus
from models import CatalogItem, Tag

# Create a new catalog item
item = CatalogItem(
    title="Example Item",
    asset_type=AssetType.CODE,
    status=ItemStatus.DRAFT
)
```

## Core Components

### 1. Domain Constants (`core_constants.py`)
- Source of truth for domain rules
- Type-safe enums for valid values
- Business constraints and validations
- State transition rules

```python
from models.core_constants import AssetType, ItemStatus, RelationType

# Type-safe asset types
asset_type = AssetType.CODE

# Valid status transitions
if item.status == ItemStatus.DRAFT:
    valid_transitions = STATE_TRANSITIONS[ItemStatus.DRAFT]
```

### 2. Domain Models
- Implement business rules
- Enforce data integrity
- Define relationships
- Handle persistence

```python
from models import CatalogItem, Tag, EmailAnalysis

# Models use core constants
item = CatalogItem(
    title="Code Example",
    asset_type=AssetType.CODE,
    status=ItemStatus.DRAFT
)
```

### 3. Mixins
- Reusable behaviors
- Common patterns
- Shared validations

```python
from models.mixins import TimestampMixin

class MyModel(Base, TimestampMixin):
    __tablename__ = 'my_models'
```

## Model Guidelines

1. **Domain Rules**
   - Always use core constants for domain values
   - Never hardcode status values or types
   - Implement validation using domain constraints

2. **Type Safety**
   - Use enums instead of strings for fixed values
   - Add type hints to all properties
   - Validate inputs against domain types

3. **Relationships**
   - Define clear ownership of relationships
   - Use appropriate cascade behaviors
   - Document relationship constraints

4. **Validation**
   - Validate at the model level
   - Use SQLAlchemy events for complex validation
   - Reference domain constraints

## Common Tasks

### Adding a New Model

1. Define domain constants in `core_constants.py`
2. Create model class with appropriate mixins
3. Add relationships and constraints
4. Update database migrations

```python
from models.core_constants import ItemStatus
from models.base import Base
from models.mixins import TimestampMixin

class NewModel(Base, TimestampMixin):
    __tablename__ = 'new_models'
    status = Column(String, default=ItemStatus.DRAFT)
```

### Updating Domain Rules

1. Modify `core_constants.py`
2. Update affected models
3. Add migrations if needed
4. Update tests

## Testing

- Test against domain constants
- Verify state transitions
- Check constraint enforcement
- Test relationship behaviors

```python
def test_valid_status():
    item = CatalogItem(title="Test")
    assert item.status == ItemStatus.DRAFT
    
    with pytest.raises(ValueError):
        item.status = "invalid_status"
```

## Version History
- 1.0.0: Initial version
- 1.1.0: Added domain-driven design with core constants
