#!/usr/bin/env python3
"""
Email Self-Log Analyzer
----------------------
Analyzes self-sent emails from the email database with advanced analysis and organization.
Includes time-based clustering, sentiment analysis, topic evolution, and HTML report generation.

This module uses the same database as app_get_mail.py but focuses on analyzing
emails that were sent to oneself, which often represent notes, reminders, or
personal documentation.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dateutil import parser
from jinja2 import Template
from sqlalchemy.orm import Session
from textblob import TextBlob

from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from shared_lib.constants import DATABASE_CONFIG, EMAIL_CONFIG
from shared_lib.database_session_util import get_analysis_session, get_email_session
from shared_lib.gmail_lib import GmailAPI
from shared_lib.logging_util import log_error, setup_logging

from .app_email_analyzer import EmailAnalyzer

logger = setup_logging(__name__)


class EmailSelfAnalyzer:
    """Analyzer for self-emails (emails sent to oneself)."""

    def __init__(self):
        """Initialize the analyzer."""
        self.gmail = GmailAPI()
        self.user_email = self._get_user_email()
        self.analyzer = EmailAnalyzer()

    def _get_user_email(self) -> str:
        """Get the user's email address from Gmail API."""
        profile = self.gmail.service.users().getProfile(userId="me").execute()
        return profile["emailAddress"]

    def get_self_emails(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get self-emails from the database."""
        with get_email_session() as session:
            # Print debug info
            print(f"Looking for emails from/to: {self.user_email}")

            query = session.query(EmailMessage).filter(
                EmailMessage.from_address == self.user_email,
                EmailMessage.to_address == self.user_email,
            )

            if days:
                cutoff = datetime.now() - timedelta(days=days)
                query = query.filter(EmailMessage.received_date >= cutoff)

            # Print debug info
            print(f"Total emails in database: {session.query(EmailMessage).count()}")
            print(f"Self-emails found: {query.count()}")

            emails = query.all()
            return [email.__dict__ for email in emails]

    def analyze_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze the content of each email."""
        results = []

        with get_analysis_session() as session:
            for email in emails:
                analysis = self.analyzer.analyze_email(email)
                if analysis:
                    if isinstance(analysis, dict):
                        results.append(analysis)
                    else:
                        results.append(analysis.__dict__)

            return results

    def run_analysis(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Run complete analysis on self-emails."""
        emails = self.get_self_emails(days)
        return self.analyze_emails(emails)

    def cluster_by_time(self, emails: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """Group emails by time periods."""
        clusters = {
            "today": {"emails": [], "topics": {}},
            "this_week": {"emails": [], "topics": {}},
            "this_month": {"emails": [], "topics": {}},
            "older": {"emails": [], "topics": {}},
        }

        now = datetime.now()

        for email in emails:
            email_date = datetime.strptime(email["date"], "%Y-%m-%d %H:%M:%S")

            # Determine time period
            if email_date.date() == now.date():
                period = "today"
            elif email_date > now - timedelta(days=7):
                period = "this_week"
            elif email_date > now - timedelta(days=30):
                period = "this_month"
            else:
                period = "older"

            clusters[period]["emails"].append(email)

            # Update topic counts
            if "topics" in email:
                for topic in email["topics"]:
                    clusters[period]["topics"][topic] = (
                        clusters[period]["topics"].get(topic, 0) + 1
                    )

        return clusters

    def generate_html_report(
        self, analyzed_emails: List[Dict[str, Any]], time_clusters: Dict[str, Dict]
    ) -> str:
        """Generate an HTML report with visualizations."""
        # Convert emails to DataFrame for analysis
        df = pd.DataFrame(analyzed_emails)

        # Create visualizations
        topic_fig = self._create_topic_evolution(df)
        sentiment_fig = self._create_sentiment_analysis(df)
        cluster_fig = self._create_cluster_visualization(time_clusters)

        # Generate HTML
        html = f"""
        <html>
        <head>
            <title>Email Self-Log Analysis</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body class="container mt-5">
            <h1>Email Self-Log Analysis</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <h2>Topic Evolution</h2>
            {topic_fig.to_html(full_html=False)}

            <h2>Sentiment Analysis</h2>
            {sentiment_fig.to_html(full_html=False)}

            <h2>Time Clusters</h2>
            {cluster_fig.to_html(full_html=False)}

            <h2>Recent Emails by Period</h2>
            {self._generate_email_summaries(time_clusters)}
        </body>
        </html>
        """

        return html

    def _create_topic_evolution(self, df: pd.DataFrame) -> go.Figure:
        """Create topic evolution visualization."""
        # Implementation details...
        pass

    def _create_sentiment_analysis(self, df: pd.DataFrame) -> go.Figure:
        """Create sentiment analysis visualization."""
        # Implementation details...
        pass

    def _create_cluster_visualization(self, clusters: Dict[str, Dict]) -> go.Figure:
        """Create cluster visualization."""
        # Implementation details...
        pass

    def _generate_email_summaries(self, clusters: Dict[str, Dict]) -> str:
        """Generate HTML summaries of emails by time period."""
        html = ""
        for period, data in clusters.items():
            html += f"<h3>{period.replace('_', ' ').title()}</h3>"
            html += "<ul>"
            for email in data["emails"][:5]:  # Show only top 5
                html += f"""
                <li>
                    <strong>{email['subject']}</strong><br>
                    <small>{email['date']}</small><br>
                    <em>Topics: {', '.join(email.get('topics', []))}</em>
                </li>
                """
            html += "</ul>"
        return html


def main():
    """Main entry point."""
    try:
        analyzer = EmailSelfAnalyzer()

        # Get and analyze emails from the last 30 days
        logger.info("Fetching self-emails from the last 30 days")
        emails = analyzer.get_self_emails(days=30)

        if not emails:
            logger.warning("No self-emails found in the specified time period")
            return

        logger.info(f"Found {len(emails)} self-emails")

        # Analyze emails
        logger.info("Analyzing emails")
        analyzed_emails = analyzer.analyze_emails(emails)

        # Cluster by time
        logger.info("Clustering emails by time period")
        time_clusters = analyzer.cluster_by_time(analyzed_emails)

        # Generate report
        logger.info("Generating HTML report")
        report = analyzer.generate_html_report(analyzed_emails, time_clusters)

        # Save report
        with open("email_self_log_report.html", "w") as f:
            f.write(report)

        logger.info("Report generated: email_self_log_report.html")

    except Exception as e:
        log_error(logger, "main_error", e)
        raise


if __name__ == "__main__":
    main()
