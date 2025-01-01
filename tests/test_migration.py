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
        with open(config_path, "w") as f:
            f.write("""
[alembic]
script_location = migrations
sqlalchemy.url = sqlite:///%(here)s/test.db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
            """)
            
        # Create migrations directory
        migrations_dir = Path(temp_dir) / "migrations"
        migrations_dir.mkdir()
        
        # Create versions directory
        versions_dir = migrations_dir / "versions"
        versions_dir.mkdir()
        
        # Create env.py
        env_py = migrations_dir / "env.py"
        with open(env_py, "w") as f:
            f.write("""
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from models.base import Base

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

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
            
        # Create script.py.mako
        script_mako = migrations_dir / "script.py.mako"
        with open(script_mako, "w") as f:
            f.write("""
"""Revision: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
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
    
    # Create and apply migration
    command.revision(
        alembic_config,
        message="create tables",
        autogenerate=True
    )
    command.upgrade(alembic_config, "head")
    
    # Check that tables were created
    with test_db["engine"].connect() as conn:
        tables = conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)).fetchall()
        table_names = {t[0] for t in tables}
        
        assert "email_messages" in table_names
        assert "email_analyses" in table_names
        assert "gmail_labels" in table_names
        assert "email_labels" in table_names


def test_rollback_migration(alembic_config, test_db):
    """Test rolling back a migration."""
    # Set database URL in alembic config
    alembic_config.set_main_option("sqlalchemy.url", test_db["url"])
    
    # Create and apply migration
    command.revision(
        alembic_config,
        message="create tables",
        autogenerate=True
    )
    command.upgrade(alembic_config, "head")
    
    # Rollback migration
    command.downgrade(alembic_config, "-1")
    
    # Check that tables were dropped
    with test_db["engine"].connect() as conn:
        tables = conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)).fetchall()
        table_names = {t[0] for t in tables}
        
        assert "email_messages" not in table_names
        assert "email_analyses" not in table_names
        assert "gmail_labels" not in table_names
        assert "email_labels" not in table_names


def test_concurrent_migrations(alembic_config, test_db):
    """Test concurrent migrations."""
    # Set database URL in alembic config
    alembic_config.set_main_option("sqlalchemy.url", test_db["url"])
    
    # Create first migration
    command.revision(
        alembic_config,
        message="create email tables",
        autogenerate=True
    )
    
    # Create second migration
    command.revision(
        alembic_config,
        message="create label tables",
        autogenerate=True
    )
    
    # Apply migrations
    command.upgrade(alembic_config, "+1")  # Apply first migration
    
    # Check that email tables exist but not label tables
    with test_db["engine"].connect() as conn:
        tables = conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)).fetchall()
        table_names = {t[0] for t in tables}
        
        assert "email_messages" in table_names
        assert "email_analyses" in table_names
        assert "gmail_labels" not in table_names
        assert "email_labels" not in table_names
    
    # Apply second migration
    command.upgrade(alembic_config, "+1")
    
    # Check that all tables exist
    with test_db["engine"].connect() as conn:
        tables = conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)).fetchall()
        table_names = {t[0] for t in tables}
        
        assert "email_messages" in table_names
        assert "email_analyses" in table_names
        assert "gmail_labels" in table_names
        assert "email_labels" in table_names
