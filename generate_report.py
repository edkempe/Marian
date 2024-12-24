#!/usr/bin/env python3
import sqlite3
from datetime import datetime
import os

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

if __name__ == "__main__":
    generate_html_report()
