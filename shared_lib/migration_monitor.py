"""Migration monitoring and alerting system.

This module provides:
1. Migration status monitoring
2. Performance metrics
3. Alert generation
4. Slack notifications
5. Email notifications
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional, Union

import requests
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from shared_lib.migration_utils import (
    get_current_revision,
    get_pending_migrations,
    get_revision_history,
)

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MigrationAlert:
    """Migration alert data."""
    level: AlertLevel
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    database: str

class MigrationMonitor:
    """Migration monitoring system."""

    def __init__(
        self,
        engines: Dict[str, Engine],
        slack_webhook: Optional[str] = None,
        email_config: Optional[Dict[str, str]] = None
    ):
        """Initialize monitor.
        
        Args:
            engines: Dictionary of database engines
            slack_webhook: Optional Slack webhook URL
            email_config: Optional email configuration
        """
        self.engines = engines
        self.slack_webhook = slack_webhook or os.getenv("SLACK_WEBHOOK_URL")
        self.email_config = email_config or {
            "smtp_host": os.getenv("SMTP_HOST", "localhost"),
            "smtp_port": os.getenv("SMTP_PORT", "587"),
            "smtp_user": os.getenv("SMTP_USER"),
            "smtp_pass": os.getenv("SMTP_PASS"),
            "from_email": os.getenv("ALERT_FROM_EMAIL"),
            "to_email": os.getenv("ALERT_TO_EMAIL"),
        }
        
    def check_database_health(self, engine: Engine) -> Dict[str, Any]:
        """Check database health.
        
        Args:
            engine: SQLAlchemy engine
            
        Returns:
            Health check results
        """
        start_time = time.time()
        results = {
            "database": engine.url.database,
            "connected": False,
            "tables": [],
            "current_revision": None,
            "pending_migrations": [],
            "response_time_ms": 0,
        }
        
        try:
            # Test connection
            with engine.connect() as conn:
                results["connected"] = True
                
                # Get tables
                inspector = inspect(engine)
                results["tables"] = inspector.get_table_names()
                
                # Get migration status
                results["current_revision"] = get_current_revision(engine)
                results["pending_migrations"] = get_pending_migrations(engine)
                
        except Exception as e:
            logger.error(f"Health check failed for {engine.url.database}: {str(e)}")
            results["error"] = str(e)
            
        results["response_time_ms"] = int((time.time() - start_time) * 1000)
        return results
    
    def get_migration_metrics(self, engine: Engine) -> Dict[str, Any]:
        """Get migration performance metrics.
        
        Args:
            engine: SQLAlchemy engine
            
        Returns:
            Migration metrics
        """
        metrics = {
            "database": engine.url.database,
            "total_migrations": 0,
            "pending_migrations": 0,
            "latest_migration": None,
            "migration_history": [],
        }
        
        try:
            history = get_revision_history(engine)
            metrics["total_migrations"] = len(history)
            metrics["migration_history"] = history
            
            if history:
                metrics["latest_migration"] = history[0]
                
            pending = get_pending_migrations(engine)
            metrics["pending_migrations"] = len(pending)
            
        except Exception as e:
            logger.error(f"Failed to get metrics for {engine.url.database}: {str(e)}")
            metrics["error"] = str(e)
            
        return metrics
    
    def generate_alerts(self) -> List[MigrationAlert]:
        """Generate alerts based on current state."""
        alerts = []
        
        for name, engine in self.engines.items():
            # Check health
            health = self.check_database_health(engine)
            if not health["connected"]:
                alerts.append(MigrationAlert(
                    level=AlertLevel.CRITICAL,
                    message=f"Database {name} is not connected",
                    details=health,
                    timestamp=datetime.now(timezone.utc),
                    database=name,
                ))
                continue
                
            # Check pending migrations
            if health["pending_migrations"]:
                alerts.append(MigrationAlert(
                    level=AlertLevel.WARNING,
                    message=f"Database {name} has {len(health['pending_migrations'])} pending migrations",
                    details={"pending": health["pending_migrations"]},
                    timestamp=datetime.now(timezone.utc),
                    database=name,
                ))
                
            # Check response time
            if health["response_time_ms"] > 1000:
                alerts.append(MigrationAlert(
                    level=AlertLevel.WARNING,
                    message=f"Database {name} response time is high: {health['response_time_ms']}ms",
                    details={"response_time": health["response_time_ms"]},
                    timestamp=datetime.now(timezone.utc),
                    database=name,
                ))
                
        return alerts
    
    def send_slack_alert(self, alert: MigrationAlert) -> bool:
        """Send alert to Slack.
        
        Args:
            alert: Alert to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.slack_webhook:
            logger.warning("Slack webhook URL not configured")
            return False
            
        try:
            color = {
                AlertLevel.INFO: "#36a64f",
                AlertLevel.WARNING: "#ffd700",
                AlertLevel.ERROR: "#ff4444",
                AlertLevel.CRITICAL: "#ff0000",
            }[alert.level]
            
            payload = {
                "attachments": [{
                    "color": color,
                    "title": f"Migration Alert: {alert.message}",
                    "text": json.dumps(alert.details, indent=2),
                    "fields": [
                        {
                            "title": "Database",
                            "value": alert.database,
                            "short": True,
                        },
                        {
                            "title": "Level",
                            "value": alert.level.value,
                            "short": True,
                        },
                        {
                            "title": "Timestamp",
                            "value": alert.timestamp.isoformat(),
                            "short": True,
                        },
                    ],
                }]
            }
            
            response = requests.post(
                self.slack_webhook,
                json=payload,
                timeout=5,
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}")
            return False
    
    def send_email_alert(self, alert: MigrationAlert) -> bool:
        """Send alert via email.
        
        Args:
            alert: Alert to send
            
        Returns:
            True if successful, False otherwise
        """
        if not all([
            self.email_config["smtp_host"],
            self.email_config["from_email"],
            self.email_config["to_email"],
        ]):
            logger.warning("Email configuration incomplete")
            return False
            
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg["Subject"] = f"Migration Alert: {alert.message}"
            msg["From"] = self.email_config["from_email"]
            msg["To"] = self.email_config["to_email"]
            
            body = f"""
            Migration Alert
            ---------------
            Level: {alert.level.value}
            Database: {alert.database}
            Message: {alert.message}
            Timestamp: {alert.timestamp.isoformat()}
            
            Details:
            {json.dumps(alert.details, indent=2)}
            """
            
            msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(
                self.email_config["smtp_host"],
                int(self.email_config["smtp_port"]),
            ) as server:
                if self.email_config["smtp_user"]:
                    server.login(
                        self.email_config["smtp_user"],
                        self.email_config["smtp_pass"],
                    )
                server.send_message(msg)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            return False
    
    def process_alerts(self, alerts: List[MigrationAlert]) -> None:
        """Process and send alerts.
        
        Args:
            alerts: List of alerts to process
        """
        for alert in alerts:
            logger.info(f"Processing alert: {alert.message}")
            
            # Send to Slack
            if alert.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
                self.send_slack_alert(alert)
                
            # Send via email
            if alert.level == AlertLevel.CRITICAL:
                self.send_email_alert(alert)
    
    def run_monitoring(self) -> None:
        """Run monitoring cycle."""
        logger.info("Starting migration monitoring cycle")
        
        try:
            # Generate alerts
            alerts = self.generate_alerts()
            
            # Process alerts
            self.process_alerts(alerts)
            
            # Log metrics
            for engine in self.engines.values():
                metrics = self.get_migration_metrics(engine)
                logger.info(f"Migration metrics for {engine.url.database}:")
                logger.info(json.dumps(metrics, indent=2))
                
        except Exception as e:
            logger.error(f"Monitoring cycle failed: {str(e)}")
            
        logger.info("Completed migration monitoring cycle")
