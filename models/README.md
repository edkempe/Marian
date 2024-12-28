# Models Directory

**Version:** 1.0.0  
**Status:** Authoritative

> Core SQLAlchemy models defining the database schema and business logic for the Marian system.

## Quick Reference
```python
# Import models
from models.user import User
from models.document import Document
from models.catalog import Catalog

# Create new instance
user = User(
    username="example",
    email="user@example.com"
)

# Query example
docs = Document.query.filter_by(
    owner_id=user.id
).all()

# Relationship example
user.documents  # Access user's documents
doc.owner      # Access document's owner
```

Common operations:
- Import models
- Create instances
- Query relationships
- Access properties

## Overview
- **Purpose**: Database schema and ORM
- **Stability**: Stable
- **Maintenance**: Active
- **Python**: SQLAlchemy models

---

## Directory Structure
```
/models/
├── README.md          # This guide
├── __init__.py        # Model initialization
├── base.py           # Base model class
├── user.py          # User model
├── document.py      # Document model
├── catalog.py       # Catalog model
└── mixins/          # Shared model mixins
    ├── __init__.py
    └── timestamp.py
```

## Core Components

1. **Base Model**
   - Purpose: Common model functionality
   - Location: `base.py`
   - Usage:
     ```python
     from models.base import Base
     
     class MyModel(Base):
         __tablename__ = 'my_model'
     ```

2. **Model Mixins**
   - Purpose: Reusable model features
   - Location: `mixins/`
   - Available mixins:
     ```python
     from models.mixins import TimestampMixin
     
     class MyModel(Base, TimestampMixin):
         __tablename__ = 'my_model'
         # Automatically gets created_at and updated_at
     ```
   - TimestampMixin:
     - `created_at`: When record was created
     - `updated_at`: When record was last updated
     - Auto-updates on save

3. **User Model**
   - Purpose: User management
   - Location: `user.py`
   - Key fields:
     - `id`: Primary key
     - `username`: Unique username
     - `email`: User's email
     - `documents`: Related documents

4. **Document Model**
   - Purpose: Document storage
   - Location: `document.py`
   - Key fields:
     - `id`: Primary key
     - `title`: Document title
     - `content`: Document content
     - `owner_id`: User reference

5. **Catalog Model**
   - Purpose: Document organization
   - Location: `catalog.py`
   - Key fields:
     - `id`: Primary key
     - `name`: Catalog name
     - `documents`: Related documents

---

## Development Guidelines

### Adding New Models
1. Create new file: `models/new_model.py`
2. Import base and dependencies:
   ```python
   from sqlalchemy import Column, Integer, String
   from models.base import Base
   ```
3. Define model class:
   ```python
   class NewModel(Base):
       __tablename__ = 'new_model'
       
       id = Column(Integer, primary_key=True)
       name = Column(String(255), nullable=False)
   ```
4. Add to `__init__.py`:
   ```python
   from models.new_model import NewModel
   ```

### Best Practices

1. **Model Design**
   - Use meaningful names
   - Document all fields
   - Add type hints
   - Include docstrings

2. **Relationships**
   - Define both sides
   - Set cascades properly
   - Consider lazy loading
   - Add indexes

3. **Validation**
   - Add constraints
   - Use validators
   - Handle errors
   - Test edge cases

---

## Common Tasks

### Database Operations
```python
# Create tables
Base.metadata.create_all(engine)

# Drop tables
Base.metadata.drop_all(engine)

# Get table names
Base.metadata.tables.keys()
```

### Model Operations
```python
# Create instance
user = User(username="test")

# Save to database
db.session.add(user)
db.session.commit()

# Query
User.query.filter_by(username="test").first()

# Update
user.username = "new_name"
db.session.commit()

# Delete
db.session.delete(user)
db.session.commit()
```

---

## Related Documentation
- Parent: `../README.md` - Project root
- `../docs/database.md` - Database configuration
- `../migrations/README.md` - Database migrations

## Version History
- 1.0.0: Initial model documentation
