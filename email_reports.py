#!/usr/bin/env python3
import sqlite3
import json
from collections import Counter
import pandas as pd
from tabulate import tabulate
from datetime import datetime
from gmail_label_id import get_label_name

class EmailAnalytics:
    def __init__(self, email_db_path="email_store.db", label_db_path="email_labels.db", analysis_db_path="email_analysis.db"):
        self.email_db_path = email_db_path
        self.label_db_path = label_db_path
        self.analysis_db_path = analysis_db_path
        
        # Connect to email database
        self.email_conn = sqlite3.connect(email_db_path)
        self.email_conn.row_factory = sqlite3.Row
        
        # Connect to analysis database
        self.analysis_conn = sqlite3.connect(analysis_db_path)
        self.analysis_conn.row_factory = sqlite3.Row

    def get_total_emails(self):
        """Get total number of emails in the database"""
        cursor = self.email_conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM emails")
        return cursor.fetchone()['count']

    def get_top_senders(self, limit=10):
        """Get top email senders by volume"""
        cursor = self.email_conn.cursor()
        cursor.execute("""
            SELECT sender, COUNT(*) as count 
            FROM emails 
            GROUP BY sender 
            ORDER BY count DESC 
            LIMIT ?
        """, (limit,))
        return [(row['sender'], row['count']) for row in cursor.fetchall()]

    def get_email_by_date(self):
        """Get email distribution by date"""
        cursor = self.email_conn.cursor()
        cursor.execute("""
            SELECT date(substr(date, 1, 10)) as email_date, 
                   COUNT(*) as count 
            FROM emails 
            GROUP BY email_date 
            ORDER BY email_date DESC 
            LIMIT 10
        """)
        return [(row['email_date'], row['count']) for row in cursor.fetchall()]

    def get_label_distribution(self):
        """Get distribution of email labels"""
        cursor = self.email_conn.cursor()
        cursor.execute("SELECT labels FROM emails WHERE labels IS NOT NULL")
        label_counts = Counter()
        for row in cursor.fetchall():
            if row['labels']:
                labels = row['labels'].split(',')
                for label in labels:
                    label_name = get_label_name(label.strip(), self.label_db_path)
                    label_counts[label_name] += 1
        return dict(label_counts.most_common(10))

    def get_anthropic_analysis(self):
        """Get Anthropic AI analysis summary"""
        analysis_cursor = self.analysis_conn.cursor()
        email_cursor = self.email_conn.cursor()
        
        # Check if analysis table has data
        analysis_cursor.execute("SELECT COUNT(*) as count FROM email_analysis")
        count = analysis_cursor.fetchone()['count']
        
        if count == 0:
            print("\nNo AI analysis available yet. Please run email_analyzer.py first to analyze emails.")
            return None
            
        # Get all analyzed emails
        analysis_cursor.execute("""
            SELECT email_id, analysis_result, analysis_date,
                   sentiment, topics, action_items, summary, project
            FROM email_analysis
            ORDER BY analysis_date DESC
            LIMIT 50
        """)
        analysis_rows = analysis_cursor.fetchall()
        
        analysis_data = []
        for row in analysis_rows:
            # Get email details from email_store.db
            email_cursor.execute("""
                SELECT subject, sender
                FROM emails
                WHERE id = ?
            """, (row['email_id'],))
            email_row = email_cursor.fetchone()
            
            if not email_row:
                print(f"Warning: Email {row['email_id']} not found in email database")
                continue
                
            try:
                # Convert JSON strings back to Python objects
                analysis_result = json.loads(row['analysis_result'])
                sentiment = json.loads(row['sentiment']) if row['sentiment'] else []
                topics = json.loads(row['topics']) if row['topics'] else []
                action_items = json.loads(row['action_items']) if row['action_items'] else []
                
                analysis_data.append({
                    'id': row['email_id'],
                    'subject': email_row['subject'],
                    'sender': email_row['sender'],
                    'analysis_date': row['analysis_date'],
                    'sentiment': sentiment,
                    'topics': topics,
                    'action_items': action_items,
                    'summary': row['summary'],
                    'project': row['project']
                })
            except json.JSONDecodeError as e:
                print(f"Error decoding analysis for email {row['email_id']}: {e}")
                continue
            
        return analysis_data

    def get_topic_distribution(self):
        """Get distribution of topics across analyzed emails"""
        cursor = self.analysis_conn.cursor()
        cursor.execute("SELECT topics FROM email_analysis WHERE topics IS NOT NULL")
        
        topic_counts = Counter()
        for row in cursor.fetchall():
            if row['topics']:
                try:
                    topics = json.loads(row['topics'])
                    if isinstance(topics, list):
                        for topic in topics:
                            if topic and topic != 'N/A':
                                topic_counts[topic] += 1
                except json.JSONDecodeError:
                    continue
        
        return dict(topic_counts.most_common(10))

    def get_project_distribution(self):
        """Get distribution of projects across analyzed emails"""
        cursor = self.analysis_conn.cursor()
        cursor.execute("SELECT project FROM email_analysis WHERE project IS NOT NULL AND project != ''")
        
        project_counts = Counter()
        for row in cursor.fetchall():
            if row['project']:
                project_counts[row['project']] += 1
        
        return dict(project_counts.most_common(10))

    def get_sentiment_distribution(self):
        """Get distribution of sentiments across analyzed emails"""
        cursor = self.analysis_conn.cursor()
        cursor.execute("SELECT sentiment FROM email_analysis WHERE sentiment IS NOT NULL")
        
        sentiment_counts = Counter()
        for row in cursor.fetchall():
            if row['sentiment']:
                try:
                    sentiments = json.loads(row['sentiment'])
                    if isinstance(sentiments, list):
                        for sentiment in sentiments:
                            if sentiment and sentiment != 'N/A':
                                sentiment_counts[sentiment] += 1
                    elif isinstance(sentiments, str) and sentiments != 'N/A':
                        sentiment_counts[sentiments] += 1
                except json.JSONDecodeError:
                    continue
        
        return dict(sentiment_counts.most_common(10))

    def get_confidence_distribution(self):
        """Get distribution of confidence scores from email analysis."""
        query = """
            SELECT 
                CASE 
                    WHEN confidence >= 0.9 THEN 'Very High (≥0.9)'
                    WHEN confidence >= 0.7 THEN 'High (0.7-0.89)'
                    WHEN confidence >= 0.5 THEN 'Medium (0.5-0.69)'
                    WHEN confidence >= 0.3 THEN 'Low (0.3-0.49)'
                    ELSE 'Very Low (<0.3)'
                END as confidence_level,
                COUNT(*) as count
            FROM email_analysis
            GROUP BY confidence_level
            ORDER BY 
                CASE confidence_level
                    WHEN 'Very High (≥0.9)' THEN 1
                    WHEN 'High (0.7-0.89)' THEN 2
                    WHEN 'Medium (0.5-0.69)' THEN 3
                    WHEN 'Low (0.3-0.49)' THEN 4
                    WHEN 'Very Low (<0.3)' THEN 5
                END;
        """
        cursor = self.analysis_conn.cursor()
        cursor.execute(query)
        return [(row['confidence_level'], row['count']) for row in cursor.fetchall()]

    def print_analysis_report(self):
        """Print a comprehensive analysis report"""
        print("\n=== Email Analytics Report ===\n")
        
        # Basic Stats
        total_emails = self.get_total_emails()
        print(f"Total Emails: {total_emails}\n")
        
        # Top Senders
        print("Top Email Senders:")
        senders = self.get_top_senders()
        print(tabulate(
            [[sender, count] for sender, count in senders],
            headers=['Sender', 'Count'],
            tablefmt='pipe'
        ))
        print()
        
        # Date Distribution
        print("Email Distribution by Date:")
        dates = self.get_email_by_date()
        print(tabulate(
            [[date, count] for date, count in dates],
            headers=['Date', 'Count'],
            tablefmt='pipe'
        ))
        print()
        
        # Label Distribution
        print("Top Email Labels:")
        labels = self.get_label_distribution()
        print(tabulate(
            [[label, count] for label, count in labels.items()],
            headers=['Label', 'Count'],
            tablefmt='pipe'
        ))
        print()
        
        # Topic Distribution
        print("Top Email Topics (AI Analysis):")
        topics = self.get_topic_distribution()
        if topics:
            print(tabulate(
                [[topic, count] for topic, count in topics.items()],
                headers=['Topic', 'Count'],
                tablefmt='pipe'
            ))
        print()
        
        # Project Distribution
        print("Project Distribution (AI Analysis):")
        projects = self.get_project_distribution()
        if projects:
            print(tabulate(
                [[project, count] for project, count in projects.items()],
                headers=['Project', 'Count'],
                tablefmt='pipe'
            ))
        print()
        
        # Sentiment Distribution
        print("Email Sentiment Distribution (AI Analysis):")
        sentiments = self.get_sentiment_distribution()
        if sentiments:
            print(tabulate(
                [[sentiment, count] for sentiment, count in sentiments.items()],
                headers=['Sentiment', 'Count'],
                tablefmt='pipe'
            ))
        print()
        
        # Confidence Distribution
        print("Confidence Distribution:")
        confidence_dist = self.get_confidence_distribution()
        print(tabulate(confidence_dist, headers=['Confidence Level', 'Count'], tablefmt='psql'))
        print()
        
        # Recent Analysis
        print("Recent Email Analysis:\n")
        analysis = self.get_anthropic_analysis()
        if analysis:
            for email in analysis:
                print(f"Email: {email['subject']}")
                print(f"From: {email['sender']}")
                print(f"Analysis Date: {email['analysis_date']}")
                if email.get('topics'):
                    print(f"Topics: {', '.join(email['topics'])}")
                if email.get('project'):
                    print(f"Project: {email['project']}")
                print(f"Summary: {email['summary']}")
                if email.get('action_items'):
                    action_items = email['action_items']
                    if action_items:
                        print(f"Action Items: {', '.join(action_items)}")
                print("-" * 80 + "\n")

    def close(self):
        """Close database connections"""
        self.email_conn.close()
        self.analysis_conn.close()

def print_menu():
    print("\n=== Email Analytics Menu ===")
    print("1. Show Basic Stats")
    print("2. Show Top Senders")
    print("3. Show Email Distribution by Date")
    print("4. Show Label Distribution")
    print("5. Show AI Analysis Summary")
    print("6. Show Full Report")
    print("7. Show Confidence Distribution")
    print("8. Exit")

if __name__ == "__main__":
    analytics = EmailAnalytics("email_store.db", "email_labels.db", "email_analysis.db")
    
    try:
        while True:
            print_menu()
            choice = input("\nEnter your choice (1-8): ")
            
            if choice == '1':
                print(f"\nTotal Emails: {analytics.get_total_emails()}")
            
            elif choice == '2':
                print("\nTop Email Senders:")
                top_senders = analytics.get_top_senders()
                print(tabulate(top_senders, headers=['Sender', 'Count'], tablefmt='psql'))
            
            elif choice == '3':
                print("\nEmail Distribution by Date:")
                date_dist = analytics.get_email_by_date()
                print(tabulate(date_dist, headers=['Date', 'Count'], tablefmt='psql'))
            
            elif choice == '4':
                print("\nTop Email Labels:")
                label_dist = analytics.get_label_distribution()
                print(tabulate(label_dist.items(), headers=['Label', 'Count'], tablefmt='psql'))
            
            elif choice == '5':
                print("\nAI Analysis Summary:")
                analysis_data = analytics.get_anthropic_analysis()
                if analysis_data:
                    for analysis in analysis_data[:5]:
                        print(f"\nEmail: {analysis['subject']}")
                        print(f"From: {analysis['sender']}")
                        print(f"Analysis Date: {analysis['analysis_date']}")
                        print(f"Topics: {', '.join(analysis['topics'])}")
                        print(f"Summary: {analysis['summary']}")
                        if analysis['action_items']:
                            print(f"Action Items: {', '.join(analysis['action_items'])}")
                        print("-" * 80)
            
            elif choice == '6':
                analytics.print_analysis_report()
            
            elif choice == '7':
                print("\nConfidence Distribution:")
                confidence_dist = analytics.get_confidence_distribution()
                print(tabulate(confidence_dist, headers=['Confidence Level', 'Count'], tablefmt='psql'))
            
            elif choice == '8':
                print("\nGoodbye!")
                break
            
            else:
                print("\nInvalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        analytics.close()
