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

def assert_column_equal(mcol, col, table, col_name):
    """Assert that two columns are equal."""
    # Compare types by string representation to handle SQLAlchemy type objects
    assert str(mcol['type']) == str(col['type']), \
        f"Column type mismatch in table {table}, column {col_name}:\nMigration: {mcol['type']}\nModel: {col['type']}"
    assert mcol['nullable'] == col['nullable'], \
        f"Column nullable mismatch in table {table}, column {col_name}:\nMigration: {mcol['nullable']}\nModel: {col['nullable']}"
    assert mcol['default'] == col['default'], \
        f"Column default mismatch in table {table}, column {col_name}:\nMigration: {mcol['default']}\nModel: {col['default']}"

def assert_schema_equal(migration_inspector, model_inspector):
    """Assert that two schemas are equal."""
    migration_tables = set(migration_inspector.get_table_names())
    model_tables = set(model_inspector.get_table_names())

    # Check tables match
    assert migration_tables == model_tables, \
        f"Tables don't match:\nMigration: {migration_tables}\nModel: {model_tables}"

    # For each table, check columns and indexes match
    for table in migration_tables:
        migration_details = {
            'columns': {c['name']: c for c in migration_inspector.get_columns(table)},
            'indexes': migration_inspector.get_indexes(table),
            'pk_constraint': migration_inspector.get_pk_constraint(table),
            'fk_constraints': migration_inspector.get_foreign_keys(table)
        }
        model_details = {
            'columns': {c['name']: c for c in model_inspector.get_columns(table)},
            'indexes': model_inspector.get_indexes(table),
            'pk_constraint': model_inspector.get_pk_constraint(table),
            'fk_constraints': model_inspector.get_foreign_keys(table)
        }

        # Check columns match
        assert migration_details['columns'].keys() == model_details['columns'].keys(), \
            f"Column names don't match in table {table}"

        for col_name, mcol in migration_details['columns'].items():
            col = model_details['columns'][col_name]
            assert_column_equal(mcol, col, table, col_name)

        # Check indexes match
        for midx in migration_details['indexes']:
            # SQLite may return column names in different order, so we need to sort them
            midx['column_names'] = sorted(midx['column_names'])
            assert any(
                idx['name'] == midx['name'] and
                idx['unique'] == midx['unique'] and
                sorted(idx['column_names']) == midx['column_names']
                for idx in model_details['indexes']
            ), f"Index mismatch in table {table}:\nMigration index: {midx}\nModel indexes: {model_details['indexes']}"

        # Check primary key matches
        mpk = migration_details['pk_constraint']
        pk = model_details['pk_constraint']
        assert set(mpk['constrained_columns']) == set(pk['constrained_columns']), \
            f"Primary key mismatch in table {table}:\nMigration: {mpk}\nModel: {pk}"

        # Check foreign keys match
        mfks = migration_details['fk_constraints']
        fks = model_details['fk_constraints']
        assert len(mfks) == len(fks), \
            f"Number of foreign keys doesn't match in table {table}"
        
        # Sort by referred table and columns since names may be None
        mfks = sorted(mfks, key=lambda x: (x['referred_table'], tuple(sorted(x['constrained_columns']))))
        fks = sorted(fks, key=lambda x: (x['referred_table'], tuple(sorted(x['constrained_columns']))))
        
        for mfk, fk in zip(mfks, fks):
            assert mfk['referred_table'] == fk['referred_table'], \
                f"Foreign key referred table mismatch in table {table}"
            assert set(mfk['constrained_columns']) == set(fk['constrained_columns']), \
                f"Foreign key constrained columns mismatch in table {table}"
            assert set(mfk['referred_columns']) == set(fk['referred_columns']), \
                f"Foreign key referred columns mismatch in table {table}"

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
                Column('threadId', String(100)),
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
            
            # Add indexes for tags table
            op.create_index('idx_tags_name', 'tags', [text('name COLLATE NOCASE')])
            op.create_index('idx_tags_deleted', 'tags', ['deleted'])

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
            
            # Add indexes for catalog_items table
            op.create_index('idx_catalog_items_deleted', 'catalog_items', ['deleted'])
            op.create_index('idx_catalog_items_status', 'catalog_items', ['status'])
            op.create_index('idx_catalog_items_title', 'catalog_items', ['title'])

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
            
            # Add indexes for item_relationships table
            op.create_index('idx_relationships_source', 'item_relationships', ['source_id'])
            op.create_index('idx_relationships_target', 'item_relationships', ['target_id'])
            op.create_index('idx_relationships_type', 'item_relationships', ['relationship_type'])

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
