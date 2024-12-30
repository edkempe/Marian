"""Test suite for migration management system."""

import os
import shutil
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime
from typing import Dict, Any, List

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    ForeignKey,
    inspect,
    event,
)
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.engine import Engine

from shared_lib.migration_utils import (
    get_alembic_config,
    get_current_revision,
    get_pending_migrations,
    validate_schema_changes,
    generate_migration,
    apply_migrations,
    get_migration_history,
    rollback_migration,
    rollback_to_revision,
)
from scripts.manage_migrations import (
    handle_generate,
    handle_apply,
    handle_validate,
    handle_history,
    handle_pending,
    handle_rollback,
)
from models.registry import Base
from shared_lib.constants import DATABASE_CONFIG, COLUMN_SIZES
from shared_lib.schema_constants import EmailDefaults, AnalysisDefaults, LabelDefaults


@pytest.fixture(scope="session")
def test_migrations_dir():
    """Create a temporary migrations directory."""
    temp_dir = tempfile.mkdtemp()
    migrations_dir = Path(temp_dir) / "migrations"
    migrations_dir.mkdir()
    
    # Copy alembic.ini to temp directory
    shutil.copy("alembic.ini", temp_dir)
    
    # Create versions directory
    versions_dir = migrations_dir / "versions"
    versions_dir.mkdir()
    
    # Create env.py
    env_py = migrations_dir / "env.py"
    env_py.write_text("""
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

config = context.config
fileConfig(config.config_file_name)

target_metadata = None

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
    """)
    
    # Create initial migration script
    initial_migration = versions_dir / "001_initial_schema.py"
    initial_migration.write_text("""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'test_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('test_table')
    """)
    
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_db(test_migrations_dir):
    """Create a temporary SQLite database."""
    _, db_path = tempfile.mkstemp(suffix=".db")
    engine = create_engine(f"sqlite:///{db_path}")
    
    # Create alembic config pointing to our test migrations
    config = Config(os.path.join(test_migrations_dir, "alembic.ini"))
    config.set_main_option("script_location", str(Path(test_migrations_dir) / "migrations"))
    config.set_main_option("sqlalchemy.url", str(engine.url))
    
    # Initialize database with alembic
    command.upgrade(config, "head")
    
    yield engine
    os.unlink(db_path)


def test_get_alembic_config(temp_db):
    """Test getting Alembic configuration."""
    config = get_alembic_config(temp_db)
    assert isinstance(config, Config)
    assert config.get_main_option("sqlalchemy.url") == str(temp_db.url)
    
    # Test with invalid database URL
    with pytest.raises(ValueError):
        get_alembic_config(None)


def test_get_current_revision(temp_db, test_migrations_dir):
    """Test getting current revision."""
    # Test with initial migration
    revision = get_current_revision(temp_db)
    assert revision is not None  # Should have initial revision
    assert revision == "001"  # Should match our initial migration
    
    # Create and apply a new migration
    config = Config(os.path.join(test_migrations_dir, "alembic.ini"))
    config.set_main_option("script_location", str(Path(test_migrations_dir) / "migrations"))
    config.set_main_option("sqlalchemy.url", str(temp_db.url))
    
    script = ScriptDirectory.from_config(config)
    
    # Create a new migration file
    new_migration = Path(test_migrations_dir) / "migrations" / "versions" / "002_test_migration.py"
    new_migration.write_text("""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'

def upgrade():
    op.create_table(
        'another_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('value', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('another_table')
""")
    
    command.upgrade(config, "head")
    new_revision = get_current_revision(temp_db)
    assert new_revision is not None
    assert new_revision == "002"  # Should have updated to new revision
    
    # Test with invalid database
    nonexistent_dir = "/nonexistent/directory/db.sqlite"
    invalid_db = create_engine(f"sqlite:///{nonexistent_dir}")
    with pytest.raises((OperationalError, sqlite3.OperationalError)):
        get_current_revision(invalid_db)


def test_get_pending_migrations(temp_db, test_migrations_dir):
    """Test getting pending migrations."""
    # Test with no migrations applied
    config = Config(os.path.join(test_migrations_dir, "alembic.ini"))
    config.set_main_option("script_location", str(Path(test_migrations_dir) / "migrations"))
    config.set_main_option("sqlalchemy.url", str(temp_db.url))
    
    # Check current revision
    with temp_db.connect() as connection:
        context = MigrationContext.configure(connection)
        current = context.get_current_revision()
    assert current == "002"  # Should be at 002 from the fixture
    
    # Create a new migration file
    new_migration = Path(test_migrations_dir) / "migrations" / "versions" / "003_test_migration.py"
    new_migration.write_text("""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'  # Make this depend on 002 since it's already applied

def upgrade():
    op.create_table(
        'test_table_3',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('value', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('test_table_3')
""")

    # Test with one pending migration
    pending = get_pending_migrations(config, temp_db)
    assert isinstance(pending, list)
    assert len(pending) == 1  # Should have our new migration
    assert pending[0] == "003"  # Should be our new migration
    
    # Apply all migrations
    command.upgrade(config, "head")
    
    # Test with no pending migrations
    pending = get_pending_migrations(config, temp_db)
    assert len(pending) == 0
    
    # Create multiple pending migrations
    new_migration_1 = Path(test_migrations_dir) / "migrations" / "versions" / "004_test_migration.py"
    new_migration_1.write_text("""
from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'

def upgrade():
    op.create_table('test_table_4', sa.Column('id', sa.Integer(), nullable=False))

def downgrade():
    op.drop_table('test_table_4')
""")

    new_migration_2 = Path(test_migrations_dir) / "migrations" / "versions" / "005_test_migration.py"
    new_migration_2.write_text("""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'

def upgrade():
    op.create_table('test_table_5', sa.Column('id', sa.Integer(), nullable=False))

def downgrade():
    op.drop_table('test_table_5')
""")

    # Test with multiple pending migrations
    pending = get_pending_migrations(config, temp_db)
    assert len(pending) == 2
    assert pending == ["004", "005"]  # Should be in upgrade order
    
    # Test with invalid database
    nonexistent_dir = "/nonexistent/directory/db.sqlite"
    invalid_db = create_engine(f"sqlite:///{nonexistent_dir}")
    with pytest.raises((OperationalError, sqlite3.OperationalError)):
        get_pending_migrations(config, invalid_db)
    
    # Test with invalid config
    invalid_config = Config(os.path.join(test_migrations_dir, "nonexistent.ini"))
    with pytest.raises(OperationalError):
        get_pending_migrations(invalid_config, temp_db)


def test_validate_schema_changes(temp_db):
    """Test schema validation using real database tables."""
    # Create test tables in the database
    metadata = MetaData()
    
    # Create and register test tables
    test_table = Table(
        'test', metadata,
        Column('name', String(50)),
        Column('id', Integer, primary_key=True)
    )
    
    # Create tables in the database
    metadata.create_all(temp_db)
    
    # Test normal validation (should pass)
    results = validate_schema_changes()
    assert isinstance(results, dict)
    assert "valid" in results
    assert "errors" in results
    assert "warnings" in results
    assert any("Column size not defined" in warning for warning in results["warnings"])
    
    # Add column size definition and test mismatch
    COLUMN_SIZES["TEST_NAME"] = 100  # Different from actual size of 50
    results = validate_schema_changes()
    assert not results["valid"]
    assert any("Column size mismatch" in error for error in results["errors"])
    assert any("expected 100, got 50" in error for error in results["errors"])
    
    # Test with invalid foreign key by creating a new table
    test_fk_table = Table(
        'test_fk', metadata,
        Column('id', Integer, primary_key=True),
        Column('other_id', Integer, ForeignKey('nonexistent.id'))
    )
    test_fk_table.create(temp_db)
    
    results = validate_schema_changes()
    assert not results["valid"]
    assert any("Invalid foreign key" in error for error in results["errors"])
    
    # Cleanup - drop all tables
    metadata.drop_all(temp_db)
    
    # Reset column sizes
    if "TEST_NAME" in COLUMN_SIZES:
        del COLUMN_SIZES["TEST_NAME"]


def test_generate_migration(temp_db):
    """Test generating migration."""
    # Test normal generation
    message = "test migration"
    revision = generate_migration(message)
    assert revision is not None
    
    # Test empty migration
    revision = generate_migration(message, autogenerate=False)
    assert revision is not None
    
    # Test with invalid message
    with pytest.raises(ValueError):
        generate_migration("")


def test_apply_migrations(temp_db):
    """Test applying migrations."""
    # Test normal upgrade
    success = apply_migrations(temp_db)
    assert success
    
    # Test with target revision
    success = apply_migrations(temp_db, target_revision="specific_rev")
    assert success
    
    # Test dry run
    results = apply_migrations(temp_db, dry_run=True)
    assert isinstance(results, dict)
    assert "success" in results
    assert "changes" in results
    
    # Test with invalid database
    nonexistent_dir = "/nonexistent/directory/db.sqlite"
    invalid_db = create_engine(f"sqlite:///{nonexistent_dir}")
    with pytest.raises((OperationalError, sqlite3.OperationalError)):
        apply_migrations(invalid_db)


def test_rollback_functionality(temp_db, test_migrations_dir):
    """Test migration rollback functionality."""
    # Get initial revision
    initial_rev = get_current_revision(temp_db)
    assert initial_rev is not None
    assert initial_rev == "001"
    
    # Create and apply a new migration
    config = Config(os.path.join(test_migrations_dir, "alembic.ini"))
    config.set_main_option("script_location", str(Path(test_migrations_dir) / "migrations"))
    config.set_main_option("sqlalchemy.url", str(temp_db.url))
    
    # Create a new migration file
    new_migration = Path(test_migrations_dir) / "migrations" / "versions" / "003_test_tables.py"
    new_migration.write_text("""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '001'

def upgrade():
    op.create_table(
        'test_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('test_table')
""")
    
    # Apply the test migration
    command.upgrade(config, "head")
    
    # Verify the table exists
    inspector = inspect(temp_db)
    assert "test_table" in inspector.get_table_names()
    
    # Test rollback one step
    success = rollback_migration(temp_db)
    assert success
    inspector = inspect(temp_db)
    assert "test_table" not in inspector.get_table_names()
    
    # Test rollback to specific revision
    command.upgrade(config, "head")
    success = rollback_to_revision(temp_db, "001")
    assert success
    assert get_current_revision(temp_db) == "001"


def test_migration_history(temp_db):
    """Test migration history functionality."""
    # Apply migrations
    config = get_alembic_config(temp_db)
    command.upgrade(config, "head")
    
    # Test basic history
    history = get_migration_history(temp_db)
    assert isinstance(history, list)
    assert len(history) > 0
    for entry in history:
        assert "revision" in entry
        assert "down_revision" in entry
    
    # Test with detailed flag
    detailed_history = get_migration_history(temp_db, detailed=True)
    assert len(detailed_history) == len(history)
    for entry in detailed_history:
        assert "revision" in entry
        assert "down_revision" in entry
        assert "is_current" in entry
        assert "operations" in entry


def test_concurrent_migrations(temp_db):
    """Test handling of concurrent migration operations."""
    from concurrent.futures import ThreadPoolExecutor
    import threading
    
    lock = threading.Lock()
    success_count = 0
    
    def run_migration():
        nonlocal success_count
        try:
            result = apply_migrations(temp_db)
            with lock:
                if result:
                    success_count += 1
        except OperationalError:
            # Expected for concurrent operations
            pass
    
    # Try running migrations concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(run_migration) for _ in range(3)]
        for future in futures:
            future.result()
    
    # Only one migration should succeed
    assert success_count == 1
    
    # Verify database is in a consistent state
    assert get_current_revision(temp_db) is not None


def test_handle_generate():
    """Test generate command handler."""
    with patch("scripts.manage_migrations.generate_migration") as mock_generate:
        mock_generate.return_value = "new_revision"
        result = handle_generate(None)
        assert result == 0
        mock_generate.assert_called_once()


def test_handle_apply():
    """Test apply command handler."""
    with patch("scripts.manage_migrations.apply_migrations") as mock_apply:
        mock_apply.return_value = True
        result = handle_apply(None)
        assert result == 0
        mock_apply.assert_called_once()


def test_handle_validate():
    """Test validate command handler."""
    with patch("scripts.manage_migrations.validate_schema_changes") as mock_validate:
        mock_validate.return_value = {"valid": True, "errors": [], "warnings": []}
        result = handle_validate(None)
        assert result == 0
        mock_validate.assert_called_once()


def test_handle_history():
    """Test history command handler."""
    with patch("scripts.manage_migrations.get_migration_history") as mock_history:
        mock_history.return_value = [
            {"revision": "rev1", "message": "first migration"},
            {"revision": "rev2", "message": "second migration"},
        ]
        result = handle_history(None)
        assert result == 0
        mock_history.assert_called_once()


def test_handle_pending():
    """Test pending command handler."""
    with patch("scripts.manage_migrations.get_pending_migrations") as mock_pending:
        mock_pending.return_value = ["rev1", "rev2"]
        result = handle_pending(None)
        assert result == 0
        mock_pending.assert_called_once()


def test_handle_rollback():
    """Test rollback command handler."""
    with patch("scripts.manage_migrations.rollback_migration") as mock_rollback:
        mock_rollback.return_value = True
        result = handle_rollback(None)
        assert result == 0
        mock_rollback.assert_called_once()


def test_migration_workflow(temp_db, test_migrations_dir):
    """Test complete migration workflow."""
    # 1. Get initial state
    initial_rev = get_current_revision(temp_db)
    assert initial_rev is not None  # Should have initial revision
    assert initial_rev == "001"  # Should match our initial migration
    
    # 2. Create and apply a new migration
    config = Config(os.path.join(test_migrations_dir, "alembic.ini"))
    config.set_main_option("script_location", str(Path(test_migrations_dir) / "migrations"))
    config.set_main_option("sqlalchemy.url", str(temp_db.url))
    
    # Create a new migration file
    new_migration = Path(test_migrations_dir) / "migrations" / "versions" / "004_app_tables.py"
    new_migration.write_text("""
from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '001'

def upgrade():
    # Create emails table
    op.create_table(
        'emails',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('subject', sa.String(200), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create email_analysis table
    op.create_table(
        'email_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email_id', sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create gmail_labels table
    op.create_table(
        'gmail_labels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('gmail_labels')
    op.drop_table('email_analysis')
    op.drop_table('emails')
""")
    
    command.upgrade(config, "head")
    
    # 3. Verify tables were created
    inspector = inspect(temp_db)
    tables = inspector.get_table_names()
    assert "emails" in tables
    assert "email_analysis" in tables
    assert "gmail_labels" in tables
    
    # 4. Check table structure
    email_columns = {col["name"]: col for col in inspector.get_columns("emails")}
    assert "id" in email_columns
    assert "subject" in email_columns
    assert email_columns["id"]["type"].__class__.__name__ == "String"
    
    # 5. Verify foreign key relationship
    fkeys = inspector.get_foreign_keys("email_analysis")
    assert len(fkeys) == 1
    assert fkeys[0]["referred_table"] == "emails"
    
    # 6. Test rollback
    success = rollback_migration(temp_db)
    assert success
    assert get_current_revision(temp_db) == "001"
