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
from sqlalchemy import create_engine, inspect, text, Column, String, Text, DateTime, Boolean, Integer, Float, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
import os
import sys
from typing import Dict, Any, List, Set, Tuple
from alembic import command, op
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations
from models.email import EMAIL_DEFAULTS

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import Base
from models.catalog import CatalogItem, Tag, CatalogTag, ItemRelationship
from models.asset_catalog import AssetCatalogItem, AssetCatalogTag, AssetDependency
from models.email import Email
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel

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
    
    # Check for extra tables in either direction
    extra_in_migrations = migration_tables - model_tables
    extra_in_models = model_tables - migration_tables
    assert not extra_in_migrations, f"Tables in migrations but not in models: {extra_in_migrations}"
    assert not extra_in_models, f"Tables in models but not in migrations: {extra_in_models}"
    
    # Now check tables that exist in both
    common_tables = migration_tables & model_tables
    for table in common_tables:
        migration_details = get_table_details(migration_inspector, table)
        model_details = get_table_details(model_inspector, table)
        
        # Get column sets
        migration_columns = set(migration_details['columns'].keys())
        model_columns = set(model_details['columns'].keys())
        
        # Check for extra columns in either direction
        extra_in_migration = migration_columns - model_columns
        extra_in_model = model_columns - migration_columns
        assert not extra_in_migration, \
            f"Columns in migration but not in model for table {table}: {extra_in_migration}"
        assert not extra_in_model, \
            f"Columns in model but not in migration for table {table}: {extra_in_model}"
        
        # For columns that exist in both, compare their properties
        common_columns = migration_columns & model_columns
        for column in common_columns:
            assert migration_details['columns'][column] == model_details['columns'][column], \
                f"Column properties mismatch in table {table}, column {column}:\n" \
                f"Migration: {migration_details['columns'][column]}\n" \
                f"Model: {model_details['columns'][column]}"
        
        # Compare primary keys
        assert migration_details['primary_keys'] == model_details['primary_keys'], \
            f"Primary key mismatch in table {table}:\nMigration: {migration_details['primary_keys']}\nModel: {model_details['primary_keys']}"
        
        # Compare foreign keys (ignoring implementation-specific details)
        mig_fks = [{k: v for k, v in fk.items() if k in ('referred_table', 'constrained_columns', 'referred_columns')}
                   for fk in migration_details['foreign_keys']]
        mod_fks = [{k: v for k, v in fk.items() if k in ('referred_table', 'constrained_columns', 'referred_columns')}
                   for fk in model_details['foreign_keys']]
        
        # Check for missing foreign keys in either direction
        assert len(mig_fks) == len(mod_fks), \
            f"Number of foreign keys mismatch in table {table}:\n" \
            f"Migration ({len(mig_fks)}): {mig_fks}\n" \
            f"Model ({len(mod_fks)}): {mod_fks}"
        
        # Check that each foreign key in migration exists in model
        for mig_fk in mig_fks:
            assert any(mig_fk == mod_fk for mod_fk in mod_fks), \
                f"Foreign key in migration not found in model for table {table}:\n" \
                f"Migration FK: {mig_fk}\n" \
                f"Model FKs: {mod_fks}"
        
        # Compare indexes (ignoring implementation-specific details)
        for midx in migration_details['indexes']:
            assert any(
                midx['name'] == idx['name'] and
                midx['unique'] == idx['unique'] and
                set(midx['columns']) == set(idx['columns'])
                for idx in model_details['indexes']
            ), f"Index mismatch in table {table}:\nMigration index: {midx}\nModel indexes: {model_details['indexes']}"

def find_code_references(table_name: str, column_name: str = None) -> bool:
    """Search for references to a table or column in the codebase."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Search patterns
    patterns = []
    if column_name:
        # Common ways to reference columns in code
        patterns.extend([
            f"{table_name}.{column_name}",
            f"'{column_name}'",
            f'"{column_name}"',
            f"Column('{column_name}'",
            f'Column("{column_name}"'
        ])
    else:
        # Common ways to reference tables in code
        patterns.extend([
            f"'{table_name}'",
            f'"{table_name}"',
            f"class {table_name}",
            f"__tablename__ = '{table_name}'",
            f'__tablename__ = "{table_name}"'
        ])
    
    # Search for any of these patterns
    for pattern in patterns:
        result = os.system(f'grep -r "{pattern}" {project_root}/models {project_root}/services {project_root}/src > /dev/null 2>&1')
        if result == 0:  # Found a match
            return True
    
    return False

def check_unused_schema_elements(inspector: Any) -> Tuple[List[str], Dict[str, List[str]]]:
    """Check for tables and columns that aren't referenced in the code.
    
    Returns:
        Tuple of (unused_tables, unused_columns_by_table)
    """
    unused_tables = []
    unused_columns_by_table = {}
    
    for table_name in inspector.get_table_names():
        # Check if table is referenced
        if not find_code_references(table_name):
            unused_tables.append(table_name)
            continue
        
        # Check each column
        unused_columns = []
        for col in inspector.get_columns(table_name):
            col_name = col['name']
            if not find_code_references(table_name, col_name):
                unused_columns.append(col_name)
        
        if unused_columns:
            unused_columns_by_table[table_name] = unused_columns
    
    return unused_tables, unused_columns_by_table

def print_schema_usage_report(migration_inspector: Any):
    """Generate schema usage report data."""
    unused_tables, unused_columns = check_unused_schema_elements(migration_inspector)
    
    report_data = {
        'unused_tables': unused_tables,
        'unused_columns': unused_columns
    }
    
    from .reporting import ReportManager
    report_manager = ReportManager()
    report_manager.write_schema_report(report_data)

@pytest.fixture(scope="session", autouse=True)
def validate_schema():
    """Validate that our SQLAlchemy models match the migrations."""
    # Create in-memory database for migration
    migration_engine = create_engine('sqlite:///:memory:')
    
    # Create migration context
    with migration_engine.begin() as conn:
        context = MigrationContext.configure(conn)
        op._proxy = Operations(context)
        
        # Apply migrations in order
        with context.begin_transaction():
            # Email-related tables
            op.create_table(
                'emails',
                Column('id', String(100), nullable=False),
                Column('threadId', String(100), nullable=True),
                Column('subject', String(500), nullable=True, server_default=EMAIL_DEFAULTS['EMAIL_SUBJECT']),
                Column('body', Text(), nullable=True),
                Column('date', DateTime(timezone=True), nullable=True),
                Column('labelIds', String(500), nullable=True),
                Column('snippet', Text(), nullable=True),
                Column('from', String(200), nullable=True),
                Column('to', String(200), nullable=True),
                Column('has_attachments', Boolean(), nullable=True, server_default=str(EMAIL_DEFAULTS['HAS_ATTACHMENTS'])),
                Column('cc', Text(), server_default="''''''"),
                Column('bcc', Text(), server_default="''''''"),
                Column('full_api_response', Text(), server_default=EMAIL_DEFAULTS['API_RESPONSE']),
                PrimaryKeyConstraint('id')
            )
            
            op.create_table(
                'email_analysis',
                Column('id', Integer(), primary_key=True),
                Column('email_id', String(100), nullable=False),
                Column('thread_id', String(100)),
                Column('analysis_date', DateTime(), nullable=True),
                Column('analyzed_date', DateTime(), nullable=False),
                Column('prompt_version', Text(), nullable=False),
                Column('summary', Text(), nullable=False),
                Column('category', Text(), nullable=False),
                Column('priority_score', Integer(), nullable=False),
                Column('priority_reason', Text(), nullable=False),
                Column('action_needed', Boolean(), nullable=False),
                Column('action_type', Text(), nullable=False),
                Column('action_deadline', Text(), nullable=True),
                Column('key_points', Text(), nullable=False),
                Column('people_mentioned', Text(), nullable=False),
                Column('links_found', Text(), nullable=False),
                Column('links_display', Text(), nullable=False),
                Column('project', Text(), nullable=True),
                Column('topic', Text(), nullable=True),
                Column('ref_docs', Text(), nullable=True),
                Column('sentiment', Text(), nullable=False),
                Column('confidence_score', Float(), nullable=False),
                Column('created_at', DateTime(), nullable=False),
                Column('updated_at', DateTime(), nullable=False),
                ForeignKeyConstraint(['email_id'], ['emails.id']),
                PrimaryKeyConstraint('id')
            )
            
            op.create_table(
                'gmail_labels',
                Column('id', String(100), nullable=False),
                Column('name', String(100), nullable=False),
                Column('type', String(50), nullable=False),
                Column('is_active', Boolean(), nullable=False, default=True),
                Column('first_seen_at', DateTime(), nullable=False,
                         server_default=func.current_timestamp()),
                Column('last_seen_at', DateTime(), nullable=False,
                         server_default=func.current_timestamp()),
                Column('deleted_at', DateTime()),
                PrimaryKeyConstraint('id')
            )

            # Catalog-related tables
            op.create_table(
                'tags',
                Column('id', Integer(), nullable=False, autoincrement=True),
                Column('name', String(100), nullable=False),
                Column('description', Text(), nullable=True),
                Column('deleted', Boolean(), nullable=False, default=False),
                Column('archived_date', Integer(), nullable=True),
                Column('created_date', Integer(), nullable=False),
                Column('modified_date', Integer(), nullable=False),
                PrimaryKeyConstraint('id')
            )

            op.create_table(
                'catalog_items',
                Column('id', Integer(), nullable=False, autoincrement=True),
                Column('title', String(255), nullable=False),
                Column('description', Text(2000), nullable=True),
                Column('content', Text(), nullable=True),
                Column('source', String(), nullable=True),
                Column('status', String(), nullable=False, server_default='draft'),
                Column('deleted', Boolean(), nullable=False, default=False),
                Column('archived_date', Integer(), nullable=True),
                Column('created_date', Integer(), nullable=False),
                Column('modified_date', Integer(), nullable=False),
                Column('item_info', JSON(), nullable=True),
                PrimaryKeyConstraint('id')
            )

            op.create_table(
                'catalog_tags',
                Column('catalog_item_id', Integer(), nullable=False),
                Column('tag_id', Integer(), nullable=False),
                ForeignKeyConstraint(['catalog_item_id'], ['catalog_items.id']),
                ForeignKeyConstraint(['tag_id'], ['tags.id']),
                PrimaryKeyConstraint('catalog_item_id', 'tag_id')
            )

            op.create_table(
                'item_relationships',
                Column('id', Integer(), primary_key=True, autoincrement=True),
                Column('source_id', Integer(), nullable=False),
                Column('target_id', Integer(), nullable=False),
                Column('relationship_type', String(50), nullable=False),
                Column('created_date', Integer(), nullable=False),
                Column('relationship_info', JSON(), nullable=True),
                ForeignKeyConstraint(['source_id'], ['catalog_items.id']),
                ForeignKeyConstraint(['target_id'], ['catalog_items.id'])
            )

            # Asset catalog tables
            op.create_table(
                'asset_catalog_items',
                Column('id', Integer(), nullable=False, autoincrement=True),
                Column('title', String(255), nullable=False),
                Column('description', Text(2000), nullable=True),
                Column('content', Text(), nullable=True),
                Column('source', String(), nullable=True),
                Column('status', String(), nullable=False, server_default='draft'),
                Column('deleted', Boolean(), nullable=False, default=False),
                Column('archived_date', Integer(), nullable=True),
                Column('created_date', Integer(), nullable=False),
                Column('modified_date', Integer(), nullable=False),
                Column('item_info', JSON(), nullable=True),
                PrimaryKeyConstraint('id')
            )

            op.create_table(
                'asset_catalog_tags',
                Column('asset_id', Integer(), nullable=False),
                Column('tag_id', Integer(), nullable=False),
                ForeignKeyConstraint(['asset_id'], ['asset_catalog_items.id']),
                ForeignKeyConstraint(['tag_id'], ['tags.id']),
                PrimaryKeyConstraint('asset_id', 'tag_id')
            )

            op.create_table(
                'asset_dependencies',
                Column('source_id', Integer(), nullable=False),
                Column('target_id', Integer(), nullable=False),
                Column('dependency_type', String(50), nullable=False),
                Column('metadata', Text(), nullable=True),
                ForeignKeyConstraint(['source_id'], ['asset_catalog_items.id'], ondelete='CASCADE'),
                ForeignKeyConstraint(['target_id'], ['asset_catalog_items.id'], ondelete='CASCADE'),
                PrimaryKeyConstraint('source_id', 'target_id', 'dependency_type')
            )
    
    # Create another in-memory database for models
    model_engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(model_engine)
    
    # Compare schemas
    migration_inspector = inspect(migration_engine)
    model_inspector = inspect(model_engine)
    
    # First do the strict validation
    assert_schema_equal(migration_inspector, model_inspector)
    
    # Then print the usage report
    print_schema_usage_report(migration_inspector)

def test_schema_validation_runs():
    """Simple test to ensure schema validation fixture runs."""
    assert True

if __name__ == '__main__':
    pytest.main([__file__])
