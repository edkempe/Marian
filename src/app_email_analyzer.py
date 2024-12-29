#!/usr/bin/env python3
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
import logging
import json
import time
import argparse
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session
from models.email import Email
from models.email_analysis import EmailAnalysis
from shared_lib.database_session_util import get_email_session, get_analysis_session
import sqlalchemy.exc
from structlog import get_logger
from shared_lib.anthropic_client_lib import get_anthropic_client, test_anthropic_connection
from shared_lib.anthropic_lib import parse_claude_response, clean_json_text, extract_json
from shared_lib.gmail_lib import GmailAPI
from shared_lib.security_util import validate_api_key, sanitize_email_content
from shared_lib.chat_log_util import ChatLogger
from shared_lib.constants import API_CONFIG, EMAIL_CONFIG, ERROR_MESSAGES, DEFAULT_MODEL, DATABASE_CONFIG
import re

# Set up structured logging
logger = get_logger()
chat_logger = ChatLogger('logs/api_interactions.jsonl')

def start_metrics_server(port: int) -> None:
    """Start Prometheus metrics server."""
    try:
        # Removed Prometheus metrics server code
        pass
    except Exception as e:
        logger.error("metrics_server_error", error=str(e))

class EmailAnalysisResponse:
    """Response from the email analysis API."""
    
    def __init__(self, summary: str, category: List[str], priority_score: int,
                 priority_reason: str, action_needed: bool, action_type: List[str],
                 action_deadline: Optional[str], key_points: List[str],
                 people_mentioned: List[str], project: str, topic: str,
                 sentiment: str, confidence_score: float = 0.8):
        self.summary = summary
        self.category = category
        self.priority_score = priority_score
        self.priority_reason = priority_reason
        self.action_needed = action_needed
        self.action_type = action_type
        self.action_deadline = action_deadline
        self.key_points = key_points
        self.people_mentioned = people_mentioned
        self.project = project
        self.topic = topic
        self.sentiment = sentiment
        self.confidence_score = confidence_score

class EmailAnalyzer:
    """Analyzes emails using Claude-3-Haiku with improved error handling and validation."""
    
    def __init__(self, test_mode: bool = False):
        """Initialize the analyzer with API client."""
        load_dotenv(verbose=True)
        
        # Initialize API clients
        self.client = get_anthropic_client()
        self.gmail = GmailAPI()
        self.test_mode = test_mode
        
        # Test API connection
        if not test_anthropic_connection(self.client):
            raise RuntimeError("Failed to connect to Anthropic API")
            
        logger.info("analyzer_initialized", test_mode=test_mode)
    
    def analyze_email(self, email_data: Dict[str, Any]) -> Optional[EmailAnalysisResponse]:
        """Analyze a single email using Anthropic API."""
        try:
            # Sanitize email content
            email_data['content'] = sanitize_email_content(email_data['content'])
            
            # Log API request
            chat_logger.log_interaction(
                role="user",
                content=f"Analyzing email: {email_data['id']}",
                metadata={"email_id": email_data['id']}
            )
            
            # Prepare system prompt
            system_prompt = """You are an expert email analyzer. Your task is to analyze the email and extract key information.
            Provide your analysis in JSON format with these fields:
            - summary: Brief summary of the email
            - category: List of categories (e.g., ["work", "meeting"])
            - priority_score: 1-5 (5 being highest)
            - priority_reason: Why this priority was assigned
            - action_needed: boolean
            - action_type: List of required actions
            - action_deadline: Optional deadline (ISO format)
            - key_points: List of key points
            - people_mentioned: List of people mentioned
            - project: Project name or "none"
            - topic: Main topic
            - sentiment: One of ["positive", "neutral", "negative"]
            - confidence_score: 0.0-1.0
            """
            
            # Call Claude API
            response = self.client.messages.create(
                model=API_CONFIG['MODEL'],
                max_tokens=API_CONFIG['MAX_TOKENS'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Subject: {email_data['subject']}\n\nContent: {email_data['content']}"}
                ]
            )
            
            # Log API response
            chat_logger.log_interaction(
                role="assistant",
                content=response.content[0].text,
                metadata={"email_id": email_data['id']}
            )
            
            # Parse response
            analysis_data = parse_claude_response(response.content[0].text)
            if not analysis_data:
                raise ValueError("Failed to parse API response")
            
            return EmailAnalysisResponse(**analysis_data)
            
        except Exception as e:
            logger.error("email_analysis_error",
                        email_id=email_data['id'],
                        error=str(e))
            return None
    
    def _extract_urls(self, text: str) -> Tuple[List[str], List[str]]:
        """Extract URLs from text and create display versions."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        display_urls = []
        for url in urls:
            if len(url) > 50:
                display_urls.append(f"{url[:25]}...{url[-22:]}")
            else:
                display_urls.append(url)
                
        return urls, display_urls
    
    def save_analysis(self, email_id: str, threadId: str, analysis: EmailAnalysisResponse, raw_json: str) -> None:
        """Save the analysis to the database."""
        try:
            with get_analysis_session() as session:
                email_analysis = EmailAnalysis(
                    email_id=email_id,
                    thread_id=threadId,
                    summary=analysis.summary,
                    category=",".join(analysis.category),
                    priority_score=analysis.priority_score,
                    priority_reason=analysis.priority_reason,
                    action_needed=analysis.action_needed,
                    action_type=",".join(analysis.action_type),
                    action_deadline=analysis.action_deadline,
                    key_points=",".join(analysis.key_points),
                    people_mentioned=",".join(analysis.people_mentioned),
                    project=analysis.project,
                    topic=analysis.topic,
                    sentiment=analysis.sentiment,
                    confidence_score=analysis.confidence_score,
                    raw_json=raw_json,
                    created_at=datetime.now(timezone.utc)
                )
                session.add(email_analysis)
                session.commit()
                
        except Exception as e:
            logger.error("save_analysis_error",
                        email_id=email_id,
                        error=str(e))
            raise
    
    def process_unanalyzed_emails(self) -> None:
        """Process all unanalyzed emails from the email store."""
        try:
            with get_email_session() as session:
                # Get unanalyzed email count
                result = session.execute(text("""
                    SELECT COUNT(*) FROM emails e
                    LEFT JOIN email_analysis ea ON e.id = ea.email_id
                    WHERE ea.email_id IS NULL
                """))
                count = result.scalar()
                
                if count == 0:
                    logger.info("no_unanalyzed_emails")
                    return
                
                logger.info("unanalyzed_emails_found", count=count)
                
                # Process in batches
                while count > 0:
                    self.process_emails(EMAIL_CONFIG['BATCH_SIZE'])
                    count -= EMAIL_CONFIG['BATCH_SIZE']
                    
        except Exception as e:
            logger.error("process_unanalyzed_error", error=str(e))
            raise
    
    def process_emails(self, count: int = EMAIL_CONFIG['BATCH_SIZE']) -> None:
        """Process a batch of unanalyzed emails."""
        try:
            with get_email_session() as session:
                # Get batch of unanalyzed emails
                result = session.execute(text("""
                    SELECT e.* FROM emails e
                    LEFT JOIN email_analysis ea ON e.id = ea.email_id
                    WHERE ea.email_id IS NULL
                    LIMIT :count
                """), {"count": count})
                
                emails = result.fetchall()
                
                for email in emails:
                    email_dict = {
                        'id': email.id,
                        'threadId': email.thread_id,
                        'subject': email.subject,
                        'content': email.content,
                        'date': email.received_date.isoformat(),
                        'labels': email.labels.split(',') if email.labels else []
                    }
                    
                    analysis = self.analyze_email(email_dict)
                    if analysis:
                        self.save_analysis(
                            email.id,
                            email.thread_id,
                            analysis,
                            json.dumps(email_dict)
                        )
                    
                    # Sleep to respect rate limits
                    time.sleep(API_CONFIG['RATE_LIMIT_DELAY'])
                    
        except Exception as e:
            logger.error("process_emails_error", error=str(e))
            raise

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Process and analyze emails using Claude API')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    args = parser.parse_args()
    
    try:
        analyzer = EmailAnalyzer(test_mode=args.test)
        analyzer.process_unanalyzed_emails()
    except Exception as e:
        logger.error("main_error", error=str(e))
        raise

if __name__ == "__main__":
    main()
