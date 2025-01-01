"""Alembic environment configuration."""

import os
from logging.config import fileConfig
from typing import Dict, List

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from alembic import context

# Import our models and config
from models.registry import Base
from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel
from config.test_settings import test_settings
from shared_lib.constants import DATABASE_CONFIG
from shared_lib.database_session_util import create_session_factory

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Get the appropriate database URL based on environment
def get_database_url() -> str:
    """Get database URL based on environment."""
    if test_settings.TEST_MODE:
        return test_settings.DATABASE_URLS["email"]
    return DATABASE_CONFIG["email"]["url"]

# Set the database URL
config.set_main_option("sqlalchemy.url", get_database_url())

# Configure SQLAlchemy connection pool
config.set_section_option(
    config.config_ini_section,
    "sqlalchemy.pool_size",
    str(test_settings.DATABASE_MAX_CONNECTIONS)
)
config.set_section_option(
    config.config_ini_section,
    "sqlalchemy.pool_recycle",
    str(test_settings.DATABASE_POOL_RECYCLE)
)
config.set_section_option(
    config.config_ini_section,
    "sqlalchemy.pool_timeout",
    str(test_settings.DATABASE_TIMEOUT)
)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def include_object(object, name: str, type_: str, reflected: bool, compare_to) -> bool:
    """Filter objects to include in autogeneration."""
    # Only include tables from our models
    if type_ == "table":
        return object.metadata is target_metadata
    return True

def process_revision_directives(context, revision, directives) -> None:
    """Process revision directives to improve migration quality."""
    # Prevent empty migrations
    if config.cmd_opts and config.cmd_opts.autogenerate:
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        process_revision_directives=process_revision_directives,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Create engine with appropriate configuration
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.QueuePool if not test_settings.TEST_MODE else pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            process_revision_directives=process_revision_directives,
            compare_type=True,
            compare_server_default=True,
            transaction_per_migration=True,
        )

        try:
            with context.begin_transaction():
                context.run_migrations()
        except Exception as e:
            # Log any migration errors
            import logging
            logger = logging.getLogger("alembic")
            logger.error(f"Migration failed: {str(e)}")
            raise


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
