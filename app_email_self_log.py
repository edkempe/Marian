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
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import logging
from sqlalchemy.orm import Session

from models.email import Email
from models.email_analysis import EmailAnalysis
from database.config import get_email_session, get_analysis_session
from utils.logging_config import setup_logging, log_error
from config.constants import DATABASE_CONFIG, EMAIL_CONFIG
from app_email_analyzer import EmailAnalyzer
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from jinja2 import Template
from dateutil import parser
import numpy as np
from textblob import TextBlob

logger = setup_logging(__name__)

class EmailSelfAnalyzer:
    """Analyzes self-sent emails for personal knowledge management."""

    def __init__(self):
        """Initialize the analyzer with database configuration."""
        self.analyzer = EmailAnalyzer()
        self.user_email = self._get_user_email()
        
    def _get_user_email(self) -> str:
        """Get the user's email address from Gmail profile."""
        gmail = GmailAPI()
        profile = gmail.service.users().getProfile(userId='me').execute()
        return profile['emailAddress']

    def _get_db_connection(self) -> Session:
        """Get a database connection."""
        return get_email_session()

    def get_self_emails(self, days: int = None) -> List[Dict[str, Any]]:
        """Get self-emails from the database."""
        session = self._get_db_connection()
        query = session.query(Email).filter(Email.sender == self.user_email, Email.recipient == self.user_email)
        
        if days:
            query = query.filter(Email.date >= datetime.now() - timedelta(days=days))
        
        emails = query.order_by(Email.date.desc()).all()
        session.close()
        
        return [email.to_dict() for email in emails]

    def analyze_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze the content of each email."""
        analyzed_emails = []
        
        with get_analysis_session() as session:
            for email in emails:
                # Check if analysis already exists
                existing = session.query(EmailAnalysis).filter_by(email_id=email['id']).first()
                
                if existing:
                    analysis = existing.to_dict()
                else:
                    # Get new analysis
                    analysis = self.analyzer.analyze_email(email)
                    if analysis:
                        session.add(EmailAnalysis(**analysis))
                        session.commit()
                
                if analysis:
                    email.update(analysis)
                    analyzed_emails.append(email)
                    
        return analyzed_emails

    def cluster_by_time(self, emails: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """Group emails by time periods."""
        clusters = {
            'today': {'emails': [], 'topics': defaultdict(int)},
            'this_week': {'emails': [], 'topics': defaultdict(int)},
            'this_month': {'emails': [], 'topics': defaultdict(int)},
            'older': {'emails': [], 'topics': defaultdict(int)}
        }
        
        now = datetime.now()
        
        for email in emails:
            email_date = datetime.strptime(email['date'], '%Y-%m-%d %H:%M:%S')
            
            # Determine time period
            if email_date.date() == now.date():
                period = 'today'
            elif email_date > now - timedelta(days=7):
                period = 'this_week'
            elif email_date > now - timedelta(days=30):
                period = 'this_month'
            else:
                period = 'older'
            
            clusters[period]['emails'].append(email)
            
            # Update topic counts
            if 'topics' in email:
                for topic in email['topics']:
                    clusters[period]['topics'][topic] += 1
        
        return clusters

    def generate_html_report(self, analyzed_emails: List[Dict[str, Any]], 
                           time_clusters: Dict[str, Dict]) -> str:
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
            for email in data['emails'][:5]:  # Show only top 5
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
        with open('email_self_log_report.html', 'w') as f:
            f.write(report)
        
        logger.info("Report generated: email_self_log_report.html")
        
    except Exception as e:
        log_error(logger, 'main_error', e)
        raise

if __name__ == '__main__':
    main()
