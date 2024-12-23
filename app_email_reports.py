#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timezone
from typing import Dict, List
from database.config import get_email_session, get_analysis_session
from models.email_analysis import EmailAnalysis
from models.email import Email
import argparse

class EmailAnalytics:
    """Analytics for email and analysis data."""
    
    def __init__(self):
        """Initialize analytics."""
        pass  # Sessions will be created as needed using context managers

    def get_total_emails(self):
        """Get total number of emails in the database"""
        with get_email_session() as session:
            return session.query(Email).count()

    def get_top_senders(self, limit=10):
        """Get top email senders by volume"""
        with get_email_session() as session:
            return session.query(Email.sender, Email.id).group_by(Email.sender).order_by(Email.id.desc()).limit(limit).all()

    def get_email_by_date(self):
        """Get email distribution by date"""
        with get_email_session() as session:
            return session.query(Email.date, Email.id).group_by(Email.date).order_by(Email.date.desc()).limit(10).all()

    def get_label_distribution(self) -> Dict[str, int]:
        """Get distribution of email labels."""
        # Get all labels first
        with get_email_session() as session:
            labels = session.query(Email.labels).all()
        
        # Count labels in emails
        label_counts = defaultdict(int)
        
        for labels_str in labels:
            if not labels_str[0]:
                continue
                
            # Split comma-separated label IDs
            label_ids = [label_id.strip() for label_id in labels_str[0].split(',')]
            
            for label_id in label_ids:
                # Get human-readable label name from map
                label_name = label_id
                label_counts[label_name] += 1
        
        return dict(sorted(label_counts.items(), key=lambda x: x[1], reverse=True))

    def get_anthropic_analysis(self):
        """Get all Anthropic analysis results."""
        analyses = []
        
        with get_analysis_session() as analysis_session:
            with get_email_session() as email_session:
                results = analysis_session.query(EmailAnalysis).order_by(EmailAnalysis.analysis_date.desc()).all()
                
                for result in results:
                    # Get email details from email database
                    email = email_session.query(Email).filter(Email.id == result.email_id).first()
                    
                    if email:
                        analysis = {
                            'email_id': result.email_id,
                            'thread_id': result.thread_id,
                            'analysis_date': result.analysis_date,
                            'subject': email.subject,
                            'sender': email.sender,
                            'summary': result.summary,
                            'category': result.category if isinstance(result.category, list) else json.loads(result.category) if result.category else [],
                            'priority': {
                                'score': result.priority_score,
                                'reason': result.priority_reason
                            },
                            'action': {
                                'needed': bool(result.action_needed),
                                'type': result.action_type if isinstance(result.action_type, list) else json.loads(result.action_type) if result.action_type else [],
                                'deadline': result.action_deadline.isoformat() if result.action_deadline else ''
                            },
                            'key_points': result.key_points if isinstance(result.key_points, list) else json.loads(result.key_points) if result.key_points else [],
                            'people_mentioned': result.people_mentioned if isinstance(result.people_mentioned, list) else json.loads(result.people_mentioned) if result.people_mentioned else [],
                            'links': {
                                'found': result.links_found if isinstance(result.links_found, list) else json.loads(result.links_found) if result.links_found else [],
                                'display': result.links_display if isinstance(result.links_display, list) else json.loads(result.links_display) if result.links_display else []
                            },
                            'project': result.project or '',
                            'topic': result.topic or '',
                            'sentiment': result.sentiment,
                            'confidence_score': result.confidence_score,
                            'raw_analysis': result.raw_analysis
                        }
                        analyses.append(analysis)
        
        return analyses

    def get_priority_distribution(self):
        """Get distribution of priority scores."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis.priority_score).all()
        
        priorities = {}
        for score in results:
            if score[0] >= 3:
                priorities['High (3)'] = priorities.get('High (3)', 0) + 1
            elif score[0] >= 2:
                priorities['Medium (2)'] = priorities.get('Medium (2)', 0) + 1
            else:
                priorities['Low (1)'] = priorities.get('Low (1)', 0) + 1
        
        return priorities

    def get_sentiment_distribution(self):
        """Get distribution of sentiment analysis."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis.sentiment).all()
        
        sentiments = {}
        for sentiment in results:
            sentiments[sentiment[0]] = sentiments.get(sentiment[0], 0) + 1
        
        return sentiments

    def get_action_needed_distribution(self):
        """Get distribution of emails needing action."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis.action_needed).all()
        
        actions = {}
        for action in results:
            actions[bool(action[0])] = actions.get(bool(action[0]), 0) + 1
        
        return actions

    def get_project_distribution(self):
        """Get distribution of projects."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis.project).filter(EmailAnalysis.project != None, EmailAnalysis.project != '').all()
        
        projects = {}
        for project in results:
            projects[project[0]] = projects.get(project[0], 0) + 1
        
        return projects

    def get_topic_distribution(self):
        """Get distribution of topics."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis.topic).filter(EmailAnalysis.topic != None, EmailAnalysis.topic != '').all()
        
        topics = {}
        for topic in results:
            topics[topic[0]] = topics.get(topic[0], 0) + 1
        
        return topics

    def get_category_distribution(self):
        """Get distribution of categories."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis.category).all()
        
        categories = defaultdict(int)
        for categories_json in results:
            if categories_json[0]:
                categories_list = json.loads(categories_json[0])
                for category in categories_list:
                    categories[category] += 1
        
        return dict(categories)

    def get_analysis_by_date(self):
        """Get analysis distribution by date."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis.analysis_date).all()
        
        dates = {}
        for date in results:
            dates[date[0]] = dates.get(date[0], 0) + 1
        
        return list(dates.items())

    def get_detailed_analysis(self, email_id):
        """Get detailed analysis for a specific email."""
        with get_analysis_session() as analysis_session:
            with get_email_session() as email_session:
                result = analysis_session.query(EmailAnalysis).filter(EmailAnalysis.email_id == email_id).first()
                if not result:
                    return None
                
                email = email_session.query(Email).filter(Email.id == email_id).first()
                if not email:
                    return None
                
                analysis = {
                    'email_id': result.email_id,
                    'thread_id': result.thread_id,
                    'analysis_date': result.analysis_date,
                    'subject': email.subject,
                    'sender': email.sender,
                    'summary': result.summary,
                    'category': result.category if isinstance(result.category, list) else json.loads(result.category) if result.category else [],
                    'priority': {
                        'score': result.priority_score,
                        'reason': result.priority_reason
                    },
                    'action': {
                        'needed': bool(result.action_needed),
                        'type': result.action_type if isinstance(result.action_type, list) else json.loads(result.action_type) if result.action_type else [],
                        'deadline': result.action_deadline.isoformat() if result.action_deadline else ''
                    },
                    'key_points': result.key_points if isinstance(result.key_points, list) else json.loads(result.key_points) if result.key_points else [],
                    'people_mentioned': result.people_mentioned if isinstance(result.people_mentioned, list) else json.loads(result.people_mentioned) if result.people_mentioned else [],
                    'links': {
                        'found': result.links_found if isinstance(result.links_found, list) else json.loads(result.links_found) if result.links_found else [],
                        'display': result.links_display if isinstance(result.links_display, list) else json.loads(result.links_display) if result.links_display else []
                    },
                    'project': result.project or '',
                    'topic': result.topic or '',
                    'sentiment': result.sentiment,
                    'confidence_score': result.confidence_score,
                    'raw_analysis': result.raw_analysis
                }
                
                return analysis

    def get_analysis_by_category(self, category):
        """Get all analyses with a specific category."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis).all()
            matching_ids = []
            for result in results:
                categories = result.category if isinstance(result.category, list) else json.loads(result.category) if result.category else []
                if category in categories:
                    matching_ids.append(result.email_id)
        
        analyses = []
        for email_id in matching_ids:
            analysis = self.get_detailed_analysis(email_id)
            if analysis:
                analyses.append(analysis)
        
        return analyses

    def get_analysis_stats(self):
        """Get overall analysis statistics."""
        with get_analysis_session() as session:
            stats = {}
            
            # Basic counts
            stats['total_analyzed'] = session.query(EmailAnalysis).count()
            stats['action_needed_count'] = session.query(EmailAnalysis).filter(EmailAnalysis.action_needed == True).count()
            stats['high_priority_count'] = session.query(EmailAnalysis).filter(EmailAnalysis.priority_score >= 3).count()
            
            # Confidence scores
            confidence_scores = [score[0] for score in session.query(EmailAnalysis.confidence_score).all() if score[0] is not None]
            if confidence_scores:
                stats['avg_confidence'] = sum(confidence_scores) / len(confidence_scores)
                stats['min_confidence'] = min(confidence_scores)
                stats['max_confidence'] = max(confidence_scores)
            else:
                stats['avg_confidence'] = 0
                stats['min_confidence'] = 0
                stats['max_confidence'] = 0
            
            # Sentiment distribution
            sentiment_counts = Counter(s[0] for s in session.query(EmailAnalysis.sentiment).all() if s[0])
            stats['sentiment_counts'] = dict(sentiment_counts)
            
            # Project and topic counts
            stats['unique_projects'] = len(set(p[0] for p in session.query(EmailAnalysis.project).all() if p[0]))
            stats['unique_topics'] = len(set(t[0] for t in session.query(EmailAnalysis.topic).all() if t[0]))
            
            # Analysis dates
            dates = [d[0] for d in session.query(EmailAnalysis.analysis_date).order_by(EmailAnalysis.analysis_date).all()]
            if dates:
                stats['first_analysis'] = dates[0]
                stats['last_analysis'] = dates[-1]
                stats['analysis_timespan'] = (dates[-1] - dates[0]).days
            
            return stats

    def get_confidence_distribution(self):
        """Get distribution of confidence scores."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis.confidence_score).all()
        
        confidence_dist = {}
        for score in results:
            if score[0] >= 0.9:
                confidence_dist['0.9-1.0'] = confidence_dist.get('0.9-1.0', 0) + 1
            elif score[0] >= 0.8:
                confidence_dist['0.8-0.89'] = confidence_dist.get('0.8-0.89', 0) + 1
            elif score[0] >= 0.7:
                confidence_dist['0.7-0.79'] = confidence_dist.get('0.7-0.79', 0) + 1
            elif score[0] >= 0.6:
                confidence_dist['0.6-0.69'] = confidence_dist.get('0.6-0.69', 0) + 1
            else:
                confidence_dist['<0.6'] = confidence_dist.get('<0.6', 0) + 1
        
        return list(confidence_dist.items())

    def get_analysis_with_action_needed(self) -> List[Dict]:
        """Get analyses that require action."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis).filter(EmailAnalysis.action_needed == True).all()
            return [self._format_analysis(analysis) for analysis in results]

    def get_high_priority_analysis(self) -> List[Dict]:
        """Get high priority analyses (priority_score >= 4)."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis).filter(EmailAnalysis.priority_score >= 4).all()
            return [self._format_analysis(analysis) for analysis in results]

    def get_analysis_by_sentiment(self, sentiment: str) -> List[Dict]:
        """Get analyses by sentiment (positive/negative/neutral)."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis).filter(EmailAnalysis.sentiment == sentiment).all()
            return [self._format_analysis(analysis) for analysis in results]

    def get_analysis_by_project(self, project: str) -> List[Dict]:
        """Get analyses by project."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis).filter(EmailAnalysis.project == project).all()
            return [self._format_analysis(analysis) for analysis in results]

    def get_analysis_by_topic(self, topic: str) -> List[Dict]:
        """Get analyses by topic."""
        with get_analysis_session() as session:
            results = session.query(EmailAnalysis).filter(EmailAnalysis.topic == topic).all()
            return [self._format_analysis(analysis) for analysis in results]

    def _format_analysis(self, analysis: EmailAnalysis) -> Dict:
        """Format an EmailAnalysis object into a dictionary.
        
        Args:
            analysis: EmailAnalysis object to format
        
        Returns:
            Dictionary containing formatted analysis data
        """
        return {
            'id': analysis.email_id,
            'thread_id': analysis.thread_id,
            'date': analysis.analysis_date.isoformat(),
            'summary': analysis.summary,
            'category': analysis.category,
            'priority_score': analysis.priority_score,
            'priority_reason': analysis.priority_reason,
            'action_needed': analysis.action_needed,
            'action_type': analysis.action_type,
            'action_deadline': analysis.action_deadline.isoformat() if analysis.action_deadline else None,
            'key_points': analysis.key_points,
            'people_mentioned': analysis.people_mentioned,
            'links_found': analysis.links_found,
            'links_display': analysis.links_display,
            'project': analysis.project,
            'topic': analysis.topic,
            'sentiment': analysis.sentiment,
            'confidence_score': analysis.confidence_score,
        }

    def print_analysis_report(self):
        """Print a comprehensive analysis report."""
        print("\n=== Email Analysis Report ===\n")
        
        # Get total analyzed emails
        total = self.get_total_emails()
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
    
    analytics = EmailAnalytics()
    
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
        pass

if __name__ == "__main__":
    main()
