# Jexi Models

**Version:** 1.2.0
**Status:** Authoritative

> SQLAlchemy models and domain constants for the Jexi project.

## Revision History
1.0.0 (2024-12-31) @dev
- Initial models documentation
- Added data model specifications
- Added validation rules

## Data Flow Hierarchy

This package follows a strict data flow hierarchy to ensure consistency:

```
External APIs (Gmail, etc.)
         ↓
    core_constants.py
         ↓
    models/*.py
         ↓
    Database Schema
```

1. **External APIs are Source of Truth**
   - API documentation referenced in model docstrings
   - Field types match API specifications
   - Constraints reflect API requirements
   Example: `Email.id` uses string type to match Gmail API

2. **Domain Constants Define Rules**
   - Type-safe enums for valid values
   - Business constraints and validations
   - State transition rules
   Example: `AssetType`, `ItemStatus` enums

3. **Models Implement API Contracts**
   - Match API data structures
   - Add domain-specific fields
   - Enforce data integrity
   Example: `Email` model mirrors Gmail message format

4. **Database Schema Follows Models**
   - Generated from SQLAlchemy models
   - Validated by schema tests
   - Changes require migrations
   Example: `emails` table matches `Email` model

## Quick Reference

```python
from models.core_constants import AssetType, ItemStatus
from models import CatalogItem, Tag, Email

# Email model matches Gmail API
email = Email(
    id="msg123",  # String ID from Gmail
    thread_id="thread123",
    labels="INBOX,UNREAD"
)

# Catalog items use domain constants
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

1. **API Alignment**
   - Match external API types exactly
   - Document API source in docstrings
   - Preserve API field names
   - Add domain fields thoughtfully

2. **Type Safety**
   - Use API-specified types
   - Add type hints matching API
   - Validate against API constraints
   - Use enums for domain values

3. **Relationships**
   - Define clear ownership
   - Use appropriate cascades
   - Document constraints
   - Consider API relationships

4. **Validation**
   - Validate at model level
   - Use events for complex rules
   - Check API constraints
   - Preserve data integrity

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
- 1.2.0 (2024-12-28): Updated to API-first hierarchy
  - Refactored models to follow API data structures
  - Added domain-specific fields and validations
  - Improved documentation and examples
- 1.1.0 (2024-12-27): Added domain-driven design
  - Introduced core constants for domain rules
  - Added type-safe enums for valid values
  - Enhanced validation and constraints
- 1.0.0 (2024-12-26): Initial version
  - Created base model structure
  - Added SQLAlchemy integration
  - Set up basic validation
