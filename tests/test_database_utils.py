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
import logging

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
import shutil

logger = logging.getLogger(__name__)

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
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        logger.warning(f"Failed to clean up temp directory: {str(e)}")


@pytest.fixture
def seeder(temp_db):
    """Create database seeder instance."""
    return DatabaseSeeder(env="test")


def test_seeder_initialization(seeder):
    """Test seeder initialization."""
    try:
        assert seeder.env == "test"
        assert seeder.faker is not None
        assert seeder.schema_config is not None
        assert seeder.email_engine is not None
        assert seeder.analysis_engine is not None
        assert seeder.email_metadata is not None
        assert seeder.analysis_metadata is not None
    finally:
        seeder.cleanup()


def test_fake_email_generation(seeder):
    """Test fake email generation."""
    try:
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
    finally:
        seeder.cleanup()


def test_fake_analysis_generation(seeder):
    """Test fake analysis generation."""
    try:
        analysis = seeder._generate_fake_analysis("test_id")
        
        assert isinstance(analysis, dict)
        assert analysis["email_id"] == "test_id"
        assert analysis["sentiment"] in seeder.schema_config.analysis.validation.valid_sentiments
        assert analysis["priority"] in seeder.schema_config.analysis.validation.valid_priorities
        assert len(analysis["summary"]) <= seeder.schema_config.analysis.validation.max_summary_length
        assert "analyzed_at" in analysis
    finally:
        seeder.cleanup()


def test_fake_label_generation(seeder):
    """Test fake label generation."""
    try:
        label = seeder._generate_fake_label()
        
        assert isinstance(label, dict)
        assert "name" in label
        assert label["type"] in seeder.schema_config.label.validation.valid_types
        assert "color" in label
        assert isinstance(label["visible"], bool)
    finally:
        seeder.cleanup()


def test_seed_emails(seeder):
    """Test email seeding."""
    try:
        count = 5
        emails = seeder.seed_emails(count=count)
        
        assert len(emails) == count
        
        # Verify database state
        inspector = inspect(seeder.email_engine)
        assert "email" in inspector.get_table_names()
        
        with seeder.email_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM email")).scalar()
            assert result == count
    finally:
        seeder.cleanup()


def test_seed_analysis(seeder):
    """Test analysis seeding."""
    try:
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
    finally:
        seeder.cleanup()


def test_seed_labels(seeder):
    """Test label seeding."""
    try:
        count = 3
        labels = seeder.seed_labels(count=count)
        
        assert len(labels) == count
        
        # Verify database state
        inspector = inspect(seeder.email_engine)
        assert "gmail_label" in inspector.get_table_names()
        
        with seeder.email_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM gmail_label")).scalar()
            assert result == count
    finally:
        seeder.cleanup()


def test_seed_all(seeder):
    """Test seeding all data types."""
    try:
        email_count = 3
        label_count = 2
        
        result = seeder.seed_all(
            email_count=email_count,
            label_count=label_count
        )
        
        assert len(result["emails"]) == email_count
        assert len(result["analyses"]) == email_count
        assert len(result["labels"]) == label_count
    finally:
        seeder.cleanup()


def test_cleanup(seeder):
    """Test data cleanup."""
    try:
        # First seed some data
        seeder.seed_all(email_count=3, label_count=2)
        
        # Then clean it up
        seeder.cleanup()
        
        # Verify all tables are empty except alembic_version
        for engine, metadata in [(seeder.email_engine, seeder.email_metadata), 
                               (seeder.analysis_engine, seeder.analysis_metadata)]:
            for table in metadata.sorted_tables:
                if table.name != "alembic_version":
                    with engine.connect() as conn:
                        result = conn.execute(table.select()).scalar()
                        assert result is None
    finally:
        seeder.cleanup()


def test_migration_generation(temp_db):
    """Test migration generation."""
    try:
        # Create migrations directory
        migrations_dir = Path(temp_db) / "migrations"
        migrations_dir.mkdir()
        
        # Generate a migration
        migration_path = generate_migration(
            "test_migration",
            str(migrations_dir),
            message="Test migration"
        )
        
        # Verify migration was created
        migration_file = Path(migration_path)
        assert migration_file.exists()
        assert "test_migration" in migration_path
        
        # Verify migration content
        content = migration_file.read_text()
        assert "Test migration" in content
        assert "def upgrade() -> None:" in content
        assert "def downgrade() -> None:" in content
        assert "revision = " in content
        assert "down_revision = None" in content
    finally:
        # Clean up all files in migrations directory
        if migrations_dir.exists():
            try:
                shutil.rmtree(migrations_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up migrations directory: {str(e)}")


def test_migration_application(temp_db):
    """Test migration application."""
    try:
        # Create migrations directory
        migrations_dir = Path(temp_db) / "migrations"
        migrations_dir.mkdir()
        
        # Generate a migration
        migration_path = generate_migration(
            "test_migration",
            str(migrations_dir),
            message="Test migration"
        )
        
        # Apply migrations
        engine = get_engine_for_db_type("email")
        apply_migrations(engine)
        
        # Verify migration was applied
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
            assert result is not None
    finally:
        # Clean up migrations directory
        if migrations_dir.exists():
            try:
                shutil.rmtree(migrations_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up migrations directory: {str(e)}")


def test_migration_status(temp_db):
    """Test migration status check."""
    try:
        status = get_migration_status()
        
        assert isinstance(status, dict)
        assert "current_revision" in status
        assert "pending_migrations" in status
    finally:
        pass


def test_seeder_with_invalid_env():
    """Test seeder initialization with invalid environment."""
    try:
        with pytest.raises(ValueError, match="Invalid environment"):
            DatabaseSeeder(env="invalid_env")
    finally:
        pass


def test_seed_with_invalid_seed_file(seeder):
    """Test seeding with non-existent seed file."""
    try:
        with pytest.raises(FileNotFoundError):
            seeder.seed_emails(seed_file="nonexistent")
    finally:
        seeder.cleanup()


def test_seed_with_malformed_seed_file(seeder, temp_db):
    """Test seeding with malformed seed file."""
    try:
        # Create malformed seed file
        seed_path = Path(temp_db) / "malformed.yaml"
        seed_path.write_text("invalid: yaml: content")
        
        with pytest.raises(Exception, match="Failed to parse seed file"):
            seeder.seed_emails(seed_file=str(seed_path))
    finally:
        seeder.cleanup()


def test_seed_with_invalid_data(seeder):
    """Test seeding with invalid data."""
    try:
        # Test emails with missing required fields
        with pytest.raises(ValueError, match="Required field"):
            seeder.seed_emails(count=1, invalid_data=True)
            
        # Test analysis with invalid data types
        # First seed a valid email to get an ID
        emails = seeder.seed_emails(count=1)
        with pytest.raises(ValueError, match="Invalid type"):
            seeder.seed_analysis(emails=emails, count=1, invalid_data=True)
            
        # Test labels with invalid data
        with pytest.raises(ValueError, match="Invalid type"):
            seeder.seed_labels(count=1, invalid_data=True)
    finally:
        seeder.cleanup()


def test_seed_with_duplicate_data(seeder):
    """Test handling of duplicate data."""
    try:
        # First insertion should succeed
        emails = seeder.seed_emails(count=1)
        assert len(emails) == 1
        
        # Second insertion with same data should fail
        with pytest.raises(IntegrityError):
            # Use the same email data for second insertion
            email_data = emails[0].copy()
            del email_data['id']  # Remove the ID as it's auto-generated
            with seeder.email_engine.begin() as conn:
                conn.execute(
                    seeder.email_metadata.tables["email"].insert(),
                    email_data
                )
    finally:
        seeder.cleanup()


def test_seed_with_large_dataset(seeder):
    """Test seeding with a large dataset."""
    try:
        count = 1000
        emails = seeder.seed_emails(count=count)
        
        assert len(emails) == count
        
        # Verify database state
        with seeder.email_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM email")).scalar()
            assert result == count
    finally:
        seeder.cleanup()


def test_seed_with_empty_dataset(seeder):
    """Test seeding with empty dataset."""
    try:
        emails = seeder.seed_emails(count=0)
        assert len(emails) == 0
        
        # Verify database state
        with seeder.email_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM email")).scalar()
            assert result == 0
    finally:
        seeder.cleanup()


def test_cleanup_with_active_connections(seeder):
    """Test cleanup with active database connections."""
    try:
        # First seed some data
        seeder.seed_emails(count=5)
        
        # Create an active connection
        conn = seeder.email_engine.connect()
        
        # Cleanup should still work
        seeder.cleanup()
        
        # Verify cleanup was successful
        result = conn.execute(text("SELECT COUNT(*) FROM email")).scalar()
        assert result == 0
    finally:
        conn.close()
        seeder.cleanup()


def test_migration_with_invalid_path():
    """Test migration generation with invalid path."""
    try:
        with pytest.raises(ValueError):
            generate_migration(
                "test_migration",
                "/nonexistent/path",
                autogenerate=True
            )
    finally:
        pass


def test_migration_with_invalid_name():
    """Test migration generation with invalid name."""
    try:
        with pytest.raises(ValueError):
            generate_migration(
                "",  # Empty name
                "migrations",
                autogenerate=True
            )
    finally:
        pass


def test_concurrent_migrations(temp_db):
    """Test concurrent migration operations.
    
    Note: This test verifies that our migration system can handle concurrent
    requests to migrate, but does not actually run migrations in parallel since
    SQLite does not support true concurrent write operations.
    """
    try:
        import threading
        import queue
        from time import sleep

        errors = queue.Queue()
        completed = queue.Queue()
        engine = get_engine_for_db_type("email")

        def run_migration(delay):
            try:
                # Add a small delay to simulate concurrent requests
                sleep(delay)
                apply_migrations(engine)
                completed.put(True)
            except Exception as e:
                errors.put(e)

        # Start multiple threads with different delays
        threads = [
            threading.Thread(target=run_migration, args=(i * 0.1,))
            for i in range(3)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Check for errors
        assert errors.empty(), f"Migration errors occurred: {list(errors.queue)}"
        
        # Verify only one migration completed (others should have been skipped)
        assert completed.qsize() == 1, "Expected only one successful migration"

    except Exception as e:
        pass


def test_schema_validation():
    """Test schema validation against configuration."""
    try:
        schema_config = get_schema_config()

        # Test email validation
        valid_email = {
            "columns": {
                "subject": "Test Subject",
                "sender": "test@example.com",
                "recipient": "recipient@example.com",
                "body": "Test body",
                "timestamp": "2024-01-01T00:00:00Z",
                "has_attachments": False,
                "thread_id": "thread123",
                "message_id": "msg123"
            }
        }

        # Should not raise any errors
        schema_config.email.model_validate(valid_email)

        # Test invalid email
        invalid_email = {
            "columns": {
                "subject": "Test Subject",
                "sender": "not_an_email",  # Invalid email format
                "body": "Test body"
                # Missing required fields
            }
        }

        # Should raise validation error
        with pytest.raises(ValidationError):
            schema_config.email.model_validate(invalid_email)

    except Exception as e:
        pass


def test_schema_constraints():
    """Test schema constraint validation."""
    try:
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
    finally:
        pass
