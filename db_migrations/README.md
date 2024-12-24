# Database Migrations

This directory contains database migration files for the Marian Catalog system. Each migration is versioned and applied sequentially to maintain database schema consistency.

## Migration Files

- `V1__initial_schema.sql`: Initial catalog schema with core tables
- `V2__add_status_and_tracking.sql`: Adds status and user tracking fields

## Schema Version Control

The `schema_versions` table tracks all applied migrations:
- `version`: Sequential version number
- `migration_id`: Unique identifier for the migration
- `description`: Brief description of changes
- `applied_at`: Timestamp when migration was applied
- `checksum`: Hash to verify migration integrity

## Adding New Migrations

1. Create a new SQL file with the format `V{N}__{description}.sql`
2. Include version update in schema_versions table
3. Add migration details to this README
4. Test migration on development database
5. Apply migration to production

## Best Practices

1. Migrations should be forward-only (no rollbacks)
2. Each migration should be atomic and independent
3. Use appropriate constraints and indexes
4. Document all changes in this README
5. Test migrations thoroughly before production

## Current Schema Version: 2

Latest changes:
- Added status field to catalog_items
- Added user tracking fields
- Added corresponding indexes
