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
import sqlite3
from lib_gmail import GmailAPI
from app_email_analyzer import EmailAnalyzer
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from jinja2 import Template
from dateutil import parser
import numpy as np
from textblob import TextBlob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSelfAnalyzer:
    def __init__(self, db_path: str = "email_store.db"):
        self.db_path = db_path
        self.analyzer = EmailAnalyzer()
        self.user_email = self._get_user_email()
        
    def _get_user_email(self) -> str:
        """Get the user's email address from Gmail profile."""
        gmail = GmailAPI()
        profile = gmail.service.users().getProfile(userId='me').execute()
        return profile['emailAddress']

    def _get_db_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(self.db_path)

    def get_self_emails(self, days: int = None) -> List[Dict[str, Any]]:
        """Get self-emails from the database."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, thread_id, subject, sender, recipient, date, body, labels
            FROM emails 
            WHERE sender LIKE ? AND recipient LIKE ?
        """
        params = [f"%{self.user_email}%", f"%{self.user_email}%"]

        if days:
            query += " AND date >= datetime('now', ?)"
            params.append(f'-{days} days')

        query += " ORDER BY date DESC"
        
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        emails = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return emails

    def analyze_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze the content of each email."""
        analyzed_emails = []
        
        for email in emails:
            # Skip emails without content
            if not email['body']:
                continue

            # Get AI analysis
            analysis = self.analyzer.analyze_email(
                subject=email['subject'] or '',
                body=email['body'] or ''
            )

            # Add sentiment analysis
            blob = TextBlob(email['body'])
            sentiment = blob.sentiment.polarity

            analyzed_email = {
                'id': email['id'],
                'thread_id': email['thread_id'],
                'date': email['date'],
                'subject': email['subject'],
                'content': email['body'],
                'labels': email['labels'],
                'analysis': analysis,
                'sentiment': sentiment
            }
            analyzed_emails.append(analyzed_email)

        return analyzed_emails

    def cluster_by_time(self, emails: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """Group emails by time periods."""
        time_clusters = defaultdict(lambda: {"count": 0, "emails": []})
        
        for email in emails:
            date = parser.parse(email['date']).date()
            time_clusters[str(date)]["count"] += 1
            time_clusters[str(date)]["emails"].append(email)
            
        return dict(time_clusters)

    def generate_html_report(self, analyzed_emails: List[Dict[str, Any]], 
                           time_clusters: Dict[str, Dict]) -> str:
        """Generate an HTML report with visualizations."""
        # Convert to DataFrame for analysis
        df = pd.DataFrame(analyzed_emails)
        df['date'] = pd.to_datetime(df['date'])
        
        # Create visualizations
        email_volume = px.line(
            df.groupby(df['date'].dt.date).size().reset_index(),
            x='date',
            y=0,
            title='Email Volume Over Time'
        )
        
        # Sentiment over time
        sentiment_df = df.copy()
        sentiment_df['date'] = sentiment_df['date'].dt.date
        sentiment_plot = px.scatter(
            sentiment_df,
            x='date',
            y='sentiment',
            title='Sentiment Analysis Over Time'
        )
        
        # Load and render template
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'email_report.html')
        with open(template_path, 'r') as f:
            template = Template(f.read())
            
        return template.render(
            emails=analyzed_emails,
            clusters=time_clusters,
            plots={
                'email_volume': email_volume.to_html(full_html=False),
                'sentiment': sentiment_plot.to_html(full_html=False)
            }
        )

def main():
    analyzer = EmailSelfAnalyzer()
    
    # Get self-emails from the last 30 days
    logger.info("Fetching self-emails from database...")
    emails = analyzer.get_self_emails(days=30)
    
    if not emails:
        logger.warning("No self-emails found in the database")
        return
        
    logger.info(f"Found {len(emails)} self-emails")
    
    # Analyze emails
    logger.info("Analyzing emails...")
    analyzed_emails = analyzer.analyze_emails(emails)
    
    # Cluster by time
    logger.info("Clustering emails by time...")
    time_clusters = analyzer.cluster_by_time(analyzed_emails)
    
    # Generate report
    logger.info("Generating HTML report...")
    report = analyzer.generate_html_report(analyzed_emails, time_clusters)
    
    # Save report
    report_path = "self_email_report.html"
    with open(report_path, "w") as f:
        f.write(report)
    
    logger.info(f"Report saved to {report_path}")

if __name__ == '__main__':
    main()
