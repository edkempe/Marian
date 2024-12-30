#!/usr/bin/env python3
"""CLI tool for managing database migrations.

This script provides commands for:
1. Generating new migrations
2. Applying pending migrations
3. Viewing migration history
4. Validating schema changes
5. Rolling back migrations
"""

import argparse
import logging
import sys
from typing import List, Optional

from shared_lib.migration_utils import (
    get_alembic_config,
    get_current_revision,
    get_pending_migrations,
    validate_schema_changes,
    generate_migration,
    apply_migrations,
    get_migration_history,
    rollback_migration,
    rollback_to_revision,
    get_revision_history,
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
        help="Create empty migration"
    )
    
    # apply command
    apply = subparsers.add_parser(
        "apply",
        help="Apply pending migrations"
    )
    apply.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate migration without applying changes"
    )
    apply.add_argument(
        "--target",
        help="Target revision to migrate to"
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
    history.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed history"
    )
    
    # pending command
    pending = subparsers.add_parser(
        "pending",
        help="Show pending migrations"
    )
    
    # rollback command
    rollback = subparsers.add_parser(
        "rollback",
        help="Roll back migrations"
    )
    rollback.add_argument(
        "--steps",
        type=int,
        default=1,
        help="Number of migrations to roll back"
    )
    rollback.add_argument(
        "--revision",
        help="Target revision to roll back to"
    )
    rollback.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate rollback without applying changes"
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
        logger.info(f"\nApplying migrations for {engine.url.database}:")
        
        if args.dry_run:
            results = apply_migrations(
                engine,
                dry_run=True,
                target_revision=args.target
            )
            
            if not results["success"]:
                logger.error(f"Migration simulation failed: {results['error']}")
                success = False
                continue
                
            logger.info(f"Current revision: {results['current_revision']}")
            logger.info(f"Target revision: {results['target_revision']}")
            
            if not results["changes"]:
                logger.info("No changes to apply")
                continue
                
            logger.info("\nChanges to apply:")
            for change in results["changes"]:
                logger.info(f"\nRevision {change['revision']}: {change['message']}")
                for op in change["operations"]:
                    logger.info(f"  - {op['type']}: {op['args']} {op['kwargs']}")
                    
        else:
            result = apply_migrations(
                engine,
                dry_run=False,
                target_revision=args.target
            )
            if not result:
                logger.error(f"Failed to apply migrations to {engine.url.database}")
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
    if args.detailed:
        email_history = get_revision_history(email_engine)
        analysis_history = get_revision_history(analysis_engine)
        
        logger.info("Email database revision history:")
        for rev in email_history:
            logger.info(
                f"  {rev['revision']}: {rev['message']} "
                f"(current: {rev['is_current']}, "
                f"down_revision: {rev['down_revision']})"
            )
        
        logger.info("\nAnalysis database revision history:")
        for rev in analysis_history:
            logger.info(
                f"  {rev['revision']}: {rev['message']} "
                f"(current: {rev['is_current']}, "
                f"down_revision: {rev['down_revision']})"
            )
    else:
        email_history = get_migration_history(email_engine)
        analysis_history = get_migration_history(analysis_engine)
        
        logger.info("Email database revision history:")
        for rev in email_history:
            logger.info(f"  {rev['revision']}: {rev['message']}")
        
        logger.info("\nAnalysis database revision history:")
        for rev in analysis_history:
            logger.info(f"  {rev['revision']}: {rev['message']}")
    
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

def handle_rollback(args) -> int:
    """Handle rollback command."""
    success = True
    
    if args.revision:
        logger.info(f"Rolling back to revision {args.revision}")
        success &= rollback_to_revision(email_engine, args.revision)
        success &= rollback_to_revision(analysis_engine, args.revision)
    else:
        logger.info(f"Rolling back {args.steps} migration(s)")
        success &= rollback_migration(email_engine, args.steps)
        success &= rollback_migration(analysis_engine, args.steps)
    
    return 0 if success else 1

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
        "rollback": handle_rollback,
    }
    
    return handlers[args.command](args)

if __name__ == "__main__":
    sys.exit(main())
