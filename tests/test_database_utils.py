"""Test suite for database utilities.

This module tests:
1. Database seeding functionality
2. Migration utilities
3. Schema validation
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest
from sqlalchemy import create_engine, MetaData, Table, text, inspect
from sqlalchemy.exc import IntegrityError, OperationalError

from shared_lib.config_loader import get_schema_config
from shared_lib.constants import DATABASE_CONFIG
from shared_lib.database_seeder import DatabaseSeeder
from shared_lib.database_session_util import get_engine_for_db_type
from shared_lib.migration_utils import (
    generate_migration,
    apply_migrations,
    get_migration_status,
)


@pytest.fixture
def temp_db():
    """Create temporary test databases."""
    temp_dir = tempfile.mkdtemp()
    
    # Create temp config
    test_config = {
        "email": {
            "url": f"sqlite:///{os.path.join(temp_dir, 'test_email.db')}",
            "path": os.path.join(temp_dir, "test_email.db"),
        },
        "analysis": {
            "url": f"sqlite:///{os.path.join(temp_dir, 'test_analysis.db')}",
            "path": os.path.join(temp_dir, "test_analysis.db"),
        },
    }
    
    # Override config for testing
    DATABASE_CONFIG.clear()
    DATABASE_CONFIG.update(test_config)
    
    yield temp_dir
    
    # Cleanup
    for db_file in Path(temp_dir).glob("*.db"):
        db_file.unlink()
    Path(temp_dir).rmdir()


@pytest.fixture
def seeder(temp_db):
    """Create database seeder instance."""
    return DatabaseSeeder(env="test")


def test_seeder_initialization(seeder):
    """Test seeder initialization."""
    assert seeder.env == "test"
    assert seeder.faker is not None
    assert seeder.schema_config is not None
    assert seeder.email_engine is not None
    assert seeder.analysis_engine is not None
    assert seeder.email_metadata is not None
    assert seeder.analysis_metadata is not None


def test_fake_email_generation(seeder):
    """Test fake email generation."""
    email = seeder._generate_fake_email()
    
    assert isinstance(email, dict)
    assert "subject" in email
    assert "sender" in email
    assert "recipient" in email
    assert "body" in email
    assert "timestamp" in email
    assert "has_attachments" in email
    assert "thread_id" in email
    assert "message_id" in email


def test_fake_analysis_generation(seeder):
    """Test fake analysis generation."""
    analysis = seeder._generate_fake_analysis("test_id")
    
    assert isinstance(analysis, dict)
    assert analysis["email_id"] == "test_id"
    assert analysis["sentiment"] in seeder.schema_config.analysis.validation.valid_sentiments
    assert analysis["priority"] in seeder.schema_config.analysis.validation.valid_priorities
    assert len(analysis["summary"]) <= seeder.schema_config.analysis.validation.max_summary_length
    assert "analyzed_at" in analysis


def test_fake_label_generation(seeder):
    """Test fake label generation."""
    label = seeder._generate_fake_label()
    
    assert isinstance(label, dict)
    assert "name" in label
    assert label["type"] in seeder.schema_config.label.validation.valid_types
    assert "color" in label
    assert isinstance(label["visible"], bool)


def test_seed_emails(seeder):
    """Test email seeding."""
    count = 5
    emails = seeder.seed_emails(count=count)
    
    assert len(emails) == count
    
    # Verify database state
    inspector = inspect(seeder.email_engine)
    assert "email" in inspector.get_table_names()
    
    with seeder.email_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM email")).scalar()
        assert result == count


def test_seed_analysis(seeder):
    """Test analysis seeding."""
    # First seed some emails
    emails = seeder.seed_emails(count=3)
    
    # Then seed analysis
    analyses = seeder.seed_analysis(emails=emails)
    
    assert len(analyses) == len(emails)
    
    # Verify database state
    inspector = inspect(seeder.analysis_engine)
    assert "analysis" in inspector.get_table_names()
    
    with seeder.analysis_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM analysis")).scalar()
        assert result == len(emails)


def test_seed_labels(seeder):
    """Test label seeding."""
    count = 3
    labels = seeder.seed_labels(count=count)
    
    assert len(labels) == count
    
    # Verify database state
    inspector = inspect(seeder.email_engine)
    assert "gmail_label" in inspector.get_table_names()
    
    with seeder.email_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM gmail_label")).scalar()
        assert result == count


def test_seed_all(seeder):
    """Test seeding all data types."""
    email_count = 3
    label_count = 2
    
    result = seeder.seed_all(
        email_count=email_count,
        label_count=label_count
    )
    
    assert len(result["emails"]) == email_count
    assert len(result["analyses"]) == email_count
    assert len(result["labels"]) == label_count


def test_cleanup(seeder):
    """Test data cleanup."""
    # First seed some data
    seeder.seed_all(email_count=3, label_count=2)
    
    # Then clean it up
    seeder.cleanup()
    
    # Verify all tables are empty except alembic_version
    for engine in [seeder.email_engine, seeder.analysis_engine]:
        inspector = inspect(engine)
        for table in inspector.get_table_names():
            if table != "alembic_version":
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    assert result == 0


def test_migration_generation(temp_db):
    """Test migration generation."""
    # Create migrations directory
    migrations_dir = Path(temp_db) / "migrations"
    migrations_dir.mkdir()
    
    try:
        # Generate a migration
        migration_path = generate_migration(
            "test_migration",
            str(migrations_dir),
            message="Test migration"
        )
        
        # Verify migration was created
        assert Path(migration_path).exists()
        assert "test_migration" in migration_path
    finally:
        # Clean up all files in migrations directory
        if migrations_dir.exists():
            for item in migrations_dir.glob("**/*"):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    for file in item.glob("*"):
                        file.unlink()
                    item.rmdir()
            migrations_dir.rmdir()


def test_migration_application(temp_db):
    """Test migration application."""
    # Apply migrations
    apply_migrations()
    
    # Check status
    status = get_migration_status()
    
    assert status["current_revision"] is not None
    assert not status["pending_migrations"]


def test_migration_status(temp_db):
    """Test migration status check."""
    status = get_migration_status()
    
    assert isinstance(status, dict)
    assert "current_revision" in status
    assert "pending_migrations" in status


def test_seeder_with_invalid_env():
    """Test seeder initialization with invalid environment."""
    with pytest.raises(ValueError, match="Invalid environment"):
        DatabaseSeeder(env="invalid_env")


def test_seed_with_invalid_seed_file(seeder):
    """Test seeding with non-existent seed file."""
    with pytest.raises(FileNotFoundError):
        seeder.seed_emails(seed_file="nonexistent")


def test_seed_with_malformed_seed_file(seeder, temp_db):
    """Test seeding with malformed seed file."""
    # Create malformed seed file
    seed_path = Path(temp_db) / "malformed.yaml"
    seed_path.write_text("invalid: yaml: content")
    
    with pytest.raises(Exception, match="Failed to parse seed file"):
        seeder.seed_emails(seed_file=str(seed_path))


def test_seed_with_invalid_data(seeder):
    """Test seeding with invalid data."""
    # Test with missing required fields
    invalid_email = {
        "subject": "Test Subject"
        # Missing other required fields
    }
    
    with pytest.raises(IntegrityError):
        seeder.email_engine.execute(
            seeder.email_metadata.tables["email"].insert(),
            invalid_email
        )


def test_seed_with_duplicate_data(seeder):
    """Test handling of duplicate data."""
    email = seeder._generate_fake_email()
    
    # First insertion should succeed
    emails = seeder.seed_emails(count=1)
    assert len(emails) == 1
    
    # Second insertion of same data should fail
    with pytest.raises(IntegrityError):
        with seeder.email_engine.begin() as conn:
            conn.execute(
                seeder.email_metadata.tables["email"].insert(),
                email
            )


def test_seed_with_large_dataset(seeder):
    """Test seeding with a large dataset."""
    count = 1000
    emails = seeder.seed_emails(count=count)
    
    assert len(emails) == count
    
    # Verify database state
    with seeder.email_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM email")).scalar()
        assert result == count


def test_seed_with_empty_dataset(seeder):
    """Test seeding with empty dataset."""
    emails = seeder.seed_emails(count=0)
    assert len(emails) == 0
    
    # Verify database state
    with seeder.email_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM email")).scalar()
        assert result == 0


def test_cleanup_with_active_connections(seeder):
    """Test cleanup with active database connections."""
    # First seed some data
    seeder.seed_emails(count=5)
    
    # Create an active connection
    conn = seeder.email_engine.connect()
    
    try:
        # Cleanup should still work
        seeder.cleanup()
        
        # Verify cleanup was successful
        result = conn.execute(text("SELECT COUNT(*) FROM email")).scalar()
        assert result == 0
    finally:
        conn.close()


def test_migration_with_invalid_path():
    """Test migration generation with invalid path."""
    with pytest.raises(ValueError):
        generate_migration(
            "test_migration",
            "/nonexistent/path",
            autogenerate=True
        )


def test_migration_with_invalid_name():
    """Test migration generation with invalid name."""
    with pytest.raises(ValueError):
        generate_migration(
            "",  # Empty name
            "migrations",
            autogenerate=True
        )


def test_migration_with_locked_db(temp_db):
    """Test migration with locked database."""
    # Create a lock on the database
    engine = get_engine_for_db_type("email")
    conn = engine.connect()
    
    try:
        # Try to apply migrations while DB is locked
        with pytest.raises(OperationalError):
            apply_migrations()
    finally:
        conn.close()


def test_concurrent_migrations(temp_db):
    """Test concurrent migration operations."""
    import threading
    import queue
    
    errors = queue.Queue()
    
    def run_migration():
        try:
            apply_migrations()
        except Exception as e:
            errors.put(e)
    
    # Start multiple threads
    threads = [
        threading.Thread(target=run_migration)
        for _ in range(3)
    ]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    # Check for errors
    assert errors.empty(), f"Migration errors occurred: {list(errors.queue)}"
    
    # Verify final state
    status = get_migration_status()
    assert not status["pending_migrations"]


def test_schema_validation():
    """Test schema validation against configuration."""
    schema_config = get_schema_config()
    
    # Test email validation
    valid_email = {
        "subject": "Test Subject",
        "sender": "test@example.com",
        "recipient": "recipient@example.com",
        "body": "Test body",
        "timestamp": "2024-01-01T00:00:00Z",
        "has_attachments": False,
        "thread_id": "thread123",
        "message_id": "msg123"
    }
    
    # Should not raise any errors
    schema_config.email.validate(valid_email)
    
    # Test with invalid email
    invalid_email = {
        "subject": "Test Subject",
        "sender": "not_an_email",  # Invalid email format
        "recipient": "also_not_an_email",  # Invalid email format
        "body": "Test body"
        # Missing required fields
    }
    
    with pytest.raises(ValueError):
        schema_config.email.validate(invalid_email)


def test_schema_constraints():
    """Test schema constraint validation."""
    schema_config = get_schema_config()
    
    # Test string length constraints
    too_long_subject = {
        "subject": "x" * (schema_config.email.validation.max_subject_length + 1),
        "sender": "test@example.com",
        "recipient": "recipient@example.com",
        "body": "Test body",
        "timestamp": "2024-01-01T00:00:00Z",
        "has_attachments": False,
        "thread_id": "thread123",
        "message_id": "msg123"
    }
    
    with pytest.raises(ValueError):
        schema_config.email.validate(too_long_subject)
    
    # Test enum constraints
    invalid_priority = {
        "email_id": "email123",
        "sentiment": "positive",
        "priority": "INVALID_PRIORITY",  # Invalid priority
        "summary": "Test summary",
        "analyzed_at": "2024-01-01T00:00:00Z"
    }
    
    with pytest.raises(ValueError):
        schema_config.analysis.validate(invalid_priority)
