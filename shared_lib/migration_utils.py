"""Utilities for managing database schema migrations.

This module provides utilities for:
1. Generating migrations from schema changes
2. Resolving migration conflicts
3. Validating migrations against configuration
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, MetaData, Table, inspect

from shared_lib.config_loader import load_schema_config
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
    config = load_schema_config()
    results = {"valid": True, "errors": [], "warnings": []}
    
    # Get all tables from models
    model_tables = Base.metadata.tables
    
    # Check each table against configuration
    for table_name, table in model_tables.items():
        table_config = getattr(config, table_name, None)
        if not table_config:
            results["errors"].append(f"Table {table_name} not found in configuration")
            results["valid"] = False
            continue
            
        # Check columns
        for column in table.columns:
            col_name = column.name
            col_config = getattr(table_config, col_name, None)
            if not col_config:
                results["errors"].append(
                    f"Column {col_name} in table {table_name} not found in configuration"
                )
                results["valid"] = False
                continue
                
            # Check types match
            model_type = str(column.type)
            config_type = col_config.type
            if model_type.lower() != config_type.lower():
                results["errors"].append(
                    f"Type mismatch for {table_name}.{col_name}: "
                    f"model={model_type}, config={config_type}"
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

def apply_migrations(engine) -> bool:
    """Apply pending migrations.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config = get_alembic_config(engine)
        command.upgrade(config, "head")
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
