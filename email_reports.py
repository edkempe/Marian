#!/usr/bin/env python3
import sqlite3
import json
from collections import Counter
import pandas as pd
from tabulate import tabulate
from datetime import datetime
from gmail_label_id import get_label_name

class EmailAnalytics:
    def __init__(self, db_path="test_email_store.db", label_db_path="email_labels.db"):
        self.db_path = db_path
        self.label_db_path = label_db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create email_triage table if it doesn't exist
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_triage (
                email_id TEXT PRIMARY KEY,
                analysis_json TEXT,
                processed_at TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails (id)
            )
        ''')
        self.conn.commit()

    def get_total_emails(self):
        """Get total number of emails in the database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM emails")
        return cursor.fetchone()['count']

    def get_top_senders(self, limit=10):
        """Get top email senders by volume"""
        cursor = self.conn.cursor()
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
        cursor = self.conn.cursor()
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
        cursor = self.conn.cursor()
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
        cursor = self.conn.cursor()
        
        # Check if email_triage table exists and has data
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM email_triage 
            WHERE analysis_json IS NOT NULL
        """)
        count = cursor.fetchone()['count']
        
        if count == 0:
            print("\nNo AI analysis available yet. Please run test_anthropic_email.py first to analyze emails.")
            return None
            
        cursor.execute("""
            SELECT e.id, e.subject, e.sender, t.analysis_json, t.processed_at
            FROM emails e
            JOIN email_triage t ON e.id = t.email_id
            WHERE t.analysis_json IS NOT NULL
            ORDER BY t.processed_at DESC
            LIMIT 50
        """)
        
        analysis_data = []
        for row in cursor.fetchall():
            try:
                analysis = json.loads(row['analysis_json'])
                analysis_data.append({
                    'id': row['id'],
                    'subject': row['subject'],
                    'sender': row['sender'],
                    'priority_score': analysis.get('priority', {}).get('score', 'N/A'),
                    'priority_reason': analysis.get('priority', {}).get('reason', 'N/A'),
                    'category': analysis.get('category', ['N/A'])[0],
                    'secondary_category': analysis.get('category', ['N/A', 'N/A'])[1] if len(analysis.get('category', [])) > 1 else 'N/A',
                    'action_needed': analysis.get('action', {}).get('needed', 'N/A'),
                    'action_type': ', '.join(analysis.get('action', {}).get('type', [])) or 'N/A',
                    'action_deadline': analysis.get('action', {}).get('deadline', 'N/A'),
                    'sentiment': analysis.get('sentiment', 'N/A'),
                    'confidence_score': analysis.get('confidence_score', 'N/A'),
                    'project': analysis.get('context', {}).get('project', 'N/A'),
                    'topic': analysis.get('context', {}).get('topic', 'N/A'),
                    'summary': analysis.get('summary', 'N/A')
                })
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing analysis for email {row['id']}: {e}")
                continue
                
        return analysis_data

    def print_basic_report(self):
        """Print basic email analytics report"""
        output = []
        output.append("\n=== Basic Email Analytics Report ===\n")
        
        # Total emails
        total_emails = self.get_total_emails()
        output.append(f"Total Emails: {total_emails}\n")
        
        # Top senders
        output.append("\nTop Email Senders:")
        top_senders = self.get_top_senders()
        sender_df = pd.DataFrame(top_senders, columns=['Sender', 'Count'])
        sender_df['Percentage'] = (sender_df['Count'] / total_emails) * 100
        output.append(tabulate(sender_df, headers='keys', tablefmt='pretty', floatfmt=".1f"))
        
        # Emails by date
        output.append("\nEmail Volume by Date:")
        date_dist = self.get_email_by_date()
        date_df = pd.DataFrame(date_dist, columns=['Date', 'Count'])
        date_df['Percentage'] = (date_df['Count'] / total_emails) * 100
        output.append(tabulate(date_df, headers='keys', tablefmt='pretty', floatfmt=".1f"))
        
        # Label distribution
        output.append("\nEmail Label Distribution:")
        label_dist = self.get_label_distribution()
        if label_dist:
            label_df = pd.DataFrame(label_dist.items(), columns=['Label', 'Count'])
            label_df['Percentage'] = (label_df['Count'] / total_emails) * 100
            output.append(tabulate(label_df, headers='keys', tablefmt='pretty', floatfmt=".1f"))
        else:
            output.append("No label data available.")
        
        print('\n'.join(str(item) for item in output))

    def print_ai_analysis_report(self):
        """Print AI analysis report"""
        output = []
        output.append("\n=== AI Email Analysis Report ===\n")
        
        analysis_data = self.get_anthropic_analysis()
        if not analysis_data:
            output.append("No AI analysis data available.")
            print('\n'.join(output))
            return

        # Priority distribution with reasons
        priority_df = pd.DataFrame([{
            'Priority': email['priority_score'],
            'Reason': email['priority_reason'],
            'Count': 1
        } for email in analysis_data])
        priority_summary = priority_df.groupby('Priority').agg({
            'Count': 'sum',
            'Reason': lambda x: ', '.join(set(x)[:3])  # Show up to 3 unique reasons
        }).reset_index()
        priority_summary['Percentage'] = (priority_summary['Count'] / len(analysis_data)) * 100
        output.append("Email Priority Distribution:")
        output.append(tabulate(priority_summary, headers='keys', tablefmt='pretty', floatfmt=".1f"))
        output.append("")

        # Category distribution (primary and secondary)
        category_df = pd.DataFrame([{
            'Primary Category': email['category'],
            'Secondary Category': email['secondary_category']
        } for email in analysis_data])
        primary_cats = category_df['Primary Category'].value_counts().reset_index()
        primary_cats.columns = ['Category', 'Count']
        primary_cats['Percentage'] = (primary_cats['Count'] / len(analysis_data)) * 100
        output.append("Primary Category Distribution:")
        output.append(tabulate(primary_cats, headers='keys', tablefmt='pretty', floatfmt=".1f"))
        output.append("")

        # Action analysis
        action_df = pd.DataFrame([{
            'Action Needed': email['action_needed'],
            'Action Type': email['action_type'],
            'Deadline': email['action_deadline']
        } for email in analysis_data])
        action_summary = action_df[action_df['Action Needed'] == True].groupby('Action Type').size().reset_index()
        action_summary.columns = ['Action Type', 'Count']
        action_summary['Percentage'] = (action_summary['Count'] / len(analysis_data)) * 100
        output.append("Required Actions Distribution:")
        output.append(tabulate(action_summary, headers='keys', tablefmt='pretty', floatfmt=".1f"))
        output.append("")

        # Project/Topic Analysis
        context_df = pd.DataFrame([{
            'Project': email['project'],
            'Topic': email['topic']
        } for email in analysis_data])
        project_summary = context_df['Project'].value_counts().reset_index()
        project_summary.columns = ['Project', 'Count']
        project_summary = project_summary[project_summary['Project'] != 'N/A']
        if not project_summary.empty:
            project_summary['Percentage'] = (project_summary['Count'] / len(analysis_data)) * 100
            output.append("Project Distribution:")
            output.append(tabulate(project_summary, headers='keys', tablefmt='pretty', floatfmt=".1f"))
            output.append("")

        # Confidence Score Analysis
        confidence_scores = [email['confidence_score'] for email in analysis_data if email['confidence_score'] != 'N/A']
        if confidence_scores:
            confidence_stats = {
                'Average Confidence': sum(confidence_scores) / len(confidence_scores),
                'Min Confidence': min(confidence_scores),
                'Max Confidence': max(confidence_scores)
            }
            confidence_df = pd.DataFrame([confidence_stats])
            output.append("AI Confidence Analysis:")
            output.append(tabulate(confidence_df, headers='keys', tablefmt='pretty', floatfmt=".3f"))
            output.append("")

        # Sentiment distribution
        sentiment_counts = Counter(email['sentiment'] for email in analysis_data)
        sentiment_df = pd.DataFrame([
            {'Sentiment': s, 'Count': c, 'Percentage': (c/len(analysis_data))*100}
            for s, c in sentiment_counts.items()
        ])
        output.append("Email Sentiment Distribution:")
        output.append(tabulate(sentiment_df, headers='keys', tablefmt='pretty', floatfmt=".1f"))
        
        print('\n'.join(str(item) for item in output))

    def __del__(self):
        self.conn.close()

def print_menu():
    """Print the main menu"""
    print("\n=== Email Analytics Menu ===")
    print("1. Basic Email Report (Senders, Dates, Labels)")
    print("2. AI Analysis Report (Priority, Categories, Sentiment)")
    print("3. Both Reports")
    print("4. Exit")

if __name__ == "__main__":
    analytics = EmailAnalytics("test_email_store.db", "email_labels.db")
    
    try:
        while True:
            print_menu()
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                analytics.print_basic_report()
            elif choice == '2':
                analytics.print_ai_analysis_report()
            elif choice == '3':
                analytics.print_basic_report()
                print("\nPress Enter to continue to AI Analysis...")
                input()
                analytics.print_ai_analysis_report()
            elif choice == '4':
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid option. Please try again.")
            
            if choice in ['1', '2', '3']:
                print("\nPress Enter to return to menu...")
                input()
    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        raise
