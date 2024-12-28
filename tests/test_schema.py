"""Test suite for database schema validation.

This module ensures that our SQLAlchemy models match the database schema
defined in our migrations. This prevents schema drift and catches model-migration
mismatches early.

Key validations:
1. Table names match between models and migrations
2. Column names, types, and constraints match
3. Indexes match
4. Foreign key relationships match

Note:
    The schema validation is implemented as a session-scoped fixture that runs
    before any other tests. If the schema validation fails, all other tests
    will be skipped as they cannot be trusted with an invalid schema.
"""

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
import os
import sys
from typing import Dict, Any, List, Set
from alembic import command, op
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import Base
from models.catalog import CatalogItem, Tag, CatalogTag, ItemRelationship
from models.asset_catalog import AssetCatalogItem, AssetCatalogTag, AssetDependency
from models.email import Email
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel

# Import migrations
from migrations.versions.initial_schema import upgrade as initial_upgrade
from migrations.versions.add_cc_bcc_fields import upgrade as cc_bcc_upgrade

def get_table_details(inspector: Any, table_name: str) -> Dict[str, Any]:
    """Get comprehensive details about a table's schema."""
    columns = {}
    for col in inspector.get_columns(table_name):
        columns[col['name']] = {
            'type': str(col['type']),
            'nullable': col['nullable'],
            'default': str(col['default']) if col['default'] is not None else None,
            'primary_key': col.get('primary_key', False)
        }
    
    return {
        'columns': columns,
        'primary_keys': set(col['name'] for col in inspector.get_columns(table_name) 
                          if col.get('primary_key')),
        'foreign_keys': inspector.get_foreign_keys(table_name),
        'indexes': inspector.get_indexes(table_name),
        'unique_constraints': inspector.get_unique_constraints(table_name)
    }

def assert_schema_equal(migration_inspector: Any, model_inspector: Any):
    """Assert that two database schemas are equivalent."""
    migration_tables = set(migration_inspector.get_table_names())
    model_tables = set(model_inspector.get_table_names())
    
    assert migration_tables == model_tables, \
        f"Table mismatch:\nMigration tables: {migration_tables}\nModel tables: {model_tables}"
    
    for table in migration_tables:
        migration_details = get_table_details(migration_inspector, table)
        model_details = get_table_details(model_inspector, table)
        
        # Compare columns
        assert migration_details['columns'] == model_details['columns'], \
            f"Column mismatch in table {table}:\nMigration: {migration_details['columns']}\nModel: {model_details['columns']}"
        
        # Compare primary keys
        assert migration_details['primary_keys'] == model_details['primary_keys'], \
            f"Primary key mismatch in table {table}:\nMigration: {migration_details['primary_keys']}\nModel: {model_details['primary_keys']}"
        
        # Compare foreign keys (ignoring implementation-specific details)
        mig_fks = [{k: v for k, v in fk.items() if k in ('referred_table', 'constrained_columns', 'referred_columns')}
                   for fk in migration_details['foreign_keys']]
        mod_fks = [{k: v for k, v in fk.items() if k in ('referred_table', 'constrained_columns', 'referred_columns')}
                   for fk in model_details['foreign_keys']]
        assert mig_fks == mod_fks, \
            f"Foreign key mismatch in table {table}:\nMigration: {mig_fks}\nModel: {mod_fks}"
        
        # Compare indexes (ignoring implementation-specific details)
        for midx in migration_details['indexes']:
            assert any(
                midx['name'] == idx['name'] and
                midx['unique'] == idx['unique'] and
                set(midx['columns']) == set(idx['columns'])
                for idx in model_details['indexes']
            ), f"Index mismatch in table {table}:\nMigration index: {midx}\nModel indexes: {model_details['indexes']}"

@pytest.fixture(scope="session", autouse=True)
def validate_schema(request):
    """Fixture to validate schema before any tests run.
    
    This fixture runs automatically before any tests and will cause all tests
    to fail if the schema validation fails.
    """
    # Create DB from migrations
    migration_engine = create_engine('sqlite:///:memory:')
    
    # Create migration context
    with migration_engine.begin() as conn:
        context = MigrationContext.configure(
            conn,
            opts={
                'target_metadata': Base.metadata,
                'include_schemas': True
            }
        )
        
        # Create operations object
        operations = Operations(context)
        op._proxy = operations
        
        # Run migrations in context
        with context.begin_transaction():
            initial_upgrade()
            cc_bcc_upgrade()
    
    # Create DB from models
    model_engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(model_engine)
    
    # Compare schemas
    migration_inspector = inspect(migration_engine)
    model_inspector = inspect(model_engine)
    
    try:
        assert_schema_equal(migration_inspector, model_inspector)
    except AssertionError as e:
        pytest.exit(f"Schema validation failed:\n{str(e)}")
        
    def cleanup():
        migration_engine.dispose()
        model_engine.dispose()
    
    request.addfinalizer(cleanup)

def test_schema_validation_runs():
    """Simple test to ensure schema validation fixture runs."""
    assert True  # If we get here, schema validation passed

if __name__ == '__main__':
    pytest.main([__file__])
