#!/usr/bin/env python3
"""CLI tool for seeding databases with test data.

This script provides commands for:
1. Seeding individual tables
2. Seeding all tables
3. Cleaning up seeded data
4. Using custom seed files
"""

import argparse
import logging
import sys
from typing import Optional

from shared_lib.database_seeder import DatabaseSeeder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_argparse() -> argparse.ArgumentParser:
    """Set up argument parser."""
    parser = argparse.ArgumentParser(
        description="Seed databases with test data"
    )
    
    parser.add_argument(
        "--env",
        default="development",
        help="Environment (development, test, etc.)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # emails command
    emails = subparsers.add_parser(
        "emails",
        help="Seed email data"
    )
    emails.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of emails to generate"
    )
    emails.add_argument(
        "--seed-file",
        help="Seed file to use"
    )
    
    # analysis command
    analysis = subparsers.add_parser(
        "analysis",
        help="Seed email analysis data"
    )
    analysis.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of analyses to generate"
    )
    analysis.add_argument(
        "--seed-file",
        help="Seed file to use"
    )
    
    # labels command
    labels = subparsers.add_parser(
        "labels",
        help="Seed Gmail label data"
    )
    labels.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of labels to generate"
    )
    labels.add_argument(
        "--seed-file",
        help="Seed file to use"
    )
    
    # all command
    all_cmd = subparsers.add_parser(
        "all",
        help="Seed all data"
    )
    all_cmd.add_argument(
        "--email-count",
        type=int,
        default=10,
        help="Number of emails to generate"
    )
    all_cmd.add_argument(
        "--label-count",
        type=int,
        default=5,
        help="Number of labels to generate"
    )
    all_cmd.add_argument(
        "--seed-file",
        help="Seed file to use"
    )
    
    # cleanup command
    cleanup = subparsers.add_parser(
        "cleanup",
        help="Clean up seeded data"
    )
    
    return parser

def handle_emails(seeder: DatabaseSeeder, args) -> int:
    """Handle emails command."""
    try:
        emails = seeder.seed_emails(args.count, args.seed_file)
        logger.info(f"Created {len(emails)} emails")
        return 0
    except Exception as e:
        logger.error(f"Failed to seed emails: {str(e)}")
        return 1

def handle_analysis(seeder: DatabaseSeeder, args) -> int:
    """Handle analysis command."""
    try:
        analyses = seeder.seed_analysis(count=args.count, seed_file=args.seed_file)
        logger.info(f"Created {len(analyses)} analyses")
        return 0
    except Exception as e:
        logger.error(f"Failed to seed analyses: {str(e)}")
        return 1

def handle_labels(seeder: DatabaseSeeder, args) -> int:
    """Handle labels command."""
    try:
        labels = seeder.seed_labels(args.count, args.seed_file)
        logger.info(f"Created {len(labels)} labels")
        return 0
    except Exception as e:
        logger.error(f"Failed to seed labels: {str(e)}")
        return 1

def handle_all(seeder: DatabaseSeeder, args) -> int:
    """Handle all command."""
    try:
        results = seeder.seed_all(
            args.email_count,
            args.label_count,
            args.seed_file
        )
        logger.info(
            f"Created {len(results['emails'])} emails, "
            f"{len(results['analyses'])} analyses, "
            f"and {len(results['labels'])} labels"
        )
        return 0
    except Exception as e:
        logger.error(f"Failed to seed all data: {str(e)}")
        return 1

def handle_cleanup(seeder: DatabaseSeeder, args) -> int:
    """Handle cleanup command."""
    try:
        seeder.cleanup()
        logger.info("Cleaned up all seeded data")
        return 0
    except Exception as e:
        logger.error(f"Failed to cleanup data: {str(e)}")
        return 1

def main() -> int:
    """Main entry point."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    seeder = DatabaseSeeder(args.env)
    
    handlers = {
        "emails": handle_emails,
        "analysis": handle_analysis,
        "labels": handle_labels,
        "all": handle_all,
        "cleanup": handle_cleanup,
    }
    
    return handlers[args.command](seeder, args)

if __name__ == "__main__":
    sys.exit(main())
