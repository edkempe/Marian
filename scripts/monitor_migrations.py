#!/usr/bin/env python3
"""CLI tool for migration monitoring.

This script provides commands for:
1. Running monitoring cycles
2. Checking database health
3. Viewing migration metrics
4. Managing alerts
"""

import argparse
import json
import logging
import sys
import time
from typing import Dict, Any

from shared_lib.database_session_util import (
    get_email_engine,
    get_analysis_engine,
)
from shared_lib.migration_monitor import MigrationMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_argparse() -> argparse.ArgumentParser:
    """Set up argument parser."""
    parser = argparse.ArgumentParser(
        description="Monitor database migrations"
    )
    
    parser.add_argument(
        "--slack-webhook",
        help="Slack webhook URL for alerts"
    )
    parser.add_argument(
        "--email-config",
        help="JSON file with email configuration"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # monitor command
    monitor = subparsers.add_parser(
        "monitor",
        help="Run monitoring cycle"
    )
    monitor.add_argument(
        "--continuous",
        action="store_true",
        help="Run monitoring continuously"
    )
    monitor.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Monitoring interval in seconds (default: 300)"
    )
    
    # health command
    health = subparsers.add_parser(
        "health",
        help="Check database health"
    )
    
    # metrics command
    metrics = subparsers.add_parser(
        "metrics",
        help="View migration metrics"
    )
    
    # alerts command
    alerts = subparsers.add_parser(
        "alerts",
        help="Generate and view alerts"
    )
    alerts.add_argument(
        "--send",
        action="store_true",
        help="Send generated alerts"
    )
    
    return parser

def load_email_config(config_file: str) -> Dict[str, str]:
    """Load email configuration from file."""
    try:
        with open(config_file) as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load email config: {str(e)}")
        return {}

def handle_monitor(monitor: MigrationMonitor, args) -> int:
    """Handle monitor command."""
    try:
        if args.continuous:
            logger.info(f"Starting continuous monitoring (interval: {args.interval}s)")
            while True:
                monitor.run_monitoring()
                time.sleep(args.interval)
        else:
            monitor.run_monitoring()
        return 0
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Monitoring failed: {str(e)}")
        return 1

def handle_health(monitor: MigrationMonitor, args) -> int:
    """Handle health command."""
    try:
        for engine in monitor.engines.values():
            health = monitor.check_database_health(engine)
            logger.info(f"\nHealth check for {engine.url.database}:")
            logger.info(json.dumps(health, indent=2))
        return 0
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return 1

def handle_metrics(monitor: MigrationMonitor, args) -> int:
    """Handle metrics command."""
    try:
        for engine in monitor.engines.values():
            metrics = monitor.get_migration_metrics(engine)
            logger.info(f"\nMigration metrics for {engine.url.database}:")
            logger.info(json.dumps(metrics, indent=2))
        return 0
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        return 1

def handle_alerts(monitor: MigrationMonitor, args) -> int:
    """Handle alerts command."""
    try:
        alerts = monitor.generate_alerts()
        
        if not alerts:
            logger.info("No alerts generated")
            return 0
            
        logger.info(f"Generated {len(alerts)} alerts:")
        for alert in alerts:
            logger.info(f"\nAlert: {alert.message}")
            logger.info(f"Level: {alert.level.value}")
            logger.info(f"Database: {alert.database}")
            logger.info(f"Details: {json.dumps(alert.details, indent=2)}")
            
        if args.send:
            monitor.process_alerts(alerts)
            
        return 0
    except Exception as e:
        logger.error(f"Failed to handle alerts: {str(e)}")
        return 1

def main() -> int:
    """Main entry point."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    # Set up monitor
    engines = {
        "email": get_email_engine(),
        "analysis": get_analysis_engine(),
    }
    
    email_config = {}
    if args.email_config:
        email_config = load_email_config(args.email_config)
        
    monitor = MigrationMonitor(
        engines=engines,
        slack_webhook=args.slack_webhook,
        email_config=email_config,
    )
    
    handlers = {
        "monitor": handle_monitor,
        "health": handle_health,
        "metrics": handle_metrics,
        "alerts": handle_alerts,
    }
    
    return handlers[args.command](monitor, args)

if __name__ == "__main__":
    sys.exit(main())
