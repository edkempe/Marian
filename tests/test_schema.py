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

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import Base
from models.catalog import CatalogItem, Tag, CatalogTag, ItemRelationship
from models.asset_catalog import AssetCatalogItem, AssetCatalogTag, AssetDependency
from models.email import Email
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel

# Import latest migration
from migrations.versions.20241223_01_initial_schema import upgrade as initial_upgrade
from migrations.versions.20241223_add_cc_bcc_fields import upgrade as cc_bcc_upgrade

def get_table_details(inspector: Any, table_name: str) -> Dict[str, Any]:
    """Get comprehensive details about a table's schema.
    
    Args:
        inspector: SQLAlchemy inspector instance
        table_name: Name of the table to inspect
        
    Returns:
        Dict containing table schema details:
        - columns: List of column definitions
        - primary_keys: Set of primary key column names
        - foreign_keys: List of foreign key constraints
        - indexes: List of index definitions
        - unique_constraints: List of unique constraints
    """
    return {
        'columns': {
            c['name']: {
                'type': str(c['type']),
                'nullable': c['nullable'],
                'default': str(c['default']) if c['default'] is not None else None,
                'primary_key': c.get('primary_key', False)
            }
            for c in inspector.get_columns(table_name)
        },
        'primary_keys': set(
            pk['name'] 
            for pk in inspector.get_pk_constraint(table_name)['constrained_columns']
        ),
        'foreign_keys': [
            {
                'referred_table': fk['referred_table'],
                'referred_columns': fk['referred_columns'],
                'constrained_columns': fk['constrained_columns']
            }
            for fk in inspector.get_foreign_keys(table_name)
        ],
        'indexes': [
            {
                'name': idx['name'],
                'unique': idx['unique'],
                'columns': idx['column_names']
            }
            for idx in inspector.get_indexes(table_name)
        ],
        'unique_constraints': [
            {
                'name': uc['name'],
                'columns': uc['column_names']
            }
            for uc in inspector.get_unique_constraints(table_name)
        ]
    }

def assert_schema_equal(migration_inspector: Any, model_inspector: Any):
    """Assert that two database schemas are equivalent.
    
    Args:
        migration_inspector: Inspector for migration-created schema
        model_inspector: Inspector for model-created schema
        
    Raises:
        AssertionError: If schemas don't match, with detailed diff
    """
    migration_tables = set(migration_inspector.get_table_names())
    model_tables = set(model_inspector.get_table_names())
    
    # Compare table names
    assert migration_tables == model_tables, \
        f"Table mismatch:\nMigration tables: {migration_tables}\nModel tables: {model_tables}"
    
    # Compare table details
    for table in migration_tables:
        migration_details = get_table_details(migration_inspector, table)
        model_details = get_table_details(model_inspector, table)
        
        # Compare columns
        assert migration_details['columns'] == model_details['columns'], \
            f"Column mismatch in table {table}:\nMigration: {migration_details['columns']}\nModel: {model_details['columns']}"
        
        # Compare primary keys
        assert migration_details['primary_keys'] == model_details['primary_keys'], \
            f"Primary key mismatch in table {table}:\nMigration: {migration_details['primary_keys']}\nModel: {model_details['primary_keys']}"
        
        # Compare foreign keys (order independent)
        assert len(migration_details['foreign_keys']) == len(model_details['foreign_keys']), \
            f"Foreign key count mismatch in table {table}"
        for mfk in migration_details['foreign_keys']:
            assert any(
                mfk['referred_table'] == fk['referred_table'] and
                set(mfk['referred_columns']) == set(fk['referred_columns']) and
                set(mfk['constrained_columns']) == set(fk['constrained_columns'])
                for fk in model_details['foreign_keys']
            ), f"Foreign key mismatch in table {table}:\nMigration FK: {mfk}\nModel FKs: {model_details['foreign_keys']}"
        
        # Compare indexes (order independent)
        assert len(migration_details['indexes']) == len(model_details['indexes']), \
            f"Index count mismatch in table {table}"
        for midx in migration_details['indexes']:
            assert any(
                midx['unique'] == idx['unique'] and
                set(midx['columns']) == set(idx['columns'])
                for idx in model_details['indexes']
            ), f"Index mismatch in table {table}:\nMigration index: {midx}\nModel indexes: {model_details['indexes']}"

@pytest.fixture(scope="session", autouse=True)
def validate_schema():
    """Fixture to validate schema before any tests run.
    
    This fixture runs automatically before any tests and will cause all tests
    to fail if the schema validation fails.
    """
    # Create DB from migrations
    migration_engine = create_engine('sqlite:///:memory:')
    with migration_engine.begin() as conn:
        # Run all migrations in order
        initial_upgrade(conn)
        cc_bcc_upgrade(conn)
    
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

if __name__ == '__main__':
    pytest.main([__file__])
