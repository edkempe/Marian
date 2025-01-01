"""Tests for database migrations."""

import os
import tempfile
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from models.base import Base
from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel


@pytest.fixture
def alembic_config():
    """Create a temporary alembic configuration."""
    # Create a temporary directory for migrations
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create alembic.ini in temp directory
        config_path = Path(temp_dir) / "alembic.ini"
        config_content = (
            "[alembic]\n"
            "script_location = migrations\n"
            "sqlalchemy.url = sqlite:///%(here)s/test.db\n\n"
            "[loggers]\n"
            "keys = root,sqlalchemy,alembic\n\n"
            "[handlers]\n"
            "keys = console\n\n"
            "[formatters]\n"
            "keys = generic\n\n"
            "[logger_root]\n"
            "level = WARN\n"
            "handlers = console\n"
            "qualname =\n\n"
            "[logger_sqlalchemy]\n"
            "level = WARN\n"
            "handlers =\n"
            "qualname = sqlalchemy.engine\n\n"
            "[logger_alembic]\n"
            "level = INFO\n"
            "handlers =\n"
            "qualname = alembic\n\n"
            "[handler_console]\n"
            "class = StreamHandler\n"
            "args = (sys.stderr,)\n"
            "level = NOTSET\n"
            "formatter = generic\n\n"
            "[formatter_generic]\n"
            "format = %(levelname)-5.5s [%(name)s] %(message)s\n"
            "datefmt = %H:%M:%S\n"
        )
        with open(config_path, "w") as f:
            f.write(config_content)
            
        # Create migrations directory
        migrations_dir = Path(temp_dir) / "migrations"
        migrations_dir.mkdir()
        
        # Create versions directory
        versions_dir = migrations_dir / "versions"
        versions_dir.mkdir()
        
        # Create env.py
        env_py = migrations_dir / "env.py"
        env_content = (
            "from logging.config import fileConfig\n\n"
            "from sqlalchemy import engine_from_config\n"
            "from sqlalchemy import pool\n\n"
            "from alembic import context\n\n"
            "from models.base import Base\n\n"
            "config = context.config\n"
            "fileConfig(config.config_file_name)\n"
            "target_metadata = Base.metadata\n\n"
            "def run_migrations_offline():\n"
            "    url = config.get_main_option(\"sqlalchemy.url\")\n"
            "    context.configure(\n"
            "        url=url,\n"
            "        target_metadata=target_metadata,\n"
            "        literal_binds=True,\n"
            "        dialect_opts={\"paramstyle\": \"named\"},\n"
            "    )\n\n"
            "    with context.begin_transaction():\n"
            "        context.run_migrations()\n\n"
            "def run_migrations_online():\n"
            "    connectable = engine_from_config(\n"
            "        config.get_section(config.config_ini_section),\n"
            "        prefix=\"sqlalchemy.\",\n"
            "        poolclass=pool.NullPool,\n"
            "    )\n\n"
            "    with connectable.connect() as connection:\n"
            "        context.configure(\n"
            "            connection=connection,\n"
            "            target_metadata=target_metadata\n"
            "        )\n\n"
            "        with context.begin_transaction():\n"
            "            context.run_migrations()\n\n"
            "if context.is_offline_mode():\n"
            "    run_migrations_offline()\n"
            "else:\n"
            "    run_migrations_online()\n"
        )
        with open(env_py, "w") as f:
            f.write(env_content)
            
        # Create script.py.mako
        script_mako = migrations_dir / "script.py.mako"
        with open(script_mako, "w") as f:
            f.write("""\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
""")
        
        # Create alembic config object
        config = Config(str(config_path))
        config.set_main_option("script_location", str(migrations_dir))
        
        yield config


@pytest.fixture
def test_db():
    """Create a test database."""
    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
        db_url = f"sqlite:///{temp_db.name}"
        engine = create_engine(db_url)
        
        # Create session factory
        Session = sessionmaker(bind=engine)
        
        yield {
            "url": db_url,
            "engine": engine,
            "session_factory": Session
        }


def test_create_migration(alembic_config, test_db):
    """Test creating a new migration."""
    # Set database URL in alembic config
    alembic_config.set_main_option("sqlalchemy.url", test_db["url"])
    
    # Create a new migration
    command.revision(
        alembic_config,
        message="create tables",
        autogenerate=True
    )
    
    # Get migration script
    script = ScriptDirectory.from_config(alembic_config)
    revisions = list(script.walk_revisions())
    
    # Should have one revision
    assert len(revisions) == 1
    
    # Revision should have upgrade and downgrade functions
    with open(revisions[0].path) as f:
        content = f.read()
        assert "def upgrade()" in content
        assert "def downgrade()" in content


def test_apply_migration(alembic_config, test_db):
    """Test applying a migration."""
    # Set database URL in alembic config
    alembic_config.set_main_option("sqlalchemy.url", test_db["url"])
    
    # Create and apply a migration
    command.revision(alembic_config, message="create tables", autogenerate=True)
    command.upgrade(alembic_config, "head")
    
    # Verify tables were created
    inspector = test_db["engine"].dialect.inspector
    tables = inspector.get_table_names()
    
    # Should have our core tables
    assert "email_messages" in tables
    assert "email_analyses" in tables
    assert "gmail_labels" in tables


def test_rollback_migration(alembic_config, test_db):
    """Test rolling back a migration."""
    # Set database URL in alembic config
    alembic_config.set_main_option("sqlalchemy.url", test_db["url"])
    
    # Create and apply a migration
    command.revision(alembic_config, message="create tables", autogenerate=True)
    command.upgrade(alembic_config, "head")
    
    # Roll back the migration
    command.downgrade(alembic_config, "-1")
    
    # Verify tables were removed
    inspector = test_db["engine"].dialect.inspector
    tables = inspector.get_table_names()
    
    # Tables should be gone
    assert "email_messages" not in tables
    assert "email_analyses" not in tables
    assert "gmail_labels" not in tables


def test_concurrent_migrations(alembic_config, test_db):
    """Test concurrent migrations."""
    # Set database URL in alembic config
    alembic_config.set_main_option("sqlalchemy.url", test_db["url"])
    
    # Create two migrations
    command.revision(alembic_config, message="create tables", autogenerate=True)
    command.revision(alembic_config, message="add indexes", autogenerate=True)
    
    # Get migration scripts
    script = ScriptDirectory.from_config(alembic_config)
    revisions = list(script.walk_revisions())
    
    # Should have two revisions
    assert len(revisions) == 2
    
    # Apply migrations concurrently (simulated)
    session1 = test_db["session_factory"]()
    session2 = test_db["session_factory"]()
    
    try:
        # Start transaction 1
        with session1.begin():
            command.upgrade(alembic_config, "+1")
            
            # Start transaction 2 (should wait for transaction 1)
            with session2.begin():
                command.upgrade(alembic_config, "+1")
                
            # Verify final state
            inspector = test_db["engine"].dialect.inspector
            tables = inspector.get_table_names()
            
            # Should have our core tables with indexes
            assert "email_messages" in tables
            assert "email_analyses" in tables
            assert "gmail_labels" in tables
            
            # Check for indexes (implementation-specific)
            for table in tables:
                indexes = inspector.get_indexes(table)
                assert len(indexes) > 0
    finally:
        session1.close()
        session2.close()
