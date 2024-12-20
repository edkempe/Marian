#!/usr/bin/env python3
import os
from datetime import datetime
from typing import Optional, Dict, Any
import anthropic
from dotenv import load_dotenv
from contextlib import contextmanager
import time

from models.email_analysis import EmailAnalysisResponse, EmailAnalysis
from database.config import get_email_session, get_analysis_session
from utils.logging import (
    logger, EMAIL_ANALYSIS_COUNTER, EMAIL_ANALYSIS_DURATION,
    log_api_error, log_validation_error, start_metrics_server
)

class EmailAnalyzer:
    """Analyzes emails using Claude-3-Haiku with improved error handling and validation."""

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
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # Start metrics server
        start_metrics_server(metrics_port)
        logger.info("analyzer_initialized", metrics_port=metrics_port)

    def analyze_email(self, email_data: Dict[str, Any]) -> Optional[EmailAnalysis]:
        """Analyze a single email and return structured analysis."""
        start_time = time.time()
        
        try:
            # Format prompt
            prompt_data = {
                'subject': email_data.get('subject', 'No Subject'),
                'sender': email_data.get('sender', 'Unknown'),
                'email_type': email_data.get('type', 'Unknown'),
                'labels': email_data.get('labels', []),
                'thread_id': email_data.get('thread_id', ''),
                'date': email_data.get('date', 'Unknown'),
                'has_attachments': email_data.get('has_attachments', False),
                'truncated_body': email_data.get('content', '')[:2000]
            }
            
            formatted_prompt = self.ANALYSIS_PROMPT.format(**prompt_data)

            # Make API call
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": formatted_prompt}
                ]
            )

            # Extract and parse response
            text = response.content[0].text if isinstance(response.content, list) else response.content
            
            # Validate response using Pydantic
            try:
                analysis_response = EmailAnalysisResponse.parse_raw(text)
            except Exception as e:
                log_validation_error("response_parsing", {"error": str(e), "response": text})
                return None

            # Create database model
            analysis = EmailAnalysis.from_response(email_data['id'], analysis_response)
            
            # Store in database
            with get_analysis_session() as session:
                session.merge(analysis)
            
            # Record metrics
            duration = time.time() - start_time
            EMAIL_ANALYSIS_COUNTER.labels(status="success").inc()
            EMAIL_ANALYSIS_DURATION.observe(duration)
            
            logger.info(
                "email_analyzed",
                email_id=email_data['id'],
                duration=duration,
                sentiment=analysis_response.sentiment,
                priority=analysis_response.priority.score
            )
            
            return analysis

        except Exception as e:
            duration = time.time() - start_time
            EMAIL_ANALYSIS_COUNTER.labels(status="failure").inc()
            EMAIL_ANALYSIS_DURATION.observe(duration)
            
            log_api_error(
                error_type=type(e).__name__,
                details={
                    "error": str(e),
                    "email_id": email_data.get('id', 'unknown'),
                    "duration": duration
                }
            )
            return None

    def process_emails(self, batch_size: int = 10) -> None:
        """Process a batch of unanalyzed emails."""
        with get_email_session() as email_session:
            # Get unanalyzed emails
            unanalyzed = email_session.execute("""
                SELECT e.* FROM emails e
                LEFT JOIN analysis.email_analysis a ON e.id = a.email_id
                WHERE a.email_id IS NULL
                LIMIT :limit
            """, {"limit": batch_size}).fetchall()
            
            logger.info("processing_batch", count=len(unanalyzed))
            
            for email in unanalyzed:
                email_dict = dict(email)
                self.analyze_email(email_dict)

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
