"""Utilities for managing database schema migrations.

This module provides utilities for:
1. Generating migrations from schema changes
2. Resolving migration conflicts
3. Validating migrations against configuration
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.exc import OperationalError
import sqlite3

from shared_lib.schema_constants import COLUMN_SIZES, EmailDefaults, AnalysisDefaults, LabelDefaults
from shared_lib.database_session_util import email_engine, analysis_engine
from models.registry import Base

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
    results = {"valid": True, "errors": [], "warnings": []}
    
    try:
        # Get all tables from models
        model_tables = Base.metadata.tables
        
        # Check each table against configuration
        for table_name, table in model_tables.items():
            # Get expected column sizes from COLUMN_SIZES
            table_prefix = table_name.upper()
            
            # Check columns
            for column in table.columns:
                if hasattr(column.type, "length"):
                    col_name = f"{table_prefix}_{column.name.upper()}"
                    
                    # Check if column size is defined
                    if col_name not in COLUMN_SIZES:
                        results["warnings"].append(
                            f"Column size not defined: {col_name} in schema constants"
                        )
                        continue
                        
                    expected_size = COLUMN_SIZES[col_name]
                    actual_size = column.type.length
                    
                    # Validate column size
                    if expected_size < 0:
                        results["errors"].append(
                            f"Invalid column size defined: {col_name} has negative size {expected_size}"
                        )
                        results["valid"] = False
                    elif actual_size != expected_size:
                        results["errors"].append(
                            f"Column size mismatch: {col_name} expected {expected_size}, got {actual_size}"
                        )
                        results["valid"] = False
                        
        # Validate foreign key relationships
        for table_name, table in model_tables.items():
            for fk in table.foreign_keys:
                if not fk.column.table in model_tables:
                    results["errors"].append(
                        f"Invalid foreign key in {table_name}: references non-existent table {fk.column.table}"
                    )
                    results["valid"] = False
                    
    except Exception as e:
        results["errors"].append(f"Schema validation failed: {str(e)}")
        results["valid"] = False
        
    return results

def generate_migration(message: str, autogenerate: bool = True) -> Optional[str]:
    """Generate new migration.
    
    Args:
        message: Migration message
        autogenerate: Whether to autogenerate migration from models
        
    Returns:
        Revision ID if successful, None otherwise
        
    Raises:
        ValueError: If message is empty or invalid
    """
    if not message or not message.strip():
        raise ValueError("Migration message cannot be empty")
        
    try:
        config = get_alembic_config(email_engine)
        script = ScriptDirectory.from_config(config)
        
        template_args = {
            "config": config
        }
        
        if autogenerate:
            # Get current database schema
            with email_engine.connect() as connection:
                context = MigrationContext.configure(connection)
                template_args["target_metadata"] = Base.metadata
                
        revision = script.generate_revision(
            message,
            autogenerate=autogenerate,
            **template_args
        )
        
        return revision.revision
    except Exception as e:
        logger.error(f"Failed to generate migration: {str(e)}")
        return None

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
                opts={"target_metadata": Base.metadata}
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
