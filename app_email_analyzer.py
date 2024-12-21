#!/usr/bin/env python3
import os
from datetime import datetime
from typing import Optional, Dict, Any
import anthropic
from dotenv import load_dotenv
from contextlib import contextmanager
import time
import json
from sqlalchemy import text

from model_email_analysis import EmailAnalysisResponse, EmailAnalysis
from database.config import get_email_session, get_analysis_session
from util_logging import (
    logger, EMAIL_ANALYSIS_COUNTER, EMAIL_ANALYSIS_DURATION,
    log_validation_error, start_metrics_server
)

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

    def process_emails(self, batch_size: int = 50) -> None:
        """Process a batch of unanalyzed emails."""
        try:
            # Get database sessions
            with get_email_session() as email_session, get_analysis_session() as analysis_session:
                # Get unanalyzed emails
                unanalyzed = email_session.execute(text("""
                    SELECT e.id, e.subject, e.body, e.sender, e.received_date, 
                           e.labels, e.thread_id, e.has_attachments 
                    FROM emails e
                    LEFT JOIN email_analysis a ON e.id = a.email_id
                    WHERE a.email_id IS NULL
                    LIMIT :batch_size
                """), {"batch_size": batch_size}).mappings().all()
                
                logger.info("processing_batch", count=len(unanalyzed))
                
                # Process each email
                for email in unanalyzed:
                    email_data = dict(email)
                    
                    # Format email for analysis
                    truncated_body = email_data['body'][:10000] if email_data['body'] else ""
                    email_type = "internal" if "@company.com" in email_data['sender'] else "external"
                    
                    # Call Claude API for analysis
                    prompt = self.ANALYSIS_PROMPT.format(
                        subject=email_data['subject'],
                        sender=email_data['sender'],
                        email_type=email_type,
                        labels=email_data['labels'],
                        thread_id=email_data['thread_id'],
                        date=email_data['received_date'],
                        has_attachments=email_data['has_attachments'],
                        truncated_body=truncated_body
                    )
                    
                    # Get analysis from Claude
                    response = self.client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=1000,
                        temperature=0.0,
                        messages=[{
                            "role": "user",
                            "content": prompt
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
                        analysis = EmailAnalysis.from_response(email_data['id'], analysis_response)
                        
                        # Save to database
                        analysis_session.add(analysis)
                        analysis_session.commit()
                        
                    except json.JSONDecodeError as e:
                        log_api_error('json_decode', str(e), analysis_json)
                    except Exception as e:
                        log_api_error('validation', str(e), analysis_json)
                        
        except Exception as e:
            logger.error("process_emails_error", error=str(e))
            raise

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
        analyzer.process_emails(batch_size=50)
    except Exception as e:
        logger.error("main_error", error=str(e))
        raise

if __name__ == "__main__":
    main()
