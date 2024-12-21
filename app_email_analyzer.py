#!/usr/bin/env python3
import os
from datetime import datetime
from typing import Optional, Dict, Any
import anthropic
from dotenv import load_dotenv
from contextlib import contextmanager
import time
import json
import ssl
import certifi
from sqlalchemy import text

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
    ANALYSIS_PROMPT = """You are an email analysis assistant. Your task is to analyze the email below and extract key information.
You MUST respond with ONLY a single-line JSON object containing the analysis - no other text, no newlines, no formatting.

Email to analyze:
Subject: {subject}
From: {sender}
Type: {email_type}
Labels: {labels}
Thread ID: {thread_id}
Date: {date}
Has Attachments: {has_attachments}

Content:
{truncated_body}

Required JSON response format (single line, no newlines, no formatting):
{{"summary": "brief summary", "category": ["category1"], "priority": {{"score": 1-5, "reason": "reason"}}, "action": {{"needed": true/false, "type": ["action1"], "deadline": "YYYY-MM-DD"}}, "key_points": ["point1"], "people_mentioned": ["person1"], "links_found": ["url1"], "context": {{"project": "project name", "topic": "topic", "ref_docs": "references"}}, "sentiment": "positive/negative/neutral", "confidence_score": 0.9}}

Important:
1. Respond with ONLY the JSON object on a single line - no other text, no newlines, no formatting
2. For any URLs in links_found, truncate them to maximum 100 characters and add ... at the end if longer
3. Make sure all JSON fields are present
4. Use empty arrays [] for missing lists
5. Use empty strings "" for missing text fields"""

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
            # Format the email content for analysis
            email_content = f"Subject: {email_data.get('subject', '')}\n\nBody: {email_data.get('body', '')}"
            
            # Get analysis from Claude
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.0,
                messages=[{
                    "role": "user",
                    "content": self.ANALYSIS_PROMPT + "\n\nEmail:\n" + email_content
                }]
            )

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
                
                analysis_response = EmailAnalysisResponse.model_validate(analysis)
                
                # Create and return EmailAnalysis instance
                return EmailAnalysis.from_response(email_data['id'], analysis_response)
                
            except json.JSONDecodeError as e:
                log_api_error('json_decode', str(e), analysis_json)
                return None
            except Exception as e:
                log_api_error('validation', str(e), analysis_json)
                return None

        except Exception as e:
            log_api_error('api_call', str(e))
            return None

    def save_analysis(self, email_id: str, thread_id: str, analysis: EmailAnalysis) -> None:
        """Save email analysis to database."""
        try:
            with get_analysis_session() as session:
                # Try to update existing record first
                result = session.execute(
                    text("""
                    UPDATE email_analysis 
                    SET analysis_date = :analysis_date,
                        thread_id = :thread_id,
                        prompt_version = :prompt_version,
                        summary = :summary,
                        category = :category,
                        priority_score = :priority_score,
                        priority_reason = :priority_reason,
                        action_needed = :action_needed,
                        action_type = :action_type,
                        action_deadline = :action_deadline,
                        key_points = :key_points,
                        people_mentioned = :people_mentioned,
                        links_found = :links_found,
                        links_display = :links_display,
                        project = :project,
                        topic = :topic,
                        sentiment = :sentiment,
                        confidence_score = :confidence_score,
                        raw_analysis = :raw_analysis
                    WHERE email_id = :email_id
                    """),
                    {
                        "email_id": email_id,
                        "thread_id": thread_id,
                        "analysis_date": datetime.utcnow(),
                        "prompt_version": "1.0",  # TODO: Make this configurable
                        "summary": analysis.summary,
                        "category": json.dumps(analysis.category),
                        "priority_score": analysis.priority.score,
                        "priority_reason": analysis.priority.reason,
                        "action_needed": analysis.action.needed,
                        "action_type": json.dumps(analysis.action.type),
                        "action_deadline": analysis.action.deadline,
                        "key_points": json.dumps(analysis.key_points),
                        "people_mentioned": json.dumps(analysis.people_mentioned),
                        "links_found": json.dumps(analysis.links_found),
                        "links_display": json.dumps(analysis.links_display),
                        "project": json.dumps([analysis.context.project] if analysis.context.project else []),
                        "topic": json.dumps([analysis.context.topic] if analysis.context.topic else []),
                        "sentiment": analysis.sentiment,
                        "confidence_score": analysis.confidence_score,
                        "raw_analysis": analysis.raw_json
                    }
                )
                
                # If no rows were updated, insert a new record
                if result.rowcount == 0:
                    session.execute(
                        text("""
                        INSERT INTO email_analysis (
                            email_id, thread_id, analysis_date, prompt_version,
                            summary, category, priority_score, priority_reason,
                            action_needed, action_type, action_deadline,
                            key_points, people_mentioned, links_found, links_display,
                            project, topic, sentiment, confidence_score,
                            raw_analysis
                        ) VALUES (
                            :email_id, :thread_id, :analysis_date, :prompt_version,
                            :summary, :category, :priority_score, :priority_reason,
                            :action_needed, :action_type, :action_deadline,
                            :key_points, :people_mentioned, :links_found, :links_display,
                            :project, :topic, :sentiment, :confidence_score,
                            :raw_analysis
                        )
                        """),
                        {
                            "email_id": email_id,
                            "thread_id": thread_id,
                            "analysis_date": datetime.utcnow(),
                            "prompt_version": "1.0",  # TODO: Make this configurable
                            "summary": analysis.summary,
                            "category": json.dumps(analysis.category),
                            "priority_score": analysis.priority.score,
                            "priority_reason": analysis.priority.reason,
                            "action_needed": analysis.action.needed,
                            "action_type": json.dumps(analysis.action.type),
                            "action_deadline": analysis.action.deadline,
                            "key_points": json.dumps(analysis.key_points),
                            "people_mentioned": json.dumps(analysis.people_mentioned),
                            "links_found": json.dumps(analysis.links_found),
                            "links_display": json.dumps(analysis.links_display),
                            "project": json.dumps([analysis.context.project] if analysis.context.project else []),
                            "topic": json.dumps([analysis.context.topic] if analysis.context.topic else []),
                            "sentiment": analysis.sentiment,
                            "confidence_score": analysis.confidence_score,
                            "raw_analysis": analysis.raw_json
                        }
                    )
                session.commit()
        except Exception as e:
            logger.error("database_error", error=str(e), email_id=email_id)

    def process_emails(self, batch_size: int = 50) -> None:
        """Process a batch of unanalyzed emails."""
        try:
            # Test API connection first
            try:
                test_response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=10,
                    temperature=0.0,
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
                                    subject=email_request.subject,
                                    sender=email_request.sender,
                                    email_type=email_request.email_type,
                                    labels=email_request.labels,
                                    thread_id=email_request.id,
                                    date=email_request.date,
                                    has_attachments="false",
                                    truncated_body=email_request.truncated_body
                                )
                                
                                response = self.client.messages.create(
                                    model="claude-3-haiku-20240307",
                                    max_tokens=1000,
                                    temperature=0.0,
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
                                analysis=email_analysis
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
    try:
        analyzer = EmailAnalyzer()
        analyzer.process_emails(batch_size=10)
    except Exception as e:
        logger.error("main_error", error=str(e))
        raise

if __name__ == "__main__":
    main()
