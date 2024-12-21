"""
Utility script to check the contents of the email analysis database.

This script provides a quick way to verify:
- Total number of analyzed emails
- Latest analyzed emails and their details
- Data integrity of analyzed emails

Usage:
    python util_email_analysis_db.py

Environment Variables:
    ANALYSIS_DB_URL: URL for the email analysis database
                    Default: sqlite:///db_email_analysis.db
"""

from sqlalchemy import create_engine, text, Engine, Connection, Row
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import json
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_database() -> None:
    """
    Check and display the contents of the email analysis database.
    
    Displays:
    - Total number of records
    - Latest 5 records with their details including:
        - Email ID
        - Thread ID
        - Analysis Date
        - Summary (truncated)
        - Priority Score
        - Action Needed flag
        - Project
        - Topic
    
    Raises:
        SQLAlchemyError: If there's an error connecting to or querying the database
    """
    try:
        # Use the same database URL as the main application
        analysis_db_url = os.getenv('ANALYSIS_DB_URL', 'sqlite:///db_email_analysis.db')
        logger.info(f"Connecting to database at: {analysis_db_url}")
        
        engine = create_engine(analysis_db_url)
        
        with engine.connect() as conn:
            try:
                # Get total count
                result = conn.execute(text("SELECT COUNT(*) as count FROM email_analysis"))
                total = result.fetchone()[0]
                print(f"\nTotal records: {total}")
                
                # Get latest 5 records
                result = conn.execute(text("SELECT * FROM email_analysis ORDER BY analysis_date DESC LIMIT 5"))
                
                print("\nLatest 5 records:")
                for row in result:
                    print("\n-------------------")
                    print(f"Email ID: {row.email_id}")
                    print(f"Thread ID: {row.thread_id}")
                    print(f"Analysis Date: {row.analysis_date}")
                    print(f"Summary: {row.summary[:100]}...")
                    print(f"Priority Score: {row.priority_score}")
                    print(f"Action Needed: {row.action_needed}")
                    print(f"Project: {row.project}")
                    print(f"Topic: {row.topic}")
                
                logger.info("Database check completed successfully")
                
            except SQLAlchemyError as e:
                logger.error(f"Error querying database: {str(e)}")
                raise
                
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    check_database()
