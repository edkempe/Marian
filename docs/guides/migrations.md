# Database Schema Management Guide

## Overview
Jexi uses a configuration-driven approach for database schema management. The schema is defined in `schema.yaml` and automatically generated into SQLAlchemy models and constants.

## Schema Management Flow

1. **Define Schema**
   - Edit `config/schema.yaml`
   - Define tables, columns, and relationships
   - All tables use the single 'main' database

2. **Generate Code**
   ```bash
   # Generate schema constants
   python scripts/generate_schema_constants.py
   
   # Generate models
   python scripts/generate_models.py
   ```

3. **Initialize Database**
   ```bash
   # Create or rebuild database
   python scripts/rebuild_db.py
   
   # Verify schema
   python scripts/verify_database_schema.py
   ```

## Directory Structure
```
jexi/
├── config/
│   └── schema.yaml          # Schema definition
├── models/
│   ├── base.py             # Base model class
│   ├── email_message.py    # Generated models
│   └── registry.py         # Model registry
├── scripts/
│   ├── generate_models.py        # Model generation
│   ├── generate_schema_constants.py  # Constants generation
│   ├── rebuild_db.py            # Database initialization
│   └── verify_database_schema.py # Schema verification
└── data/
    └── jexi.db            # Main database
```

## Making Schema Changes

1. Update `schema.yaml`:
   ```yaml
   email:
     database: "main"
     columns:
       new_field:
         type: string
         size: 100
   ```

2. Regenerate code:
   ```bash
   python scripts/generate_schema_constants.py
   python scripts/generate_models.py
   ```

3. Rebuild database:
   ```bash
   python scripts/rebuild_db.py
   python scripts/verify_database_schema.py
   ```

## Best Practices

1. **Schema Changes**
   - Always update schema.yaml first
   - Use the generate_* scripts to update code
   - Verify changes with verify_database_schema.py

2. **Database Management**
   - Keep regular backups of jexi.db
   - Use transactions for data modifications
   - Follow table naming conventions

3. **Testing**
   - Use test database for development
   - Write tests for new schema features
   - Verify schema changes in test environment first

## References
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/20/)
- [SQLite Documentation](https://sqlite.org/docs.html)
