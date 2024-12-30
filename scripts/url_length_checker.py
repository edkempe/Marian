#!/usr/bin/env python3
"""
URL Length Checker Utility
-------------------------
A diagnostic tool that scans the email_analysis database for URLs exceeding
a specified length threshold. This helps identify potentially problematic
URLs that might cause issues in processing or storage.

Usage:
    python util_check_urls.py [--threshold=100]

The script will:
1. Connect to email_analysis.db
2. Check all URLs stored in the links_found column
3. Report any URLs longer than the threshold
4. Display the email ID, URL length, and the URL itself

This is useful for:
- Identifying unusually long URLs that might need special handling
- Debugging URL-related issues in email processing
- Monitoring URL patterns in analyzed emails
"""

import argparse
import json
import logging
from typing import List, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.email_analysis import EmailAnalysis

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_long_urls(threshold: int = 100) -> List[Tuple[str, str, int]]:
    """
    Check for URLs longer than the specified threshold.

    Args:
        threshold: Maximum acceptable URL length (default: 100)

    Returns:
        List of tuples containing (email_id, url, length) for long URLs
    """
    try:
        # Create SQLAlchemy engine and session
        engine = create_engine("sqlite:///email_analysis.db")
        Session = sessionmaker(bind=engine)
        session = Session()

        long_urls = []

        # Query all email analyses with links
        analyses = (
            session.query(EmailAnalysis)
            .filter(EmailAnalysis.links_found.isnot(None))
            .all()
        )

        for analysis in analyses:
            try:
                # Parse links_found JSON
                if not analysis.links_found:
                    continue

                links = json.loads(analysis.links_found)
                if not isinstance(links, list):
                    logger.warning(
                        f"Invalid links format for email {analysis.email_id}"
                    )
                    continue

                # Check each URL's length
                for url in links:
                    url_length = len(url)
                    if url_length > threshold:
                        long_urls.append((analysis.email_id, url, url_length))

            except json.JSONDecodeError:
                logger.error(
                    f"Failed to parse links JSON for email {analysis.email_id}"
                )
                continue

        return sorted(long_urls, key=lambda x: x[2], reverse=True)

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return []

    finally:
        session.close()


def main():
    """Main entry point for the URL checker utility."""
    parser = argparse.ArgumentParser(
        description="Check for long URLs in email analysis database"
    )
    parser.add_argument(
        "--threshold", type=int, default=100, help="URL length threshold (default: 100)"
    )
    args = parser.parse_args()

    logger.info(f"Checking for URLs longer than {args.threshold} characters...")

    long_urls = check_long_urls(args.threshold)

    if not long_urls:
        logger.info("No URLs found exceeding the length threshold.")
        return

    logger.info(f"Found {len(long_urls)} URLs exceeding threshold:")
    for email_id, url, length in long_urls:
        logger.info(f"Email {email_id}: URL length {length}")
        logger.info(f"URL: {url}\n")


if __name__ == "__main__":
    main()
