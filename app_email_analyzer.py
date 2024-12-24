#!/usr/bin/env python3
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
import anthropic
import json
import time
import argparse
from dotenv import load_dotenv
from sqlalchemy import text
import sqlalchemy.exc
from structlog import get_logger
from prometheus_client import start_http_server as start_prometheus_server
from database.config import get_email_session, get_analysis_session
from models.email_analysis import EmailAnalysis, EmailAnalysisResponse
from constants import API_CONFIG, EMAIL_CONFIG, METRICS_CONFIG

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
    
    Known Issues:
    1. Claude API Response Formatting:
       - The API may prefix responses with text like "Here is the JSON response:"
       - This causes json.loads() to fail with "Expecting value: line 1 column 2 (char 1)"
       - Solution: Use _extract_json() to clean the response
       
    2. JSON Validation:
       - Sometimes the API response may be missing required fields
       - Always validate the JSON structure before processing
       - Use empty strings/arrays instead of null values
       
    Model Requirements:
    - Always use claude-3-haiku-20240307
    - Keep max_tokens_to_sample at 1000 for consistent response sizes
    - Use temperature=0 for deterministic outputs
    
    Example API Response Issues:
    1. "Here is the JSON response: {...}"
    2. "{...} Hope this helps!"
    3. "I've analyzed the email. Here's the JSON: {...}"
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
            # Format email data for analysis
            content = API_CONFIG['EMAIL_ANALYSIS_PROMPT'].format(
                email_content=f"""Subject: {email_data.get('subject', '')}
Content: {email_data.get('content', '')}"""
            )

            # Get analysis from API
            response = None
            try:
                response = self.client.messages.create(
                    model=API_CONFIG['ANTHROPIC_MODEL'],
                    max_tokens=API_CONFIG['MAX_TOKENS'],
                    temperature=API_CONFIG['TEMPERATURE'],
                    messages=[{
                        "role": "user",
                        "content": content
                    }]
                )
                # Parse API response
                analysis_data = json.loads(response.content[0].text)
                
                # Create and return EmailAnalysis object
                return EmailAnalysis.from_api_response(
                    email_id=email_data['id'],
                    thread_id=email_data.get('thread_id', ''),
                    response=EmailAnalysisResponse(**analysis_data)
                )
            except Exception as e:
                error_context = {
                    'error_type': "analysis",
                    'error': str(e),
                    'response': response.content[0].text if response and hasattr(response, 'content') else None,
                    'email_id': email_data.get('id'),
                    'subject': email_data.get('subject', '')
                }
                logger.error(API_CONFIG['ERROR_MESSAGES']["api_error"].format(error=str(e)), **error_context)
                return None
        except Exception as e:
            logger.error(API_CONFIG['ERROR_MESSAGES']["api_error"].format(error=str(e)), 
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
                # Check if analysis already exists
                existing = session.query(EmailAnalysis).filter_by(
                    email_id=email_id, thread_id=thread_id
                ).first()
                
                # Create or update analysis object
                analysis_obj = existing or EmailAnalysis(email_id=email_id, thread_id=thread_id)
                
                # Convert action_deadline to datetime if present
                if analysis.action_deadline:
                    try:
                        action_deadline = datetime.strptime(analysis.action_deadline, '%Y-%m-%d')
                    except ValueError:
                        action_deadline = None
                else:
                    action_deadline = None
                
                # Update fields
                analysis_obj.summary = analysis.summary[:100]  # Update summary field
                analysis_obj.category = ','.join(analysis.category)
                analysis_obj.priority_score = analysis.priority_score
                analysis_obj.priority_reason = analysis.priority_reason
                analysis_obj.action_needed = analysis.action_needed
                analysis_obj.action_type = ','.join(analysis.action_type)
                analysis_obj.action_deadline = action_deadline
                analysis_obj.key_points = ','.join(analysis.key_points)
                analysis_obj.people_mentioned = ','.join(analysis.people_mentioned)
                analysis_obj.links_found = ','.join(analysis.links_found)
                analysis_obj.links_display = ','.join(analysis.links_display)
                analysis_obj.project = analysis.project
                analysis_obj.topic = analysis.topic
                analysis_obj.sentiment = analysis.sentiment
                analysis_obj.confidence_score = analysis.confidence_score
                analysis_obj.analysis_date = datetime.now(timezone.utc)
                
                try:
                    analysis_obj.raw_analysis = json.loads(raw_json)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON for email {email_id}: {str(e)}")
                    analysis_obj.raw_analysis = {}
                analysis_obj.full_api_response = raw_json

                if not existing:
                    session.add(analysis_obj)
                session.commit()
                
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"Database integrity error for email {email_id}: {str(e)}")
            raise RuntimeError(f"Database integrity error: {str(e)}")
        except Exception as e:
            logger.error(f"Database error for email {email_id}: {str(e)}")
            raise RuntimeError(f"Database error: {str(e)}")

    def process_emails(self, count: int = EMAIL_CONFIG['COUNT']):
        """Process a batch of unanalyzed emails."""
        try:
            # Test API connection first
            try:
                test_response = self.client.messages.create(
                    model=API_CONFIG['TEST_MODEL'],
                    max_tokens=API_CONFIG['API_TEST_MAX_TOKENS'],
                    temperature=API_CONFIG['TEMPERATURE'],
                    messages=[{"role": "user", "content": "test"}]
                )
            except Exception as e:
                logger.error(f"API connection test failed: {str(e)}")
                return

            with get_email_session() as email_session, get_analysis_session() as analysis_session:
                # Get unanalyzed emails
                email_session.execute(text("ATTACH DATABASE 'db_email_analysis.db' AS analysis_db"))
                
                unanalyzed = email_session.execute(text("""
                    SELECT e.id, e.subject, e.from_address as sender, e.received_date as date, e.content as body,
                           e.labels, e.full_api_response, e.thread_id
                    FROM emails e
                    WHERE NOT EXISTS (
                        SELECT 1 FROM analysis_db.email_analysis a 
                        WHERE a.email_id = e.id AND a.thread_id = e.thread_id
                    )
                    LIMIT :count
                """), {"count": count}).mappings().all()
                
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
                                    model=API_CONFIG['ANTHROPIC_MODEL'],
                                    max_tokens=API_CONFIG['MAX_TOKENS'],
                                    temperature=API_CONFIG['TEMPERATURE'],
                                    messages=[{
                                        "role": "user",
                                        "content": prompt
                                    }]
                                )
                                break  # Success, exit retry loop
                            except Exception as api_error:
                                if retry < max_retries - 1:
                                    logger.warning(f"API call failed (attempt {retry + 1}/{max_retries}), retrying in {retry_delay} seconds...")
                                    time.sleep(retry_delay)
                                    retry_delay *= 2  # Exponential backoff
                                else:
                                    raise api_error

                        # Extract and validate the analysis
                        try:
                            analysis_json = response.content[0].text
                            analysis = json.loads(analysis_json)
                            
                            # Ensure links_display is present
                            if 'links_found' in analysis and 'links_display' not in analysis:
                                analysis['links_display'] = [
                                    url[:100] + '...' if len(url) > 100 else url
                                    for url in analysis['links_found']
                                ]
                            
                            # Set default empty string for project if it's None
                            if analysis.get('project') is None:
                                analysis['project'] = ""
                            
                            analysis_response = EmailAnalysisResponse.model_validate(analysis)
                            
                            # Create EmailAnalysis instance with thread_id
                            email_analysis = EmailAnalysis.from_api_response(
                                email_id=email_data.get('id', ''),
                                thread_id=email_data.get('thread_id', email_data.get('id', '')),  # Fallback to email_id if thread_id not present
                                response=analysis_response
                            )
                            
                            # Save analysis with thread_id
                            self.save_analysis(
                                email_id=email_data.get('id', ''),
                                thread_id=email_data.get('thread_id', email_data.get('id', '')),  # Fallback to email_id if thread_id not present
                                analysis=email_analysis,
                                raw_json=analysis_json
                            )
                        except json.JSONDecodeError as e:
                            log_api_error('json_decode', str(e))
                            continue
                        except Exception as e:
                            log_api_error('validation', str(e))
                            continue
                            
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
