# Marian Database Migrations

**Version:** 1.0.0  
**Status:** Authoritative

> Database migrations for the Marian project.

## Migration Hierarchy

Migrations implement our data flow hierarchy:

```
External APIs → Models → Database Migrations
```

Each migration ensures database schema matches:
1. API data types and constraints
2. Model definitions
3. Business rules

## Migration Guidelines

### 1. Type Alignment
- Match API data types exactly
- Use appropriate column types
- Document type decisions
Example: Email IDs are strings (VARCHAR) to match Gmail API

### 2. Schema Evolution
- Preserve data during changes
- Add migrations for model changes
- Test both upgrade and downgrade
Example: Changing ID type from INTEGER to VARCHAR

### 3. Constraints
- Match API constraints
- Enforce model rules
- Add appropriate indexes
Example: Required fields, foreign keys

## Current Migrations

1. **Initial Schema** (`initial_schema.py`)
   - Base tables and relationships
   - Core field definitions
   - Primary keys and indexes

2. **CC/BCC Fields** (`add_cc_bcc_fields.py`)
   - Added CC/BCC address fields
   - Text type for multiple addresses
   - Default empty string

3. **Email and Label Fields** (`add_email_and_label_fields.py`)
   - Added recipient address
   - Added full API response
   - Added label tracking fields

4. **Email ID Type Fix** (`fix_email_id_type.py`)
   - Changed email ID to string
   - Matches Gmail API format
   - Updated foreign key relationships

## Common Patterns

### Type Changes
```python
# Change column type
with op.batch_alter_table('emails') as batch_op:
    batch_op.alter_column('id',
                         type_=sa.String(100),
                         existing_type=sa.Integer)
```

### Adding Fields
```python
# Add new field
op.add_column('emails',
              sa.Column('full_api_response', sa.Text()))
```

### Constraints
```python
# Add constraint
op.create_foreign_key(
    'fk_analysis_email',
    'email_analysis', 'emails',
    ['email_id'], ['id']
)
```

## Version History
- 1.0.0: Initial version documenting API-first migrations
