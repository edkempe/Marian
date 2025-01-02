# Database Schema Management Process

The single source of truth for our database schema is `/config/schema.yaml`. This file defines all table structures, field types, sizes, defaults, validation rules, and relationships. To maintain schema consistency:

1. Make ALL schema changes in schema.yaml first
2. Run `python3 scripts/generate_schema_constants.py` to update shared_lib/schema_constants.py
3. Run `python3 scripts/generate_models.py` to update SQLAlchemy models in /models
4. Generate new Alembic migration with `alembic revision --autogenerate`
5. Verify migration matches schema.yaml expectations
6. Apply changes with `alembic upgrade head`
7. Test API endpoints to validate changes

## IMPORTANT RULES:
- Never modify models, constants, or migrations directly. All changes must start with schema.yaml
- Use 'analysis_metadata' instead of 'metadata' as field names (SQLAlchemy reserved word)
- Always use JSON type for array/list fields in SQLite (e.g., 'labels', 'categories', 'key_points')
- Store arrays as JSON strings: empty array = "[]", empty object = "{}"
- Validate JSON fields during serialization/deserialization

## Scripts:
- `scripts/generate_schema_constants.py`: Generates constants from schema.yaml
- `scripts/generate_models.py`: Generates SQLAlchemy models from schema.yaml

## Files:
- `config/schema.yaml`: Source of truth for database schema
- `shared_lib/schema_constants.py`: Generated constants
- `models/*.py`: Generated SQLAlchemy models
- `migrations/versions/*.py`: Generated Alembic migrations

For questions or schema changes, contact [your-team-lead].
