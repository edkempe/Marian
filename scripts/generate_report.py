#!/usr/bin/env python3
from datetime import datetime
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from jinja2 import Environment, BaseLoader
import sys
from constants import DATABASE_CONFIG
from models.email import Email
from models.email_analysis import EmailAnalysis

def generate_html_report():
    # Create SQLAlchemy engine and session
    analysis_db_path = 'data/db_email_analysis.db'
    email_db_path = 'data/db_email_store.db'
    
    if not os.path.exists(analysis_db_path) or not os.path.exists(email_db_path):
        print(f"Database files not found!")
        return
        
    # Create SQLAlchemy engine
    engine = create_engine(f'sqlite:///{analysis_db_path}?check_same_thread=False')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Query the data using SQLAlchemy
        query = text("""
        SELECT 
            e.subject,
            e.from_ as from_address,
            a.priority_score,
            a.priority_reason,
            a.analysis_date,
            a.sentiment
        FROM emails e
        JOIN email_analysis a ON e.id = a.email_id
        ORDER BY a.analysis_date DESC, a.priority_score DESC
        """)
        
        # Execute query
        result = session.execute(query)
        rows = result.fetchall()
        
        if not rows:
            print("No analyzed emails found in the database!")
            return
        
        print(f"Found {len(rows)} analyzed emails")
        
        # Convert rows to dictionaries for template rendering
        emails = []
        for row in rows:
            email_dict = dict(row)
            # Format dates
            if email_dict['analysis_date']:
                email_dict['analysis_date'] = email_dict['analysis_date'].strftime('%Y-%m-%d %H:%M:%S')
            emails.append(email_dict)
        
        # Generate HTML report using template
        template = Environment(loader=BaseLoader()).from_string("""
        <html>
        <head>
            <title>Email Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .high { color: red; }
                .medium { color: orange; }
                .low { color: green; }
            </style>
        </head>
        <body>
            <h1>Email Analysis Report</h1>
            <p>Generated on: {{ generation_date }}</p>
            <table>
                <tr>
                    <th>Subject</th>
                    <th>From</th>
                    <th>Priority</th>
                    <th>Reason</th>
                    <th>Sentiment</th>
                    <th>Analysis Date</th>
                </tr>
                {% for email in emails %}
                <tr>
                    <td>{{ email.subject }}</td>
                    <td>{{ email.from_address }}</td>
                    <td class="{{ 'high' if email.priority_score > 0.7 else 'medium' if email.priority_score > 0.4 else 'low' }}">
                        {{ "%.2f"|format(email.priority_score) }}
                    </td>
                    <td>{{ email.priority_reason }}</td>
                    <td>{{ email.sentiment }}</td>
                    <td>{{ email.analysis_date }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """)
        
        html = template.render(
            emails=emails,
            generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Write HTML report to file
        with open('reports/email_analysis_report.html', 'w') as f:
            f.write(html)
            
        print("Report generated successfully!")
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        
    finally:
        session.close()

def generate_sent_emails_report(output_file='reports/sent_emails_report.html'):
    """Generate a report of sent emails."""
    # Create SQLAlchemy engine and session
    email_db_path = 'data/db_email_store.db'
    
    if not os.path.exists(email_db_path):
        print(f"Email database not found!")
        return
        
    # Create SQLAlchemy engine
    engine = create_engine(f'sqlite:///{email_db_path}?check_same_thread=False')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Query sent emails using SQLAlchemy
        sent_emails = session.query(Email).filter(
            Email.from_.like('%@gmail.com')
        ).order_by(Email.received_date.desc()).all()
        
        if not sent_emails:
            print("No sent emails found!")
            return
            
        print(f"Found {len(sent_emails)} sent emails")
        
        # Convert to list of dictionaries for template
        emails = []
        for email in sent_emails:
            emails.append({
                'subject': email.subject,
                'to': email.to,
                'date': email.received_date.strftime('%Y-%m-%d %H:%M:%S') if email.received_date else '',
                'body': email.body[:200] + '...' if len(email.body or '') > 200 else email.body
            })
        
        # Generate HTML report
        template = Environment(loader=BaseLoader()).from_string("""
        <html>
        <head>
            <title>Sent Emails Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <h1>Sent Emails Report</h1>
            <p>Generated on: {{ generation_date }}</p>
            <table>
                <tr>
                    <th>Subject</th>
                    <th>To</th>
                    <th>Date</th>
                    <th>Content Preview</th>
                </tr>
                {% for email in emails %}
                <tr>
                    <td>{{ email.subject }}</td>
                    <td>{{ email.to }}</td>
                    <td>{{ email.date }}</td>
                    <td>{{ email.body }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """)
        
        html = template.render(
            emails=emails,
            generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Write report to file
        with open(output_file, 'w') as f:
            f.write(html)
            
        print(f"Report generated successfully at {output_file}")
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        
    finally:
        session.close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--sent':
        generate_sent_emails_report()
    else:
        generate_html_report()
