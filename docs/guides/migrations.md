# Database Migration Guide

## Overview

Marian uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations, with additional tooling to ensure migrations stay in sync with our configuration-based schema definitions.

## Quick Start

```bash
# Generate a new migration
./scripts/manage_migrations.py generate "add user preferences table"

# Apply pending migrations
./scripts/manage_migrations.py apply

# View migration history
./scripts/manage_migrations.py history

# Show pending migrations
./scripts/manage_migrations.py pending

# Validate schema changes
./scripts/manage_migrations.py validate
```

## Migration Workflow

1. Make changes to your SQLAlchemy models
2. Update the schema configuration in `config/schema.yaml`
3. Run `./scripts/manage_migrations.py validate` to ensure changes are valid
4. Generate a migration with `./scripts/manage_migrations.py generate "description"`
5. Review the generated migration in `alembic/versions/`
6. Apply the migration with `./scripts/manage_migrations.py apply`

## Configuration Integration

Our migration system is integrated with our configuration-based schema definitions:

1. **Schema Validation**: Before generating migrations, the system validates that your model changes match the schema configuration.

2. **Type Consistency**: The system ensures that column types in your models match those defined in the configuration.

3. **Configuration as Source of Truth**: The schema configuration in `config/schema.yaml` serves as the source of truth for your database schema.

## Best Practices

1. **One Change per Migration**: Each migration should handle one logical change to make it easier to review and roll back if needed.

2. **Descriptive Messages**: Use clear, descriptive messages for your migrations that explain what they do.

3. **Review Generated Migrations**: Always review auto-generated migrations before applying them.

4. **Test Migrations**: Test migrations on a development database before applying them to production.

5. **Version Control**: Always commit migrations with their corresponding model and configuration changes.

## Troubleshooting

### Migration Conflicts

If you encounter migration conflicts (multiple heads):

1. Run `./scripts/manage_migrations.py history` to see the current state
2. Create a new migration to merge the heads:
   ```bash
   ./scripts/manage_migrations.py generate "merge heads" --empty
   ```
3. Edit the migration to include both parent revisions
4. Apply the migration to resolve the conflict

### Failed Migrations

If a migration fails:

1. Check the error message for details
2. Roll back to the previous revision if needed
3. Fix any issues in your models or configuration
4. Generate a new migration with the fixes

## Migration Directory Structure

```
alembic/
├── versions/          # Migration version files
├── env.py            # Environment configuration
├── script.py.mako    # Migration template
└── README           # Alembic readme
```

## Related Documentation

- [Schema Configuration Guide](schema_configuration.md)
- [Database Design ADR](../adr/0001-database-design.md)
- [Configuration-Based Schema ADR](../adr/0005-configuration-based-schema-definitions.md)
