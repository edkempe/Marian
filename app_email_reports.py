#!/usr/bin/env python3
import sqlite3
import json
from collections import Counter, defaultdict
import pandas as pd
from tabulate import tabulate
from datetime import datetime
from typing import Dict
import argparse

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

    def get_label_distribution(self) -> Dict[str, int]:
        """Get distribution of email labels."""
        # Get all labels first
        label_cursor = sqlite3.connect(self.label_db_path).cursor()
        label_cursor.execute('SELECT label_id, name FROM gmail_labels')
        label_map = {row[0]: row[1] for row in label_cursor.fetchall()}
        print("Label map:", label_map)  # Debug
        label_cursor.close()
        
        # Count labels in emails
        email_cursor = self.email_conn.cursor()
        email_cursor.execute('SELECT labels FROM emails')
        label_counts = defaultdict(int)
        
        for (labels_str,) in email_cursor.fetchall():
            print("Labels string:", labels_str)  # Debug
            if not labels_str:
                continue
                
            # Split comma-separated label IDs
            label_ids = [label_id.strip() for label_id in labels_str.split(',')]
            print("Label IDs:", label_ids)  # Debug
            
            for label_id in label_ids:
                # Get human-readable label name from map
                label_name = label_map.get(label_id, label_id)
                print(f"Label ID: {label_id}, Label name: {label_name}")  # Debug
                label_counts[label_name] += 1
        
        print("Final label counts:", dict(label_counts))  # Debug
        return dict(sorted(label_counts.items(), key=lambda x: x[1], reverse=True))

    def get_anthropic_analysis(self):
        """Get AI analysis results."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('''
            SELECT 
                a.email_id,
                a.summary,
                a.category,
                a.priority_score,
                a.priority_reason,
                a.action_needed,
                a.action_type,
                a.action_deadline,
                a.key_points,
                a.people_mentioned,
                a.links_found,
                a.project,
                a.topic,
                a.ref_docs,
                a.sentiment,
                a.confidence_score
            FROM email_analysis a
            ORDER BY a.analysis_date DESC
        ''')
        
        results = []
        for row in cursor.fetchall():
            # Get email details from email database
            email_cursor = self.email_conn.cursor()
            email_cursor.execute('SELECT subject, sender FROM emails WHERE id = ?', (row[0],))
            email_row = email_cursor.fetchone()
            
            if email_row:
                analysis = {
                    'email_id': row[0],
                    'subject': email_row[0],
                    'sender': email_row[1],
                    'summary': row[1],
                    'category': json.loads(row[2]) if row[2] else [],
                    'priority': {
                        'score': row[3],
                        'reason': row[4]
                    },
                    'action': {
                        'needed': bool(row[5]),
                        'type': json.loads(row[6]) if row[6] else [],
                        'deadline': row[7] or ''
                    },
                    'key_points': json.loads(row[8]) if row[8] else [],
                    'people_mentioned': json.loads(row[9]) if row[9] else [],
                    'links_found': json.loads(row[10]) if row[10] else [],
                    'project': row[11] or '',
                    'topic': row[12] or '',
                    'ref_docs': row[13] or '',
                    'sentiment': row[14],
                    'confidence_score': row[15]
                }
                results.append(analysis)
        
        return results

    def get_priority_distribution(self):
        """Get distribution of priority scores."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN priority_score >= 3 THEN 'High (3)'
                    WHEN priority_score >= 2 THEN 'Medium (2)'
                    ELSE 'Low (1)'
                END as priority_level,
                COUNT(*) as count
            FROM email_analysis
            GROUP BY priority_level
            ORDER BY priority_score DESC
        ''')
        return {row[0]: row[1] for row in cursor.fetchall()}

    def get_sentiment_distribution(self):
        """Get distribution of sentiment analysis."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('''
            SELECT sentiment, COUNT(*) as count
            FROM email_analysis
            GROUP BY sentiment
        ''')
        return {row[0]: row[1] for row in cursor.fetchall()}

    def get_action_needed_distribution(self):
        """Get distribution of emails needing action."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('''
            SELECT action_needed, COUNT(*) as count
            FROM email_analysis
            GROUP BY action_needed
        ''')
        return {bool(row[0]): row[1] for row in cursor.fetchall()}

    def get_project_distribution(self):
        """Get distribution of projects."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('''
            SELECT project, COUNT(*) as count
            FROM email_analysis
            WHERE project IS NOT NULL AND project != ''
            GROUP BY project
        ''')
        return {row[0]: row[1] for row in cursor.fetchall()}

    def get_topic_distribution(self):
        """Get distribution of topics."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('''
            SELECT topic, COUNT(*) as count
            FROM email_analysis
            WHERE topic IS NOT NULL AND topic != ''
            GROUP BY topic
        ''')
        return {row[0]: row[1] for row in cursor.fetchall()}

    def get_category_distribution(self):
        """Get distribution of categories."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('SELECT category FROM email_analysis')
        category_counts = defaultdict(int)
        
        for (categories_json,) in cursor.fetchall():
            if categories_json:
                categories = json.loads(categories_json)
                for category in categories:
                    category_counts[category] += 1
        
        return dict(category_counts)

    def get_analysis_by_date(self):
        """Get analysis distribution by date."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('''
            SELECT date(analysis_date) as analysis_date,
                   COUNT(*) as count
            FROM email_analysis
            GROUP BY analysis_date
            ORDER BY analysis_date DESC
        ''')
        return [(row[0], row[1]) for row in cursor.fetchall()]

    def get_detailed_analysis(self, email_id):
        """Get detailed analysis for a specific email."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('''
            SELECT *
            FROM email_analysis
            WHERE email_id = ?
        ''', (email_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return {
            'email_id': row['email_id'],
            'summary': row['summary'],
            'category': json.loads(row['category']) if row['category'] else [],
            'priority': {
                'score': row['priority_score'],
                'reason': row['priority_reason']
            },
            'action': {
                'needed': bool(row['action_needed']),
                'type': json.loads(row['action_type']) if row['action_type'] else [],
                'deadline': row['action_deadline'] or ''
            },
            'key_points': json.loads(row['key_points']) if row['key_points'] else [],
            'people_mentioned': json.loads(row['people_mentioned']) if row['people_mentioned'] else [],
            'links_found': json.loads(row['links_found']) if row['links_found'] else [],
            'project': row['project'] or '',
            'topic': row['topic'] or '',
            'ref_docs': row['ref_docs'] or '',
            'sentiment': row['sentiment'],
            'confidence_score': row['confidence_score']
        }

    def get_analysis_with_action_needed(self):
        """Get all analyses that require action."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('SELECT email_id FROM email_analysis WHERE action_needed = 1')
        analyses = []
        for row in cursor.fetchall():
            analysis = self.get_detailed_analysis(row['email_id'])
            if analysis:
                analyses.append(analysis)
        return analyses

    def get_high_priority_analysis(self):
        """Get all high priority analyses (score >= 3)."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('SELECT email_id FROM email_analysis WHERE priority_score >= 3')
        analyses = []
        for row in cursor.fetchall():
            analysis = self.get_detailed_analysis(row['email_id'])
            if analysis:
                analyses.append(analysis)
        return analyses

    def get_analysis_by_sentiment(self, sentiment):
        """Get all analyses with a specific sentiment."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('SELECT email_id FROM email_analysis WHERE sentiment = ?', (sentiment,))
        analyses = []
        for row in cursor.fetchall():
            analysis = self.get_detailed_analysis(row['email_id'])
            if analysis:
                analyses.append(analysis)
        return analyses

    def get_analysis_by_project(self, project):
        """Get all analyses for a specific project."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('SELECT email_id FROM email_analysis WHERE project = ?', (project,))
        analyses = []
        for row in cursor.fetchall():
            analysis = self.get_detailed_analysis(row['email_id'])
            if analysis:
                analyses.append(analysis)
        return analyses

    def get_analysis_by_topic(self, topic):
        """Get all analyses for a specific topic."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('SELECT email_id FROM email_analysis WHERE topic = ?', (topic,))
        analyses = []
        for row in cursor.fetchall():
            analysis = self.get_detailed_analysis(row['email_id'])
            if analysis:
                analyses.append(analysis)
        return analyses

    def get_analysis_by_category(self, category):
        """Get all analyses with a specific category."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('SELECT email_id FROM email_analysis WHERE category LIKE ?', (f'%{category}%',))
        analyses = []
        for row in cursor.fetchall():
            analysis = self.get_detailed_analysis(row['email_id'])
            if analysis:
                analyses.append(analysis)
        return analyses

    def get_analysis_stats(self):
        """Get overall analysis statistics."""
        cursor = self.analysis_conn.cursor()
        stats = {}
        
        # Get total analyzed emails
        cursor.execute('SELECT COUNT(*) as count FROM email_analysis')
        stats['total_analyzed'] = cursor.fetchone()['count']
        
        # Get average confidence score
        cursor.execute('SELECT AVG(confidence_score) as avg_conf FROM email_analysis')
        stats['avg_confidence'] = round(cursor.fetchone()['avg_conf'], 2)
        
        # Get count of emails needing action
        cursor.execute('SELECT COUNT(*) as count FROM email_analysis WHERE action_needed = 1')
        stats['action_needed_count'] = cursor.fetchone()['count']
        
        # Get count of high priority emails
        cursor.execute('SELECT COUNT(*) as count FROM email_analysis WHERE priority_score >= 3')
        stats['high_priority_count'] = cursor.fetchone()['count']
        
        # Get sentiment counts
        cursor.execute('''
            SELECT sentiment, COUNT(*) as count
            FROM email_analysis
            GROUP BY sentiment
        ''')
        stats['sentiment_counts'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        return stats

    def get_confidence_distribution(self):
        """Get distribution of confidence scores."""
        cursor = self.analysis_conn.cursor()
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN confidence_score >= 0.9 THEN '0.9-1.0'
                    WHEN confidence_score >= 0.8 THEN '0.8-0.89'
                    WHEN confidence_score >= 0.7 THEN '0.7-0.79'
                    WHEN confidence_score >= 0.6 THEN '0.6-0.69'
                    ELSE '<0.6'
                END as range,
                COUNT(*) as count
            FROM email_analysis
            GROUP BY range
            ORDER BY range DESC
        ''')
        return cursor.fetchall()

    def print_analysis_report(self):
        """Print a comprehensive analysis report."""
        print("\n=== Email Analysis Report ===\n")
        
        # Get total analyzed emails
        self.analysis_conn.execute("SELECT COUNT(*) as count FROM email_analysis")
        total = self.analysis_conn.fetchone()['count']
        print(f"Total Analyzed Emails: {total}\n")
        
        # Priority Distribution
        print("\nPriority Distribution:")
        priorities = self.get_priority_distribution()
        for score, count in priorities.items():
            print(f"  Priority {score}: {count} emails ({count/total*100:.1f}%)")
        
        # Action Types
        print("\nAction Type Distribution:")
        actions = self.get_action_needed_distribution()
        for action, count in actions.items():
            print(f"  {action}: {count} emails")
        
        # Categories
        print("\nTop Categories:")
        categories = self.get_category_distribution()
        for category, count in categories.items():
            print(f"  {category}: {count} emails")
        
        # Sentiment
        print("\nSentiment Distribution:")
        sentiments = self.get_sentiment_distribution()
        for sentiment, count in sentiments.items():
            print(f"  {sentiment}: {count} emails ({count/total*100:.1f}%)")
        
        # Topic Distribution
        print("\nTop Email Topics (AI Analysis):")
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
        
        # Confidence Distribution
        print("\nConfidence Distribution:")
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
                print(f"Summary: {email['summary']}")
                if email.get('topics'):
                    print(f"Topics: {', '.join(email['topics'])}")
                if email.get('project'):
                    print(f"Project: {email['project']}")
                print(f"Sentiment: {email['sentiment']}")
                if email.get('action_items'):
                    action_items = email['action_items']
                    if action_items:
                        print(f"Action Items: {', '.join(action_items)}")
                print("-" * 80 + "\n")

    def show_basic_stats(self):
        """Show basic email statistics."""
        print("\nBasic Email Statistics:")
        print(f"Total Emails: {self.get_total_emails()}")
        print(f"Top Senders: {self.get_top_senders()}")
        print(f"Email Distribution by Date: {self.get_email_by_date()}")
        print(f"Label Distribution: {self.get_label_distribution()}")

    def show_top_senders(self):
        """Show top email senders."""
        print("\nTop Email Senders:")
        top_senders = self.get_top_senders()
        print(tabulate(top_senders, headers=['Sender', 'Count'], tablefmt='psql'))

    def show_email_distribution(self):
        """Show email distribution by date."""
        print("\nEmail Distribution by Date:")
        date_dist = self.get_email_by_date()
        print(tabulate(date_dist, headers=['Date', 'Count'], tablefmt='psql'))

    def show_label_distribution(self):
        """Show label distribution."""
        print("\nLabel Distribution:")
        label_dist = self.get_label_distribution()
        print(tabulate(label_dist.items(), headers=['Label', 'Count'], tablefmt='psql'))

    def show_ai_analysis_summary(self):
        """Show AI analysis summary."""
        print("\nAI Analysis Summary:")
        analysis_data = self.get_anthropic_analysis()
        if analysis_data:
            for analysis in analysis_data[:5]:
                print(f"\nEmail: {analysis['subject']}")
                print(f"From: {analysis['sender']}")
                print(f"Summary: {analysis['summary']}")
                print(f"Topics: {', '.join(analysis['topic'])}")
                print(f"Sentiment: {analysis['sentiment']}")
                if analysis['action']['needed']:
                    print(f"Action Needed: {analysis['action']['needed']}")
                    print(f"Action Type: {', '.join(analysis['action']['type'])}")
                    print(f"Action Deadline: {analysis['action']['deadline']}")
                print("-" * 80)

    def show_confidence_distribution(self):
        """Show confidence distribution."""
        print("\nConfidence Distribution:")
        confidence_dist = self.get_confidence_distribution()
        print(tabulate(confidence_dist, headers=['Confidence Level', 'Count'], tablefmt='psql'))

    def close_connections(self):
        """Close database connections"""
        self.email_conn.close()
        self.analysis_conn.close()

def sync_gmail_labels():
    """Sync Gmail labels with local database."""
    from lib_gmail import GmailAPI
    
    # Initialize Gmail API and sync labels
    gmail = GmailAPI()
    gmail.sync_labels()

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

def run_report(analytics: EmailAnalytics, report_type: str) -> None:
    """Run a specific report."""
    if report_type == 'basic':
        print(f"\nTotal Emails: {analytics.get_total_emails()}")
    
    elif report_type == 'senders':
        print("\nTop Email Senders:")
        top_senders = analytics.get_top_senders()
        print(tabulate(top_senders, headers=['Sender', 'Count'], tablefmt='psql'))
    
    elif report_type == 'dates':
        print("\nEmail Distribution by Date:")
        date_dist = analytics.get_email_by_date()
        print(tabulate(date_dist, headers=['Date', 'Count'], tablefmt='psql'))
    
    elif report_type == 'labels':
        print("\nTop Email Labels:")
        label_dist = analytics.get_label_distribution()
        print(tabulate(label_dist.items(), headers=['Label', 'Count'], tablefmt='psql'))
    
    elif report_type == 'analysis':
        print("\nAI Analysis Summary:")
        analysis_data = analytics.get_anthropic_analysis()
        if analysis_data:
            for analysis in analysis_data[:5]:
                print(f"\nEmail: {analysis['subject']}")
                print(f"From: {analysis['sender']}")
                print(f"Summary: {analysis['summary']}")
                print(f"Topics: {', '.join(analysis['topic'])}")
                print(f"Sentiment: {analysis['sentiment']}")
                if analysis['action']['needed']:
                    print(f"Action Needed: {analysis['action']['needed']}")
                    print(f"Action Type: {', '.join(analysis['action']['type'])}")
                    print(f"Action Deadline: {analysis['action']['deadline']}")
                print("-" * 80)
    
    elif report_type == 'full':
        analytics.print_analysis_report()
    
    elif report_type == 'confidence':
        print("\nConfidence Distribution:")
        confidence_dist = analytics.get_confidence_distribution()
        print(tabulate(confidence_dist, headers=['Confidence Level', 'Count'], tablefmt='psql'))
    
    elif report_type == 'all':
        # Run all reports in sequence
        for report in ['basic', 'senders', 'dates', 'labels', 'analysis', 'confidence']:
            run_report(analytics, report)
            print("\n" + "="*80 + "\n")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Email Analytics Reports')
    parser.add_argument('--report', choices=['basic', 'senders', 'dates', 'labels', 'analysis', 'full', 'confidence', 'all'],
                      help='Type of report to run. If not specified, starts interactive menu.')
    args = parser.parse_args()
    
    # Sync labels first
    sync_gmail_labels()
    
    analytics = EmailAnalytics("email_store.db", "email_labels.db", "email_analysis.db")
    
    try:
        if args.report:
            # Run specific report
            run_report(analytics, args.report)
        else:
            # Interactive menu
            while True:
                print_menu()
                choice = input("\nEnter your choice (1-8): ")
                
                if choice == '1':
                    run_report(analytics, 'basic')
                elif choice == '2':
                    run_report(analytics, 'senders')
                elif choice == '3':
                    run_report(analytics, 'dates')
                elif choice == '4':
                    run_report(analytics, 'labels')
                elif choice == '5':
                    run_report(analytics, 'analysis')
                elif choice == '6':
                    run_report(analytics, 'full')
                elif choice == '7':
                    run_report(analytics, 'confidence')
                elif choice == '8':
                    print("\nGoodbye!")
                    break
                else:
                    print("\nInvalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        analytics.close_connections()

if __name__ == "__main__":
    main()
