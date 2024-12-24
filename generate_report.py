#!/usr/bin/env python3
import sqlite3
from datetime import datetime
import os
from sqlalchemy import create_engine
import pandas as pd
from jinja2 import Environment, BaseLoader
import sys
from constants import DATABASE_CONFIG

def generate_html_report():
    # Connect to the databases
    analysis_db_path = 'db_email_analysis.db'
    email_db_path = 'db_email_store.db'
    
    if not os.path.exists(analysis_db_path) or not os.path.exists(email_db_path):
        print(f"Database files not found!")
        return
        
    # Create connection to analysis database
    analysis_conn = sqlite3.connect(analysis_db_path)
    analysis_conn.row_factory = sqlite3.Row
    
    try:
        # Query the data from both databases
        query = """
        SELECT 
            e.subject,
            e.from_address,
            a.priority_score,
            a.priority_reason,
            a.analysis_date,
            a.sentiment
        FROM db_email_store.emails e
        JOIN db_email_analysis.email_analysis a ON e.id = a.email_id
        ORDER BY a.analysis_date DESC, a.priority_score DESC
        """
        
        # Execute query against analysis database
        cursor = analysis_conn.cursor()
        cursor.execute("ATTACH DATABASE 'db_email_store.db' AS db_email_store")
        cursor.execute("ATTACH DATABASE 'db_email_analysis.db' AS db_email_analysis")
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("No analyzed emails found in the database!")
            return
        
        print(f"Found {len(rows)} analyzed emails")
        
        # Generate HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ 
                    border-collapse: collapse; 
                    width: 100%;
                    margin-top: 20px;
                }}
                th, td {{ 
                    padding: 12px; 
                    text-align: left; 
                    border-bottom: 1px solid #ddd; 
                }}
                th {{ 
                    background-color: #f5f5f5;
                    color: #333;
                }}
                tr:hover {{ background-color: #f9f9f9; }}
                .priority-high {{ color: #d32f2f; }}
                .priority-medium {{ color: #f57c00; }}
                .priority-low {{ color: #388e3c; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <h1>Email Analysis Report</h1>
            <p class="timestamp">Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <table>
                <tr>
                    <th>Subject</th>
                    <th>Sender</th>
                    <th>Priority</th>
                    <th>Reason</th>
                    <th>Sentiment</th>
                </tr>
        """
        
        for row in rows:
            subject, sender, priority, reason, _, sentiment = row
            
            # Determine priority class
            if priority >= 4:
                priority_class = "priority-high"
            elif priority >= 3:
                priority_class = "priority-medium"
            else:
                priority_class = "priority-low"
                
            html += f"""
                <tr>
                    <td>{subject}</td>
                    <td>{sender}</td>
                    <td class="{priority_class}">{priority}</td>
                    <td>{reason}</td>
                    <td>{sentiment}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        # Write to file
        with open('email_analysis_report.html', 'w') as f:
            f.write(html)
        
        print("Report generated: email_analysis_report.html")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        analysis_conn.close()

def generate_sent_emails_report(output_file='sent_emails_report.html'):
    """Generate a report of emails sent by eddiekempe@gmail.com."""
    # Connect to databases
    email_store = create_engine(f'sqlite:///{DATABASE_CONFIG["EMAIL_DB_FILE"]}')
    analysis_db = create_engine(f'sqlite:///{DATABASE_CONFIG["ANALYSIS_DB_FILE"]}')
    
    # Get sent emails and their analysis
    query = """
    SELECT 
        e.id,
        e.subject,
        e.from_address,
        e.received_date,
        e.labels,
        a.priority_score,
        a.priority_reason,
        a.action_needed,
        a.action_deadline
    FROM emails e
    LEFT JOIN email_analysis a ON e.id = a.email_id
    WHERE e.from_address LIKE '%eddiekempe@gmail.com%'
    ORDER BY e.received_date DESC
    """
    
    with email_store.connect() as conn:
        results = pd.read_sql(query, conn, parse_dates=['received_date'])
    
    # Generate HTML report
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sent Emails Analysis Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { background-color: #f8f9fa; padding: 20px; margin-bottom: 20px; }
            .email-card { 
                border: 1px solid #ddd; 
                margin: 10px 0; 
                padding: 15px;
                border-radius: 5px;
            }
            .priority-5 { border-left: 5px solid #dc3545; }
            .priority-4 { border-left: 5px solid #fd7e14; }
            .priority-3 { border-left: 5px solid #ffc107; }
            .priority-2 { border-left: 5px solid #20c997; }
            .priority-1 { border-left: 5px solid #6c757d; }
            .metadata { color: #666; font-size: 0.9em; }
            .action { background-color: #e9ecef; padding: 10px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Sent Emails Analysis Report</h1>
            <p>Generated on: {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}</p>
            <p>Total Sent Emails: {{ len(results) }}</p>
        </div>
        
        {% for _, email in results.iterrows() %}
        <div class="email-card priority-{{ email.priority_score if not pd.isna(email.priority_score) else '3' }}">
            <h3>{{ email.subject }}</h3>
            <div class="metadata">
                <p>Date: {{ email.received_date.strftime('%Y-%m-%d %H:%M:%S') }}</p>
                <p>Labels: {{ email.labels }}</p>
                {% if not pd.isna(email.priority_score) %}
                <p>Priority: {{ email.priority_score }}/5 - {{ email.priority_reason }}</p>
                {% endif %}
            </div>
            {% if not pd.isna(email.action_needed) and email.action_needed %}
            <div class="action">
                <p><strong>Action Needed:</strong> {{ email.action_needed }}</p>
                {% if not pd.isna(email.action_deadline) %}
                <p><strong>Deadline:</strong> {{ email.action_deadline }}</p>
                {% endif %}
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </body>
    </html>
    """
    
    # Render template
    env = Environment(loader=BaseLoader())
    template = env.from_string(template)
    html = template.render(results=results, datetime=datetime, pd=pd, len=len)
    
    # Save report
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Found {len(results)} sent emails")
    print(f"Report generated: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--sent':
        generate_sent_emails_report()
    else:
        generate_html_report()
