"""Alembic environment configuration."""

import os
from logging.config import fileConfig
from typing import Dict, List

from alembic import context
from sqlalchemy import engine_from_config, pool

from models.base import Base
from shared_lib.database_session_util import get_database_url

# Import all models to ensure they are registered with Base.metadata
from models.email_message import EmailMessage
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel
from models.catalog_item import CatalogItem
from models.tag import Tag
from models.item_relationship import ItemRelationship

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get database URL
url = get_database_url()

def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    context.configure(
        url=url,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in online mode."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
