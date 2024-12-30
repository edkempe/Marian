"""Test suite for migration management system."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer

from shared_lib.migration_utils import (
    get_alembic_config,
    get_current_revision,
    get_pending_migrations,
    validate_schema_changes,
    generate_migration,
    apply_migrations,
    get_migration_history,
)
from scripts.manage_migrations import (
    handle_generate,
    handle_apply,
    handle_validate,
    handle_history,
    handle_pending,
)
from models.registry import Base

@pytest.fixture
def temp_db():
    """Create a temporary SQLite database."""
    _, db_path = tempfile.mkstemp(suffix=".db")
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    yield engine
    os.unlink(db_path)

@pytest.fixture
def mock_config():
    """Create a mock Alembic config."""
    config = MagicMock(spec=Config)
    config.get_main_option.return_value = "sqlite:///test.db"
    return config

@pytest.fixture
def mock_args():
    """Create mock command-line arguments."""
    class Args:
        pass
    args = Args()
    args.message = "test migration"
    args.empty = False
    return args

def test_get_alembic_config(temp_db):
    """Test getting Alembic configuration."""
    config = get_alembic_config(temp_db)
    assert isinstance(config, Config)
    assert config.get_main_option("sqlalchemy.url") == str(temp_db.url)

def test_get_current_revision(temp_db):
    """Test getting current revision."""
    revision = get_current_revision(temp_db)
    assert revision is None  # No migrations applied yet

def test_get_pending_migrations(temp_db):
    """Test getting pending migrations."""
    pending = get_pending_migrations(temp_db)
    assert isinstance(pending, list)

def test_validate_schema_changes():
    """Test schema validation."""
    results = validate_schema_changes()
    assert isinstance(results, dict)
    assert "valid" in results
    assert "errors" in results
    assert "warnings" in results

@patch("shared_lib.migration_utils.command")
def test_generate_migration(mock_command):
    """Test generating migration."""
    message = "test migration"
    revision = generate_migration(message)
    mock_command.revision.assert_called_once()

@patch("shared_lib.migration_utils.command")
def test_apply_migrations(mock_command, temp_db):
    """Test applying migrations."""
    success = apply_migrations(temp_db)
    assert success
    mock_command.upgrade.assert_called_once()

def test_get_migration_history(temp_db):
    """Test getting migration history."""
    history = get_migration_history(temp_db)
    assert isinstance(history, list)
    for entry in history:
        assert "revision" in entry
        assert "down_revision" in entry
        assert "message" in entry
        assert "is_current" in entry

# CLI Command Tests

@patch("shared_lib.migration_utils.generate_migration")
def test_handle_generate(mock_generate, mock_args):
    """Test generate command handler."""
    mock_generate.return_value = "abc123"
    result = handle_generate(mock_args)
    assert result == 0
    mock_generate.assert_called_with("test migration", True)

@patch("shared_lib.migration_utils.apply_migrations")
def test_handle_apply(mock_apply, mock_args):
    """Test apply command handler."""
    mock_apply.return_value = True
    result = handle_apply(mock_args)
    assert result == 0
    assert mock_apply.call_count == 2  # Called for both databases

@patch("shared_lib.migration_utils.validate_schema_changes")
def test_handle_validate(mock_validate, mock_args):
    """Test validate command handler."""
    mock_validate.return_value = {"valid": True, "errors": [], "warnings": []}
    result = handle_validate(mock_args)
    assert result == 0
    mock_validate.assert_called_once()

@patch("shared_lib.migration_utils.get_migration_history")
def test_handle_history(mock_history, mock_args):
    """Test history command handler."""
    mock_history.return_value = [
        {
            "revision": "abc123",
            "down_revision": None,
            "message": "test",
            "is_current": True
        }
    ]
    result = handle_history(mock_args)
    assert result == 0
    assert mock_history.call_count == 2  # Called for both databases

@patch("shared_lib.migration_utils.get_pending_migrations")
def test_handle_pending(mock_pending, mock_args):
    """Test pending command handler."""
    mock_pending.return_value = ["abc123"]
    result = handle_pending(mock_args)
    assert result == 1  # Has pending migrations
    assert mock_pending.call_count == 2  # Called for both databases

# Integration Tests

def test_migration_workflow(temp_db):
    """Test complete migration workflow."""
    # 1. Generate migration
    message = "test migration"
    revision = generate_migration(message)
    assert revision is not None

    # 2. Validate schema
    validation = validate_schema_changes()
    assert validation["valid"]

    # 3. Apply migration
    success = apply_migrations(temp_db)
    assert success

    # 4. Check history
    history = get_migration_history(temp_db)
    assert len(history) > 0
    assert history[0]["message"] == message

    # 5. Check no pending migrations
    pending = get_pending_migrations(temp_db)
    assert len(pending) == 0
