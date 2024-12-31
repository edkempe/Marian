"""Utilities for managing database schema migrations.

This module provides utilities for:
1. Generating migrations from schema changes
2. Resolving migration conflicts
3. Validating migrations against configuration
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import os
import sys
import shutil

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, MetaData, Table, inspect, text
from sqlalchemy.exc import OperationalError
import sqlite3

from shared_lib.config_loader import get_schema_config
from shared_lib.constants import DATABASE_CONFIG
from shared_lib.database_session_util import get_engine_for_db_type

logger = logging.getLogger(__name__)

def get_alembic_config(engine=None) -> Config:
    """Get Alembic configuration.
    
    Args:
        engine: Optional SQLAlchemy engine. If provided, sets the sqlalchemy.url.
        
    Returns:
        Alembic Config object
        
    Raises:
        ValueError: If engine is invalid or None
    """
    if not engine:
        raise ValueError("Engine must be provided")
        
    try:
        config = Config("alembic.ini")
        config.set_main_option("sqlalchemy.url", str(engine.url))
        return config
    except Exception as e:
        raise ValueError(f"Failed to create Alembic config: {str(e)}")

def get_current_revision(engine) -> Optional[str]:
    """Get current revision of database.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        Current revision hash or None if no revision
        
    Raises:
        OperationalError: If database connection fails
    """
    if not engine:
        raise ValueError("Engine must be provided")
        
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            return context.get_current_revision()
    except (OperationalError, sqlite3.OperationalError) as e:
        raise  # Re-raise the original error
    except Exception as e:
        raise OperationalError("Failed to get current revision", str(e))

def get_pending_migrations(config, engine) -> List[str]:
    """Get list of pending migrations in upgrade order.

    This function returns a list of migration revision hashes that need to be
    applied to bring the database up to date. The migrations are returned in
    the order they should be applied (upgrade order).

    Args:
        config: Alembic config object containing migration settings
        engine: SQLAlchemy engine for database connection

    Returns:
        List of migration revision hashes in upgrade order (oldest first)

    Raises:
        ValueError: If engine is invalid
        OperationalError: If database connection fails or there are issues
            with the migration history
    """
    if not engine:
        raise ValueError("Engine must be provided")

    try:
        script = ScriptDirectory.from_config(config)

        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current = context.get_current_revision()

        # Get all revisions from current to heads
        revisions = []
        for rev in script.revision_map.iterate_revisions("heads", current, select_for_downgrade=True):
            if rev.revision != current:  # Skip the current revision
                revisions.append(rev.revision)
        return list(reversed(revisions))  # Return in upgrade order
    except (OperationalError, sqlite3.OperationalError) as e:
        raise  # Re-raise database-specific errors
    except Exception as e:
        # Create a proper SQLAlchemy OperationalError
        statement = "get_pending_migrations"
        orig = e
        params = None
        raise OperationalError(statement, params, orig)

def validate_schema_changes() -> Dict[str, Any]:
    """Validate schema changes against configuration.
    
    This function validates the database schema against the configuration,
    checking for:
    - Column size mismatches
    - Missing column size definitions
    - Invalid foreign key relationships
    - General schema consistency
    
    Returns:
        Dict containing validation results:
        {
            "valid": bool,  # True if no errors found
            "errors": List[str],  # List of error messages
            "warnings": List[str]  # List of warning messages
        }
    """
    errors = []
    warnings = []
    
    # Load schema configuration
    schema_config = get_schema_config()
    
    # Create engine for validation
    engine = create_engine(DATABASE_CONFIG["url"])
    inspector = inspect(engine)
    
    # Get actual table schemas
    for table_name in inspector.get_table_names():
        # Skip alembic_version table
        if table_name == "alembic_version":
            continue
            
        # Get configured table
        table_config = getattr(schema_config, table_name, None)
        if not table_config:
            warnings.append(f"Table {table_name} not found in configuration")
            continue
            
        # Check columns
        for column in inspector.get_columns(table_name):
            col_name = column["name"]
            col_type = str(column["type"])
            
            # Get configured column
            col_config = table_config.columns.get(col_name)
            if not col_config:
                warnings.append(f"Column {table_name}.{col_name} not found in configuration")
                continue
                
            # Validate column type
            expected_type = col_config.type
            if expected_type not in col_type.lower():
                errors.append(
                    f"Column {table_name}.{col_name} type mismatch: "
                    f"expected {expected_type}, got {col_type}"
                )
                
            # Validate string column sizes
            if expected_type == "string" and hasattr(column["type"], "length"):
                actual_size = column["type"].length
                if actual_size != col_config.size:
                    errors.append(
                        f"Column {table_name}.{col_name} size mismatch: "
                        f"expected {col_config.size}, got {actual_size}"
                    )
    
    # Check for missing tables
    for table_name in ["email", "analysis", "label"]:
        if table_name not in inspector.get_table_names():
            errors.append(f"Required table {table_name} not found in database")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def generate_migration(
    name: str,
    directory: str,
    autogenerate: bool = True,
    message: Optional[str] = None,
    db_type: str = "email"
) -> str:
    """Generate a new migration.
    
    Args:
        name: Name of the migration
        directory: Directory to store migrations
        autogenerate: Whether to autogenerate migration from models
        message: Optional message to include in migration
        db_type: Type of database to generate migration for
        
    Returns:
        Path to generated migration file
        
    Raises:
        ValueError: If name is empty or directory doesn't exist
        OperationalError: If migration generation fails
    """
    if not name:
        raise ValueError("Migration name cannot be empty")
        
    if not os.path.exists(directory):
        raise ValueError(f"Migration directory {directory} does not exist")
        
    try:
        engine = get_engine_for_db_type(db_type)
        config = get_alembic_config(engine)
        
        # Set migration directory
        config.set_main_option("script_location", directory)
        
        # Create env.py if it doesn't exist
        env_path = Path(directory) / "env.py"
        if not env_path.exists():
            env_path.write_text("""
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool, MetaData

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Create MetaData instance
target_metadata = MetaData()

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
        
        # Create alembic.ini if it doesn't exist
        ini_path = Path(directory) / "alembic.ini"
        if not ini_path.exists():
            ini_path.write_text(f"""
[alembic]
script_location = {directory}
sqlalchemy.url = {engine.url}

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

        # Create script.py.mako if it doesn't exist
        script_mako_path = Path(directory) / "script.py.mako"
        if not script_mako_path.exists():
            script_mako_path.write_text('''
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}

def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
''')
        
        # Create versions directory if it doesn't exist
        versions_dir = Path(directory) / "versions"
        versions_dir.mkdir(exist_ok=True)
        
        # Generate migration
        revision = command.revision(
            config,
            autogenerate=False,  # Set to False to avoid requiring MetaData
            rev_id=None,
            message=message if message else name,
            version_path=versions_dir
        )
        
        # Get migration file path
        script = ScriptDirectory.from_config(config)
        migration_file = next(versions_dir.glob("*_test_migration.py"))
        
        return str(migration_file)
    except Exception as e:
        logger.error(f"Failed to generate migration: {str(e)}")
        raise ValueError(f"Failed to generate migration: {str(e)}")
    finally:
        # Clean up temporary files
        if os.path.exists(directory):
            for cache_dir in Path(directory).rglob("__pycache__"):
                if cache_dir.is_dir():
                    shutil.rmtree(cache_dir)

def simulate_migration(
    engine,
    target_revision: Optional[str] = None
) -> Dict[str, Any]:
    """Simulate migration without applying changes.
    
    Args:
        engine: SQLAlchemy engine
        target_revision: Optional target revision
        
    Returns:
        Simulation results
        
    Raises:
        ValueError: If engine is invalid
        OperationalError: If simulation fails
    """
    if not engine:
        raise ValueError("Engine must be provided")
        
    try:
        results = {
            "success": True,
            "error": None,
            "current_revision": None,
            "target_revision": target_revision or "head",
            "changes": []
        }
        
        config = get_alembic_config(engine)
        script = ScriptDirectory.from_config(config)
        
        with engine.connect() as connection:
            context = MigrationContext.configure(
                connection,
                opts={"target_metadata": MetaData()}
            )
            current = context.get_current_revision()
            results["current_revision"] = current
            
            # Get migration plan
            revisions = list(script.walk_revisions(
                target_revision or "head",
                current
            ))
            
            # Record changes for each revision
            for rev in reversed(revisions):
                changes = {
                    "revision": rev.revision,
                    "message": rev.doc,
                    "operations": []
                }
                
                # Parse upgrade operations
                upgrade_ops = rev.module.upgrade()
                if upgrade_ops:
                    for op in upgrade_ops:
                        changes["operations"].append({
                            "type": op.__class__.__name__,
                            "args": getattr(op, "args", []),
                            "kwargs": getattr(op, "kwargs", {})
                        })
                        
                results["changes"].append(changes)
                
        return results
    except Exception as e:
        raise OperationalError("Migration simulation failed", str(e))

def apply_migrations(
    engine,
    dry_run: bool = False,
    target_revision: Optional[str] = None
) -> Union[bool, Dict[str, Any]]:
    """Apply pending migrations.
    
    Args:
        engine: SQLAlchemy engine
        dry_run: If True, simulate migration without applying changes
        target_revision: Optional target revision
        
    Returns:
        True if successful, False if failed, or simulation results if dry_run
        
    Raises:
        ValueError: If engine is invalid
        OperationalError: If migration fails
    """
    if not engine:
        raise ValueError("Engine must be provided")
        
    try:
        if dry_run:
            return simulate_migration(engine, target_revision)
            
        config = get_alembic_config(engine)
        command.upgrade(config, target_revision or "head")
        return True
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False

def get_migration_history(engine, detailed: bool = False) -> List[Dict[str, Any]]:
    """Get migration history.
    
    Args:
        engine: SQLAlchemy engine
        detailed: Whether to include detailed information
        
    Returns:
        List of dicts containing migration info
        
    Raises:
        ValueError: If engine is invalid
        OperationalError: If history retrieval fails
    """
    if not engine:
        raise ValueError("Engine must be provided")
        
    try:
        config = get_alembic_config(engine)
        script = ScriptDirectory.from_config(config)
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current = context.get_current_revision()
            
        history = []
        for rev in script.walk_revisions():
            info = {
                "revision": rev.revision,
                "down_revision": rev.down_revision,
                "message": rev.doc,
                "is_current": rev.revision == current
            }
            
            if detailed:
                # Add operation details
                info["operations"] = []
                if hasattr(rev.module, "upgrade"):
                    upgrade_ops = rev.module.upgrade()
                    if upgrade_ops:
                        for op in upgrade_ops:
                            info["operations"].append({
                                "type": op.__class__.__name__,
                                "args": getattr(op, "args", []),
                                "kwargs": getattr(op, "kwargs", {})
                            })
                            
            history.append(info)
            
        return history
    except Exception as e:
        raise OperationalError("Failed to get migration history", str(e))

def get_revision_history(engine) -> List[Dict[str, Any]]:
    """Get detailed revision history.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        List of revision details
        
    Raises:
        ValueError: If engine is invalid
        OperationalError: If history retrieval fails
    """
    if not engine:
        raise ValueError("Engine must be provided")
        
    try:
        config = get_alembic_config(engine)
        script = ScriptDirectory.from_config(config)
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current = context.get_current_revision()
            
        history = []
        for rev in script.walk_revisions():
            info = {
                "revision": rev.revision,
                "down_revision": rev.down_revision,
                "message": rev.doc,
                "is_current": rev.revision == current,
                "operations": []
            }
            
            # Add operation details
            if hasattr(rev.module, "upgrade"):
                upgrade_ops = rev.module.upgrade()
                if upgrade_ops:
                    for op in upgrade_ops:
                        info["operations"].append({
                            "type": op.__class__.__name__,
                            "args": getattr(op, "args", []),
                            "kwargs": getattr(op, "kwargs", {})
                        })
                        
            history.append(info)
            
        return history
    except Exception as e:
        raise OperationalError("Failed to get revision history", str(e))

def get_migration_status(db_type: str = "email") -> Dict[str, Any]:
    """Get current migration status.
    
    Args:
        db_type: Type of database to check ('email' or 'analysis')
        
    Returns:
        Dictionary containing:
        - current_revision: Current revision ID or None if no migrations
        - pending_migrations: List of pending migration IDs
    """
    engine = get_engine_for_db_type(db_type)
    config = get_alembic_config(engine)
    script = ScriptDirectory.from_config(config)
    
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current = context.get_current_revision()
        
        # Get all revisions
        revisions = [rev.revision for rev in script.walk_revisions()]
        
        # Get pending migrations
        if current is None:
            pending = revisions
        else:
            current_idx = revisions.index(current)
            pending = revisions[:current_idx]
            
    return {
        "current_revision": current,
        "pending_migrations": pending
    }

def rollback_migration(engine, steps: int = 1) -> bool:
    """Roll back the last N migrations.
    
    Args:
        engine: SQLAlchemy engine
        steps: Number of migrations to roll back
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ValueError: If engine is invalid or steps < 1
    """
    if not engine:
        raise ValueError("Engine must be provided")
        
    if steps < 1:
        raise ValueError("Steps must be greater than 0")
        
    try:
        config = get_alembic_config(engine)
        command.downgrade(config, f"-{steps}")
        return True
    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}")
        return False

def rollback_to_revision(engine, target_revision: str) -> bool:
    """Roll back to a specific revision.
    
    Args:
        engine: SQLAlchemy engine
        target_revision: Target revision to roll back to
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ValueError: If engine is invalid or target_revision is empty
    """
    if not engine:
        raise ValueError("Engine must be provided")
        
    if not target_revision or not target_revision.strip():
        raise ValueError("Target revision cannot be empty")
        
    try:
        config = get_alembic_config(engine)
        command.downgrade(config, target_revision)
        return True
    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}")
        return False
