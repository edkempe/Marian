#!/usr/bin/env python3
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
import anthropic
from dotenv import load_dotenv
from contextlib import contextmanager
import time
import json
import ssl
import certifi
import re
from sqlalchemy import text
import argparse

from models.email import Email
from models.email_analysis import EmailAnalysisResponse, EmailAnalysis
from database.config import get_email_session, get_analysis_session
from util_logging import (
    logger, EMAIL_ANALYSIS_COUNTER, EMAIL_ANALYSIS_DURATION,
    log_validation_error, start_metrics_server
)

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

    # Standard prompt template for consistent API responses
    ANALYSIS_PROMPT = """Analyze the email below and provide a structured response with the following information:
1. A brief summary of the main points (1-2 sentences)
2. List of categories that best describe the email content (e.g., meeting, request, update)
3. Priority score (1-5) where:
   1 = Low priority (FYI only)
   2 = Normal priority (routine task/update)
   3 = Medium priority (needs attention this week)
   4 = High priority (needs attention today)
   5 = Urgent (needs immediate attention)
4. Priority reason explaining the score
5. Action assessment:
   - action_needed: true/false if any action is required
   - action_type: list of required actions (e.g., ["reply", "review", "schedule"])
   - action_deadline: YYYY-MM-DD format if there's a deadline, null if none
6. List of key points from the email
7. List of people mentioned
8. Context:
   - project: project name if mentioned
   - topic: general topic/subject matter
9. Overall sentiment (positive/negative/neutral)
10. Confidence score (0.0-1.0) for the analysis

Format the response as a JSON object with these exact field names:
{{"summary": "brief summary", "category": ["category1"], "priority_score": 1-5, "priority_reason": "reason", "action_needed": true/false, "action_type": ["action1"], "action_deadline": "YYYY-MM-DD", "key_points": ["point1"], "people_mentioned": ["person1"], "project": "project name", "topic": "topic", "sentiment": "positive/negative/neutral", "confidence_score": 0.9}}

Email to analyze:
{text}

JSON response:"""

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
        """Analyze a single email and return structured analysis."""
        try:
            # Extract URLs from the email body first
            body = email_data.get('body', '')
            full_urls, display_urls = self._extract_urls(body)
            
            # Format the email content for analysis
            email_content = f"""Subject: {email_data.get('subject', '')}
From: {email_data.get('sender', '')}
Type: {email_data.get('email_type', '')}
Labels: {email_data.get('labels', '')}
Thread ID: {email_data.get('thread_id', '')}
Date: {email_data.get('date', '')}
Has Attachments: {email_data.get('has_attachments', False)}

Content:
{body}"""
            
            # Get analysis from Claude
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,  # Increased from 1000 to handle longer responses
                temperature=0.05,
                messages=[{
                    "role": "user",
                    "content": self.ANALYSIS_PROMPT.format(
                        text=email_content
                    )
                }]
            )

            # Extract response content
            response_text = response.content[0].text
            
            # Clean and truncate URLs if needed
            try:
                response_json = json.loads(response_text)
                # Add our pre-extracted URLs
                response_json["links_found"] = full_urls
                response_json["links_display"] = display_urls
                response_text = json.dumps(response_json)
            except json.JSONDecodeError:
                logger.error("json_decode_error", error="Failed to parse initial JSON response")
                return None

            # Extract and validate the analysis
            try:
                analysis = json.loads(response_text)
                
                # Validate the analysis response
                analysis_response = EmailAnalysisResponse(
                    summary=analysis.get('summary', ''),
                    category=analysis.get('category', []),
                    priority_score=analysis.get('priority_score', 1),
                    priority_reason=analysis.get('priority_reason', ''),
                    action_needed=analysis.get('action_needed', False),
                    action_type=analysis.get('action_type', []),
                    action_deadline=analysis.get('action_deadline'),
                    key_points=analysis.get('key_points', []),
                    people_mentioned=analysis.get('people_mentioned', []),
                    links_found=full_urls,
                    links_display=display_urls,
                    project=analysis.get('project', ''),
                    topic=analysis.get('topic', ''),
                    sentiment=analysis.get('sentiment', 'neutral'),
                    confidence_score=analysis.get('confidence_score', 0.9)
                )
                
                # Create and return EmailAnalysis instance
                return EmailAnalysis.from_response(
                    email_id=email_data['id'],
                    thread_id=email_data['thread_id'],
                    response=analysis_response
                )
                
            except json.JSONDecodeError as e:
                log_api_error('json_decode', str(e), response_text)
                return None
            except Exception as e:
                log_api_error('validation', str(e), response_text)
                return None

        except Exception as e:
            log_api_error('api_call', str(e))
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
                existing = session.query(EmailAnalysis).filter_by(email_id=email_id).first()
                analysis_obj = existing or EmailAnalysis(email_id=email_id, thread_id=thread_id)
                
                # Update fields
                analysis_obj.summary = analysis.summary[:100]  # Update summary field
                analysis_obj.category = analysis.category
                analysis_obj.priority_score = analysis.priority_score
                analysis_obj.priority_reason = analysis.priority_reason
                analysis_obj.action_needed = analysis.action_needed
                analysis_obj.action_type = analysis.action_type
                analysis_obj.action_deadline = analysis.action_deadline
                analysis_obj.key_points = analysis.key_points
                analysis_obj.people_mentioned = analysis.people_mentioned
                analysis_obj.links_found = analysis.links_found
                analysis_obj.links_display = analysis.links_display
                analysis_obj.project = analysis.project
                analysis_obj.topic = analysis.topic
                analysis_obj.sentiment = analysis.sentiment
                analysis_obj.confidence_score = analysis.confidence_score
                analysis_obj.analysis_date = datetime.now(timezone.utc)
                analysis_obj.raw_analysis = json.loads(raw_json)

                if not existing:
                    session.add(analysis_obj)
                session.commit()
        except Exception as e:
            logger.error("database_error", error=str(e), email_id=email_id)

    def process_emails(self, batch_size: int = 50):
        """Process a batch of unanalyzed emails."""
        try:
            # Test API connection first
            try:
                test_response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=10,
                    temperature=0.05,
                    messages=[{"role": "user", "content": "test"}]
                )
            except Exception as e:
                logger.error("api_connection_error", error=str(e))
                raise Exception(f"Failed to connect to Claude API. Please check your API key and network connection. Error: {str(e)}")

            with get_email_session() as email_session, get_analysis_session() as analysis_session:
                # Get unanalyzed emails
                unanalyzed = email_session.execute(text("""
                    SELECT e.id, e.subject, e.body, e.sender, e.date, 
                           e.labels, e.raw_data, e.thread_id
                    FROM emails e
                    WHERE NOT EXISTS (
                        SELECT 1 FROM email_analysis a 
                        WHERE a.email_id = e.id AND a.thread_id = e.thread_id
                    )
                    LIMIT :batch_size
                """), {"batch_size": batch_size}).mappings().all()
                
                logger.info("processing_batch", count=len(unanalyzed))
                
                # Process each email
                for i, email_data in enumerate(unanalyzed):
                    # Rate limit: process 5 emails then wait to avoid hitting API limits
                    if i > 0 and i % 5 == 0:
                        logger.info("rate_limit_pause", processed=i)
                        time.sleep(60)  # Wait 60 seconds to respect rate limit
                        
                    try:
                        email_data = dict(email_data)
                        
                        # Format email for analysis
                        truncated_body = email_data['body'][:5000] if email_data['body'] else ""  
                        email_type = "internal" if "@company.com" in email_data['sender'] else "external"
                        
                        email_request = EmailRequest(
                            id=email_data['id'],
                            subject=email_data['subject'] or '',
                            body=email_data['body'] or '',
                            sender=email_data['sender'] or '',
                            date=email_data['date'] or '',
                            labels=email_data['labels'] or '[]',
                            raw_data=email_data['raw_data'] or '',
                            email_type=email_type,
                            truncated_body=truncated_body
                        )
                        
                        # Call Claude API for analysis with retry
                        max_retries = 3
                        retry_delay = 5  # seconds
                        
                        for retry in range(max_retries):
                            try:
                                prompt = self.ANALYSIS_PROMPT.format(
                                    text=email_request.truncated_body
                                )
                                
                                response = self.client.messages.create(
                                    model="claude-3-haiku-20240307",
                                    max_tokens=1000,
                                    temperature=0.05,
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
                            email_analysis = EmailAnalysis.from_response(
                                email_id=email_data['id'],
                                thread_id=email_data.get('thread_id', email_data['id']),  # Fallback to email_id if thread_id not present
                                response=analysis_response
                            )
                            
                            # Save analysis with thread_id
                            self.save_analysis(
                                email_id=email_data['id'],
                                thread_id=email_data.get('thread_id', email_data['id']),  # Fallback to email_id if thread_id not present
                                analysis=email_analysis,
                                raw_json=analysis_json
                            )
                        except json.JSONDecodeError as e:
                            log_api_error('json_decode', str(e), analysis_json)
                            continue
                        except Exception as e:
                            log_api_error('validation', str(e), analysis_json)
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
    raw_data: str
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
    parser = argparse.ArgumentParser(description='Email analyzer with configurable batch size')
    parser.add_argument('--batch_size', type=int, default=500,
                      help='Number of emails to process in each batch (default: 500)')
    args = parser.parse_args()

    try:
        analyzer = EmailAnalyzer()
        analyzer.process_emails(batch_size=args.batch_size)
    except Exception as e:
        logger.error("main_error", error=str(e))
        raise

if __name__ == "__main__":
    main()
