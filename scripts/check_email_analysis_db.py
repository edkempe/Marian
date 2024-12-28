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
                    Default: sqlite:///data/db_email_analysis.db
"""

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import json
import os
import sys
import logging
from models.email_analysis import EmailAnalysis

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
        # Create database engine and session
        db_url = os.getenv('ANALYSIS_DB_URL', 'sqlite:///data/db_email_analysis.db')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Get total count using ORM
            total_count = session.query(EmailAnalysis).count()
            logger.info(f"Total analyzed emails: {total_count}")

            # Get latest 5 records using ORM
            latest_records = (
                session.query(EmailAnalysis)
                .order_by(desc(EmailAnalysis.analysis_date))
                .limit(5)
                .all()
            )

            if not latest_records:
                logger.warning("No records found in database")
                return

            # Display latest records
            logger.info("\nLatest analyzed emails:")
            for record in latest_records:
                # Format summary for display
                summary = record.summary[:100] + "..." if record.summary and len(record.summary) > 100 else record.summary

                logger.info("-" * 80)
                logger.info(f"Email ID: {record.email_id}")
                logger.info(f"Thread ID: {record.thread_id}")
                logger.info(f"Analysis Date: {record.analysis_date}")
                logger.info(f"Summary: {summary}")
                logger.info(f"Priority Score: {record.priority_score}")
                logger.info(f"Action Needed: {record.action_needed}")
                logger.info(f"Project: {record.project}")
                logger.info(f"Topic: {record.topic}")

        finally:
            session.close()

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    check_database()
