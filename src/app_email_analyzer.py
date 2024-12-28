#!/usr/bin/env python3
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
import logging
import os
from shared_lib.anthropic_lib import parse_claude_response
import json
import time
import argparse
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session
from models.email import Email
from models.email_analysis import EmailAnalysis, EmailAnalysisResponse
from shared_lib.database_session_util import get_email_session, get_analysis_session
import sqlalchemy.exc
from structlog import get_logger
from prometheus_client import start_http_server as start_prometheus_server
from shared_lib.constants import API_CONFIG, EMAIL_CONFIG, METRICS_CONFIG, ERROR_MESSAGES, DEFAULT_MODEL, DATABASE_CONFIG
import anthropic  # <--- Added missing anthropic import
import re

# Set up structured logging
logger = get_logger()

def start_metrics_server(port: int) -> None:
    """Start Prometheus metrics server."""
    try:
        start_prometheus_server(port)
        logger.info("metrics_server_started", port=port)
    except Exception as e:
        logger.error("metrics_server_error", error=str(e))

"""Email analyzer using Claude-3-Haiku for processing and categorizing emails.

This module provides functionality to analyze emails using the Anthropic Claude API.
It processes emails in batches, analyzes their content, and stores the results in a database.

Note on SSL/Network Configuration:
    - If you encounter SSL certificate verification errors, check if you're connected to a corporate VPN
    - Corporate VPNs often use self-signed certificates which can interfere with API connections
    - Disconnect from VPN if experiencing SSL certificate chain errors
    - The script uses Python's default certificate handling when not on VPN

Dependencies:
    - anthropic: For Claude API access
    - sqlalchemy: For database operations
    - python-dotenv: For environment variable management

Environment Variables:
    - ANTHROPIC_API_KEY: Required for Claude API authentication
"""

class EmailAnalyzer:
    """Analyzes emails using Claude-3-Haiku with improved error handling and validation.
    
    This analyzer uses the Claude-3-Haiku model exclusively for consistent performance and cost efficiency.
    Do not change to other models without thorough testing and approval.
    
    Model Requirements:
    - Always use claude-3-haiku-20240307
    - Keep max_tokens_to_sample at 1000 for consistent response sizes
    - Use temperature=0 for deterministic outputs
    
    Note: For known issues and solutions, see docs/troubleshooting.md
    """

    def __init__(self, metrics_port: int = 8000):
        """Initialize the analyzer with API client and start metrics server."""
        load_dotenv(verbose=True)
        
        # Verify environment
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY not found in environment")
        
        # Log first few characters of API key for verification (safely)
        logger.info(
            "api_key_check",
            prefix=api_key[:7] if len(api_key) > 7 else "too_short",
            length=len(api_key)
        )
            
        # Initialize API client
        self.client = anthropic.Client(api_key=api_key)
        
        # Start metrics server
        start_metrics_server(metrics_port)
        logger.info("analyzer_initialized", metrics_port=metrics_port)

    def analyze_email(self, email_data: Dict[str, Any]) -> Optional[EmailAnalysis]:
        """Analyze a single email using Anthropic API.
        
        Args:
            email_data: Dictionary containing email data with fields:
                - id: Email ID
                - thread_id: Thread ID
                - subject: Email subject
                - content: Email content
                - date: Email received date
                - labels: List of labels
                
        Returns:
            EmailAnalysis object if successful, None if failed
        """
        try:
            # Extract URLs from content
            full_urls, display_urls = self._extract_urls(email_data.get('content', ''))
            
            # Create prompt using template
            content = API_CONFIG['EMAIL_ANALYSIS_PROMPT'].format(
                email_content=f"""Subject: {email_data.get('subject', '')}
Content: {email_data.get('content', '')}"""
            )

            # Get analysis from API
            response = None
            try:
                response = self.client.messages.create(
                    model=API_CONFIG['MODEL'],
                    max_tokens=API_CONFIG['MAX_TOKENS'],
                    temperature=API_CONFIG['TEMPERATURE'],
                    messages=[{
                        "role": "user",
                        "content": content
                    }]
                )
                
                # Extract and parse JSON from response
                analysis_data = parse_claude_response(response.content)
                if analysis_data is None:
                    logger.error(
                        ERROR_MESSAGES['API_ERROR'].format(error="Failed to parse API response"),
                        error_type="parsing",
                        response=response.content if response else None
                    )
                    return None
                
                # Create EmailAnalysis object with extracted URLs
                analysis_response = EmailAnalysisResponse(**analysis_data)
                return EmailAnalysis.from_api_response(
                    email_id=email_data['id'],
                    thread_id=email_data.get('thread_id', ''),
                    response=analysis_response,
                    links_found=full_urls,
                    links_display=display_urls,
                    analyzed_date=datetime.now()  # Add analyzed_date
                )
            except Exception as e:
                error_context = {
                    'error_type': "analysis",
                    'error': str(e),
                    'response': response.content if response else None,
                    'email_id': email_data.get('id'),
                    'subject': email_data.get('subject', '')
                }
                logger.error(ERROR_MESSAGES['API_ERROR'].format(error=str(e)), **error_context)
                return None
        except Exception as e:
            logger.error(ERROR_MESSAGES['API_ERROR'].format(error=str(e)), 
                        error_type="analysis",
                        error=str(e))
            return None

    def _extract_urls(self, text: str) -> Tuple[List[str], List[str]]:
        """Extract URLs from text and create display versions.
        
        Args:
            text: The text to extract URLs from
            
        Returns:
            Tuple of (full_urls, display_urls) where display_urls are truncated
        """
        # This pattern matches URLs starting with http:// or https://
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+' 
        
        # Find all URLs in the text
        full_urls = re.findall(url_pattern, text)
        
        # Create display versions (truncated to 50 chars)
        display_urls = [url[:47] + "..." if len(url) > 50 else url 
                       for url in full_urls]
        
        return full_urls, display_urls

    def save_analysis(self, email_id: str, thread_id: str, analysis: EmailAnalysisResponse, raw_json: str):
        """Save the analysis to the database."""
        try:
            with get_analysis_session() as session:
                # Extract URLs from content
                full_urls, display_urls = self._extract_urls(raw_json)
                
                # Create or update analysis object
                existing = session.query(EmailAnalysis).filter_by(
                    email_id=email_id, thread_id=thread_id
                ).first()
                
                # Create new analysis object with URLs
                analysis_obj = EmailAnalysis.from_api_response(
                    email_id=email_id,
                    thread_id=thread_id,
                    response=analysis,
                    links_found=full_urls,
                    links_display=display_urls
                )
                
                if existing:
                    # Update existing analysis
                    for key, value in analysis_obj.__dict__.items():
                        if key != '_sa_instance_state':  # Skip SQLAlchemy internal state
                            setattr(existing, key, value)
                    session.merge(existing)
                else:
                    # Add new analysis
                    session.add(analysis_obj)
                
                session.commit()
                logger.info(
                    "analysis_saved",
                    email_id=email_id,
                    action="updated" if existing else "created"
                )
                
        except Exception as e:
            logger.error(
                "Failed to save analysis",
                error=str(e),
                email_id=email_id,
                thread_id=thread_id
            )
            raise

    def process_unanalyzed_emails(self):
        """Process all unanalyzed emails from the email store."""
        try:
            with get_email_session() as email_session, get_analysis_session() as analysis_session:
                # Get unanalyzed emails using SQLAlchemy ORM
                unanalyzed = (
                    email_session.query(Email)
                    .outerjoin(EmailAnalysis, and_(
                        Email.id == EmailAnalysis.email_id,
                        Email.thread_id == EmailAnalysis.thread_id
                    ))
                    .filter(EmailAnalysis.email_id == None)
                    .with_entities(
                        Email.id,
                        Email.subject,
                        Email.from_address.label('sender'),
                        Email.received_date.label('date'),
                        Email.content.label('body'),
                        Email.labels,
                        Email.full_api_response,
                        Email.thread_id
                    )
                    .all()
                )
                
                if not unanalyzed:
                    logger.info("no_unanalyzed_emails_found")
                    return
                
                # Process up to 500 emails at a time
                for i in range(0, len(unanalyzed), 500):
                    batch = unanalyzed[i:i+500]
                    logger.info("processing_batch", start=i, count=len(batch))
                    
                    # Process the batch
                    self.process_emails(count=len(batch))
                    
                    # Rate limit between large batches
                    if i + 500 < len(unanalyzed):
                        time.sleep(EMAIL_CONFIG['RATE_LIMIT']['PAUSE_SECONDS'])
                        
        except Exception as e:
            logger.error("process_unanalyzed_error", error=str(e))
            raise

    def process_emails(self, count: int = EMAIL_CONFIG['COUNT']):
        """Process a batch of unanalyzed emails."""
        try:
            # Test API connection first
            try:
                test_response = self.client.messages.create(
                    model=API_CONFIG['TEST_MODEL'],
                    max_tokens=API_CONFIG['MAX_TOKENS_TEST'],
                    temperature=API_CONFIG['TEMPERATURE'],
                    messages=[{"role": "user", "content": "test"}]
                )
            except Exception as e:
                logger.error(f"API connection test failed: {str(e)}")
                return

            with get_email_session() as email_session, get_analysis_session() as analysis_session:
                # Get unanalyzed emails using SQLAlchemy ORM
                unanalyzed = (
                    email_session.query(Email)
                    .outerjoin(EmailAnalysis, and_(
                        Email.id == EmailAnalysis.email_id,
                        Email.thread_id == EmailAnalysis.thread_id
                    ))
                    .filter(EmailAnalysis.email_id == None)
                    .with_entities(
                        Email.id,
                        Email.subject,
                        Email.from_address.label('sender'),
                        Email.received_date.label('date'),
                        Email.content.label('body'),
                        Email.labels,
                        Email.full_api_response,
                        Email.thread_id
                    )
                    .limit(count)
                    .all()
                )
                
                if not unanalyzed:
                    logger.info("no_unanalyzed_emails_found")
                    return
                    
                logger.info("processing_batch", count=len(unanalyzed))
                
                # Process each email
                for i, email_data in enumerate(unanalyzed):
                    # Rate limit: Process batch of emails then pause to avoid hitting API limits
                    if i > 0 and i % EMAIL_CONFIG['BATCH_SIZE'] == 0:
                        logger.info("rate_limit_pause", processed=i)
                        time.sleep(EMAIL_CONFIG['RATE_LIMIT']['PAUSE_SECONDS'])
                        
                    try:
                        email_data = dict(email_data)
                        
                        # Format email for analysis
                        truncated_body = email_data.get('body', '')[:5000]
                        email_type = "internal" if "@company.com" in email_data.get('sender', '') else "external"
                        
                        email_request = EmailRequest(
                            id=email_data.get('id', ''),
                            subject=email_data.get('subject', ''),
                            body=email_data.get('body', ''),
                            sender=email_data.get('sender', ''),
                            date=email_data.get('date', ''),
                            labels=email_data.get('labels', '[]'),
                            full_api_response=email_data.get('full_api_response', '{}'),
                            email_type=email_type,
                            truncated_body=truncated_body
                        )
                        
                        # Call Claude API for analysis with retry
                        max_retries = EMAIL_CONFIG['MAX_RETRIES']
                        retry_delay = EMAIL_CONFIG['RETRY_DELAY']  # seconds
                        
                        for retry in range(max_retries):
                            try:
                                prompt = API_CONFIG['EMAIL_ANALYSIS_PROMPT'].format(
                                    email_content=f"""Subject: {email_request.subject}
Content: {email_request.truncated_body}"""
                                )
                                
                                response = self.client.messages.create(
                                    model=API_CONFIG['MODEL'],
                                    max_tokens=API_CONFIG['MAX_TOKENS'],
                                    temperature=API_CONFIG['TEMPERATURE'],
                                    messages=[{
                                        "role": "user",
                                        "content": prompt
                                    }]
                                )
                                # Extract URLs from email content
                                links_found, links_display = self._extract_urls(email_data.get('body', ''))
                                
                                # Parse response and validate
                                analysis_data = parse_claude_response(response.content)
                                if not analysis_data:
                                    logger.error(
                                        "Failed to parse API response",
                                        email_id=email_request.id,
                                        response=response.content
                                    )
                                    continue
                                
                                # Create EmailAnalysisResponse
                                analysis_response = EmailAnalysisResponse(**analysis_data)
                                
                                # Save analysis with URLs
                                self.save_analysis(
                                    email_id=email_data.get('id', ''),
                                    thread_id=email_data.get('thread_id', email_data.get('id', '')),
                                    analysis=analysis_response,
                                    raw_json=email_data.get('body', '')  # For URL extraction
                                )
                                
                                logger.info(
                                    "email_analyzed",
                                    email_id=email_request.id,
                                    subject=email_request.subject
                                )
                                break  # Success, exit retry loop
                            except Exception as api_error:
                                if retry < max_retries - 1:
                                    logger.warning(f"API call failed (attempt {retry + 1}/{max_retries}), retrying in {retry_delay} seconds...")
                                    time.sleep(retry_delay)
                                    retry_delay *= 2  # Exponential backoff
                                else:
                                    raise api_error

                    except Exception as e:
                        logger.error("process_email_error", error=str(e))
                        continue

        except Exception as e:
            logger.error("process_emails_error", error=str(e))
            raise

from dataclasses import dataclass
from typing import Optional

@dataclass
class EmailRequest:
    """Data class for email analysis request."""
    id: str
    subject: str
    body: str
    sender: str
    date: str
    labels: str
    full_api_response: str  # Complete Gmail API response for future reference
    email_type: str
    truncated_body: str

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def log_api_error(error_type: str, error_message: str, response_text: str = None) -> None:
    """Log an API error with context."""
    logger.error(
        "api_error",
        error_type=error_type,
        error=error_message,
        response=response_text if response_text else "N/A"
    )

def log_validation_error(error_type: str, error_message: str, response_text: str = None) -> None:
    """Log a validation error with context."""
    logger.error(
        "validation_error",
        error_type=error_type,
        error=error_message,
        response=response_text if response_text else "N/A"
    )

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Email analyzer with configurable email count')
    parser.add_argument('--count', type=int, default=EMAIL_CONFIG['COUNT'],
                      help='Number of emails to process (default: {})'.format(EMAIL_CONFIG['COUNT']))
    args = parser.parse_args()

    try:
        analyzer = EmailAnalyzer()
        analyzer.process_emails(count=args.count)
    except Exception as e:
        logger.error("main_error", error=str(e))
        raise

if __name__ == "__main__":
    main()
