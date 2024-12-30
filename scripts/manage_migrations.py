#!/usr/bin/env python3
"""CLI tool for managing database migrations.

This script provides commands for:
1. Generating new migrations
2. Applying pending migrations
3. Viewing migration history
4. Validating schema changes
"""

import argparse
import logging
import sys
from typing import List, Optional

from shared_lib.migration_utils import (
    generate_migration,
    apply_migrations,
    get_migration_history,
    get_pending_migrations,
    validate_schema_changes,
)
from shared_lib.database_session_util import email_engine, analysis_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_argparse() -> argparse.ArgumentParser:
    """Set up argument parser."""
    parser = argparse.ArgumentParser(
        description="Manage database migrations"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # generate command
    generate = subparsers.add_parser(
        "generate",
        help="Generate new migration"
    )
    generate.add_argument(
        "message",
        help="Migration message"
    )
    generate.add_argument(
        "--empty",
        action="store_true",
        help="Create empty migration instead of auto-generating"
    )
    
    # apply command
    apply = subparsers.add_parser(
        "apply",
        help="Apply pending migrations"
    )
    
    # validate command
    validate = subparsers.add_parser(
        "validate",
        help="Validate schema changes"
    )
    
    # history command
    history = subparsers.add_parser(
        "history",
        help="Show migration history"
    )
    
    # pending command
    pending = subparsers.add_parser(
        "pending",
        help="Show pending migrations"
    )
    
    return parser

def handle_generate(args) -> int:
    """Handle generate command."""
    revision = generate_migration(args.message, not args.empty)
    if revision:
        logger.info(f"Generated migration {revision}")
        return 0
    return 1

def handle_apply(args) -> int:
    """Handle apply command."""
    success = True
    for engine in [email_engine, analysis_engine]:
        if not apply_migrations(engine):
            success = False
    return 0 if success else 1

def handle_validate(args) -> int:
    """Handle validate command."""
    results = validate_schema_changes()
    
    if results["valid"]:
        logger.info("Schema validation passed!")
        if results["warnings"]:
            logger.warning("Warnings:")
            for warning in results["warnings"]:
                logger.warning(f"  - {warning}")
        return 0
    
    logger.error("Schema validation failed:")
    for error in results["errors"]:
        logger.error(f"  - {error}")
    return 1

def handle_history(args) -> int:
    """Handle history command."""
    for engine in [email_engine, analysis_engine]:
        logger.info(f"\nMigration history for {engine.url.database}:")
        history = get_migration_history(engine)
        
        if not history:
            logger.info("  No migrations found")
            continue
            
        for entry in history:
            current = " (current)" if entry["is_current"] else ""
            logger.info(
                f"  {entry['revision']}{current}: {entry['message']}"
            )
    return 0

def handle_pending(args) -> int:
    """Handle pending command."""
    has_pending = False
    for engine in [email_engine, analysis_engine]:
        logger.info(f"\nPending migrations for {engine.url.database}:")
        pending = get_pending_migrations(engine)
        
        if not pending:
            logger.info("  No pending migrations")
            continue
            
        has_pending = True
        for revision in pending:
            logger.info(f"  - {revision}")
    
    return 1 if has_pending else 0

def main() -> int:
    """Main entry point."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    handlers = {
        "generate": handle_generate,
        "apply": handle_apply,
        "validate": handle_validate,
        "history": handle_history,
        "pending": handle_pending,
    }
    
    return handlers[args.command](args)

if __name__ == "__main__":
    sys.exit(main())
