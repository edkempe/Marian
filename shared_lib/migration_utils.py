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
    """
    config = Config("alembic.ini")
    if engine:
        config.set_main_option("sqlalchemy.url", str(engine.url))
    return config

def get_current_revision(engine) -> str:
    """Get current revision of database.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        Current revision hash or None if no revision
    """
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        return context.get_current_revision()

def get_pending_migrations(engine) -> List[str]:
    """Get list of pending migrations.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        List of pending migration revision hashes
    """
    config = get_alembic_config(engine)
    script = ScriptDirectory.from_config(config)
    
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current = context.get_current_revision()
        
    def _get_revs(upper, lower):
        return [rev for rev in script.walk_revisions(upper, lower)]
        
    return [rev.revision for rev in _get_revs("heads", current)]

def validate_schema_changes() -> Dict[str, Any]:
    """Validate schema changes against configuration.
    
    Returns:
        Dict containing validation results:
        {
            "valid": bool,
            "errors": List[str],
            "warnings": List[str]
        }
    """
    results = {"valid": True, "errors": [], "warnings": []}
    
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
                if col_name not in COLUMN_SIZES:
                    results["warnings"].append(f"Column {col_name} size not defined in schema constants")
                    continue
                
                expected_size = COLUMN_SIZES[col_name]
                actual_size = column.type.length
                
                if actual_size != expected_size:
                    results["errors"].append(
                        f"Column {table_name}.{column.name} size mismatch: "
                        f"expected {expected_size}, got {actual_size}"
                    )
                    results["valid"] = False
    
    return results

def generate_migration(message: str, autogenerate: bool = True) -> Optional[str]:
    """Generate new migration.
    
    Args:
        message: Migration message
        autogenerate: Whether to autogenerate migration from models
        
    Returns:
        Revision ID if successful, None otherwise
    """
    # First validate schema changes
    validation = validate_schema_changes()
    if not validation["valid"]:
        logger.error("Schema validation failed:")
        for error in validation["errors"]:
            logger.error(f"  - {error}")
        return None
        
    try:
        config = get_alembic_config()
        if autogenerate:
            # Create revision with --autogenerate
            command.revision(config, message=message, autogenerate=True)
        else:
            # Create empty revision
            command.revision(config, message=message)
            
        script = ScriptDirectory.from_config(config)
        return script.get_current_head()
        
    except Exception as e:
        logger.error(f"Failed to generate migration: {str(e)}")
        return None

def simulate_migration(engine, target_revision: Optional[str] = None) -> Dict[str, Any]:
    """Simulate migration without applying changes.
    
    Args:
        engine: SQLAlchemy engine
        target_revision: Optional target revision
        
    Returns:
        Simulation results
    """
    try:
        config = get_alembic_config(engine)
        script = ScriptDirectory.from_config(config)
        
        # Get current and target revisions
        current = get_current_revision(engine)
        if not target_revision:
            target_revision = script.get_current_head()
            
        # Get revisions to apply
        revisions = []
        for rev in script.walk_revisions(current, target_revision):
            revisions.append({
                "revision": rev.revision,
                "down_revision": rev.down_revision,
                "message": rev.doc,
                "module": rev.module.__file__,
                "dependencies": rev.dependencies,
                "branch_labels": rev.branch_labels,
            })
            
        # Analyze changes
        changes = []
        for rev in revisions:
            module = script.get_revision(rev["revision"]).module
            
            # Extract upgrade operations
            upgrade_ops = []
            for op in getattr(module, "upgrade"):
                if hasattr(op, "_orig_args"):
                    upgrade_ops.append({
                        "type": op.__class__.__name__,
                        "args": op._orig_args,
                        "kwargs": op._orig_kwargs,
                    })
            
            changes.append({
                "revision": rev["revision"],
                "message": rev["message"],
                "operations": upgrade_ops,
            })
            
        return {
            "current_revision": current,
            "target_revision": target_revision,
            "revisions": revisions,
            "changes": changes,
            "success": True,
        }
        
    except Exception as e:
        logger.error(f"Migration simulation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
        }

def apply_migrations(engine, dry_run: bool = False, target_revision: Optional[str] = None) -> Union[bool, Dict[str, Any]]:
    """Apply pending migrations.
    
    Args:
        engine: SQLAlchemy engine
        dry_run: If True, simulate migration without applying changes
        target_revision: Optional target revision
        
    Returns:
        True if successful, False if failed, or simulation results if dry_run
    """
    try:
        if dry_run:
            return simulate_migration(engine, target_revision)
            
        config = get_alembic_config(engine)
        command.upgrade(config, target_revision or "head")
        return True
        
    except Exception as e:
        logger.error(f"Failed to apply migrations: {str(e)}")
        return False

def get_migration_history(engine) -> List[Dict[str, Any]]:
    """Get migration history.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        List of dicts containing migration info
    """
    config = get_alembic_config(engine)
    script = ScriptDirectory.from_config(config)
    
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current = context.get_current_revision()
    
    history = []
    for rev in script.walk_revisions():
        history.append({
            "revision": rev.revision,
            "down_revision": rev.down_revision,
            "message": rev.doc,
            "is_current": rev.revision == current
        })
    
    return history

def rollback_migration(engine, steps: int = 1) -> bool:
    """Roll back the last N migrations.
    
    Args:
        engine: SQLAlchemy engine
        steps: Number of migrations to roll back
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config = get_alembic_config(engine)
        command.downgrade(config, f"-{steps}")
        return True
    except Exception as e:
        logger.error(f"Failed to roll back migrations: {str(e)}")
        return False

def rollback_to_revision(engine, target_revision: str) -> bool:
    """Roll back to a specific revision.
    
    Args:
        engine: SQLAlchemy engine
        target_revision: Target revision to roll back to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config = get_alembic_config(engine)
        command.downgrade(config, target_revision)
        return True
    except Exception as e:
        logger.error(f"Failed to roll back to revision {target_revision}: {str(e)}")
        return False

def get_revision_history(engine) -> List[Dict[str, Any]]:
    """Get detailed revision history.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        List of revision details
    """
    try:
        config = get_alembic_config(engine)
        script = ScriptDirectory.from_config(config)
        
        # Get current revision
        current = get_current_revision(engine)
        
        history = []
        for rev in script.walk_revisions():
            history.append({
                "revision": rev.revision,
                "down_revision": rev.down_revision,
                "message": rev.doc,
                "is_current": rev.revision == current,
                "created_at": rev.module.__file__,
                "dependencies": rev.dependencies,
                "branch_labels": rev.branch_labels,
            })
        
        return history
    except Exception as e:
        logger.error(f"Failed to get revision history: {str(e)}")
        return []
