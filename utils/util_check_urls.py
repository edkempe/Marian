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

import sqlite3
import json
import argparse
import logging
from typing import List, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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
        conn = sqlite3.connect('email_analysis.db')
        cur = conn.cursor()
        
        # Get all URLs from links_found
        cur.execute('SELECT email_id, links_found FROM email_analysis')
        results = cur.fetchall()
        
        long_urls = []
        for email_id, links in results:
            if not links:
                continue
                
            try:
                urls = json.loads(links)
                for url in urls:
                    if len(url) > threshold:
                        long_urls.append((email_id, url, len(url)))
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in links_found for email_id: {email_id}")
                continue
        
        return long_urls
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []
    finally:
        conn.close()

def main():
    """Main entry point for the URL checker utility."""
    parser = argparse.ArgumentParser(description='Check for long URLs in email analysis database')
    parser.add_argument('--threshold', type=int, default=100,
                       help='URL length threshold (default: 100)')
    args = parser.parse_args()
    
    logger.info(f"Checking for URLs longer than {args.threshold} characters...")
    
    long_urls = check_long_urls(args.threshold)
    
    if long_urls:
        logger.info(f"Found {len(long_urls)} URLs longer than {args.threshold} characters:")
        for email_id, url, length in long_urls:
            print(f"\nEmail ID: {email_id}")
            print(f"URL Length: {length}")
            print(f"URL: {url}")
    else:
        logger.info(f"No URLs longer than {args.threshold} characters found.")

if __name__ == "__main__":
    main()
