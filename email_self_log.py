#!/usr/bin/env python3
"""
Email Self-Log Generator
-----------------------
Creates a comprehensive log of all self-sent emails with advanced analysis and organization.
Includes time-based clustering, sentiment analysis, topic evolution, and HTML report generation.
"""

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import logging
from gmail_lib import GmailAPI
from email_analyzer import EmailProcessor, verify_environment, get_api_key
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from jinja2 import Template
from dateutil import parser
import numpy as np
from textblob import TextBlob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSelfLogger:
    def __init__(self):
        verify_environment()
        self.gmail_api = GmailAPI()
        api_key = get_api_key()
        self.email_processor = EmailProcessor(api_key=api_key)
        self.user_email = self._get_user_email()
        
    def _get_user_email(self) -> str:
        """Get the user's email address from Gmail profile."""
        profile = self.gmail_api.service.users().getProfile(userId='me').execute()
        return profile['emailAddress']

    def fetch_self_emails(self, max_results: int = None) -> List[Dict[str, Any]]:
        """Fetch all emails sent to self."""
        query = f'from:{self.user_email} to:{self.user_email}'
        messages = []
        
        try:
            response = self.gmail_api.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response and (max_results is None or len(messages) < max_results):
                page_token = response['nextPageToken']
                response = self.gmail_api.service.users().messages().list(
                    userId='me',
                    q=query,
                    pageToken=page_token,
                    maxResults=max_results
                ).execute()
                if 'messages' in response:
                    messages.extend(response['messages'])

            return messages
        except Exception as e:
            logger.error(f"Error fetching self-emails: {str(e)}")
            return []

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text using TextBlob."""
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }

    def process_emails(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process each email and extract relevant information with enhanced analysis."""
        processed_emails = []
        total = len(messages)

        for idx, message in enumerate(messages, 1):
            try:
                logger.info(f"Processing email {idx}/{total}")
                msg_data = self.gmail_api.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                # Extract headers
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), None)
                date = parser.parse(date_str) if date_str else None
                
                # Get message content
                email_data = self.gmail_api.process_email(message['id'])
                if not email_data:
                    logger.error(f"Error processing message {message['id']}")
                    continue

                # Extract content from processed email
                content = email_data['body']
                
                # Enhanced analysis
                analysis = self.email_processor.analyze_email(
                    email_id=message['id'],
                    subject=subject,
                    sender=self.user_email,
                    date=date_str if date_str else "",
                    body=content
                )
                sentiment = self.analyze_sentiment(content)
                
                processed_email = {
                    'id': message['id'],
                    'date': date.isoformat() if date else None,
                    'subject': subject,
                    'content': content,
                    'analysis': analysis,
                    'sentiment': sentiment,
                    'labels': msg_data.get('labelIds', []),
                    'thread_id': msg_data.get('threadId'),
                    'timestamp': date.timestamp() if date else None
                }

                # Extract action items and deadlines
                if 'actions_required' in analysis:
                    processed_email['action_items'] = analysis['actions_required']
                if 'deadlines' in analysis:
                    processed_email['deadlines'] = analysis['deadlines']

                processed_emails.append(processed_email)

            except Exception as e:
                logger.error(f"Error processing message {message['id']}: {str(e)}")
                continue

        return processed_emails

    def cluster_by_time(self, emails: List[Dict[str, Any]], window_days: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """Cluster emails by time periods."""
        if not emails:
            return {}

        # Sort emails by timestamp
        sorted_emails = sorted(emails, key=lambda x: x['timestamp'] or 0)
        
        clusters = defaultdict(list)
        current_start = datetime.fromtimestamp(sorted_emails[0]['timestamp'])
        
        for email in sorted_emails:
            email_date = datetime.fromtimestamp(email['timestamp'])
            if (email_date - current_start).days > window_days:
                current_start = email_date
            
            cluster_key = current_start.strftime('%Y-%m-%d')
            clusters[cluster_key].append(email)

        return dict(clusters)

    def analyze_topic_evolution(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze how topics evolve over time."""
        topic_timeline = []
        
        # Sort emails by date
        sorted_emails = sorted(emails, key=lambda x: x['timestamp'] or 0)
        
        # Track topic frequency over time
        topic_freq = defaultdict(list)
        
        for email in sorted_emails:
            date = datetime.fromtimestamp(email['timestamp'])
            if 'analysis' in email and 'key_topics' in email['analysis']:
                for topic in email['analysis']['key_topics']:
                    topic_freq[topic].append({
                        'date': date.isoformat(),
                        'count': 1
                    })

        # Aggregate topic frequency by month
        for topic, occurrences in topic_freq.items():
            df = pd.DataFrame(occurrences)
            df['date'] = pd.to_datetime(df['date'])
            monthly = df.set_index('date').resample('M')['count'].sum()
            
            topic_timeline.append({
                'topic': topic,
                'timeline': [
                    {'date': date.isoformat(), 'count': count}
                    for date, count in monthly.items()
                ]
            })

        return topic_timeline

    def generate_html_report(self, data: Dict[str, Any], output_file: str = 'email_report.html'):
        """Generate an HTML report with visualizations."""
        # Convert data to pandas DataFrame for easier manipulation
        emails_df = pd.DataFrame([
            {
                'date': email['date'],
                'subject': email['subject'],
                'sentiment': email['sentiment']['polarity'],
                'topics': ', '.join(email['analysis'].get('key_topics', [])),
                'importance': email['analysis'].get('importance', 'medium')
            }
            for email in data['all_emails']
        ])

        # Create visualizations using plotly
        sentiment_fig = px.line(
            emails_df, 
            x='date', 
            y='sentiment',
            title='Sentiment Analysis Over Time'
        )

        # Topic distribution pie chart
        topic_counts = defaultdict(int)
        for email in data['all_emails']:
            for topic in email['analysis'].get('key_topics', []):
                topic_counts[topic] += 1

        topics_fig = px.pie(
            values=list(topic_counts.values()),
            names=list(topic_counts.keys()),
            title='Topic Distribution'
        )

        # Generate HTML template
        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email Self-Analysis Report</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .section { margin-bottom: 30px; }
                .chart { margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Email Self-Analysis Report</h1>
                <div class="section">
                    <h2>Summary</h2>
                    <p>Total Emails: {{ total_emails }}</p>
                    <p>Date Range: {{ date_range }}</p>
                </div>
                
                <div class="section">
                    <h2>Sentiment Analysis</h2>
                    <div class="chart" id="sentiment-chart"></div>
                </div>

                <div class="section">
                    <h2>Topic Distribution</h2>
                    <div class="chart" id="topics-chart"></div>
                </div>

                <div class="section">
                    <h2>Recent Action Items</h2>
                    <table>
                        <tr>
                            <th>Date</th>
                            <th>Subject</th>
                            <th>Action Required</th>
                        </tr>
                        {% for item in action_items %}
                        <tr>
                            <td>{{ item.date }}</td>
                            <td>{{ item.subject }}</td>
                            <td>{{ item.action }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
            </div>

            <script>
                {{ sentiment_plot }}
                {{ topics_plot }}
            </script>
        </body>
        </html>
        """)

        # Prepare template variables
        template_vars = {
            'total_emails': len(data['all_emails']),
            'date_range': f"{emails_df['date'].min()} to {emails_df['date'].max()}",
            'sentiment_plot': sentiment_fig.to_json(),
            'topics_plot': topics_fig.to_json(),
            'action_items': [
                {
                    'date': email['date'],
                    'subject': email['subject'],
                    'action': action
                }
                for email in data['all_emails']
                if 'action_items' in email
                for action in email['action_items']
            ][:10]  # Show only 10 most recent action items
        }

        # Generate and save HTML report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template.render(**template_vars))

        logger.info(f"HTML report generated and saved to {output_file}")

    def generate_log(self, output_file: str = 'self_email_log.json', max_results: int = None):
        """Generate comprehensive log of self-emails with enhanced analysis."""
        logger.info("Starting enhanced email log generation...")
        
        # Fetch all self-emails
        messages = self.fetch_self_emails(max_results)
        logger.info(f"Found {len(messages)} self-emails")

        # Process emails with enhanced analysis
        processed_emails = self.process_emails(messages)
        
        # Time-based clustering
        time_clusters = self.cluster_by_time(processed_emails)
        
        # Topic evolution analysis
        topic_evolution = self.analyze_topic_evolution(processed_emails)
        
        # Organize by topic
        topic_clusters = defaultdict(list)
        for email in processed_emails:
            if 'analysis' in email and 'key_topics' in email['analysis']:
                for topic in email['analysis']['key_topics']:
                    topic_clusters[topic].append(email)
        
        # Create final output structure
        output = {
            'generated_at': datetime.now().isoformat(),
            'total_emails': len(processed_emails),
            'all_emails': processed_emails,  # Include all processed emails for the HTML report
            'time_clusters': {
                period: {
                    'count': len(emails),
                    'emails': sorted(emails, key=lambda x: x['timestamp'] or 0, reverse=True)
                }
                for period, emails in time_clusters.items()
            },
            'topic_clusters': {
                topic: {
                    'count': len(emails),
                    'emails': sorted(emails, key=lambda x: x['timestamp'] or 0, reverse=True)
                }
                for topic, emails in topic_clusters.items()
            },
            'topic_evolution': topic_evolution,
            'action_items': [
                {
                    'date': email['date'],
                    'subject': email['subject'],
                    'action': action
                }
                for email in processed_emails
                if 'action_items' in email
                for action in email['action_items']
            ]
        }

        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        logger.info(f"Enhanced email log generated and saved to {output_file}")
        
        # Generate HTML report
        self.generate_html_report(output)
        
        return output

def main():
    logger = EmailSelfLogger()
    # Generate log for a sample of 50 emails
    logger.generate_log(max_results=50)

if __name__ == '__main__':
    main()
