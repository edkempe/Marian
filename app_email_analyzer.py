#!/usr/bin/env python3
import os
import json
import time
import argparse
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import anthropic
from dotenv import load_dotenv
from sqlalchemy import text
from models.email_analysis import EmailAnalysisModel, EmailAnalysis
from models.email import Email
from database.config import get_email_session, get_analysis_session, init_db
from util_logging import logger
from dataclasses import dataclass

# Load environment variables from .env file
load_dotenv()

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
    email_type: str = ""
    truncated_body: str = ""

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
    TRIAGE_PROMPT = """Quickly assess if this email requires detailed analysis. Consider:
1. Is it a marketing/promotional email? (newsletters, ads, etc.)
2. Is it an automated notification? (system alerts, social media updates, etc.)
3. Does it require any action from the recipient?
4. Is it time-sensitive?
5. Does it contain important business/personal information?

Respond with a JSON object:
{
    "needs_analysis": true/false,
    "reason": "Brief explanation",
    "estimated_priority": 1-5
}

Email to analyze:
{text}

JSON response:"""

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
8. List of URLs found in the email (both full and display versions)
9. Context:
   - project: project name if mentioned
   - topic: general topic/subject matter
10. Overall sentiment (positive/negative/neutral)
11. Confidence score (0.0-1.0) for the analysis

Format the response as a JSON object with these exact field names:
{{"summary": "brief summary", "category": ["category1"], "priority_score": 1-5, "priority_reason": "reason", "action_needed": true/false, "action_type": ["action1"], "action_deadline": "YYYY-MM-DD", "key_points": ["point1"], "people_mentioned": ["person1"], "links_found": ["url1"], "links_display": ["display_url1"], "project": "project name", "topic": "topic", "sentiment": "positive/negative/neutral", "confidence_score": 0.9}}

Email to analyze:
{text}

JSON response:"""

    def __init__(self, api_key: Optional[str] = None, email_db: Optional[str] = None, analysis_db: Optional[str] = None):
        """Initialize the analyzer with optional API key and database paths."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = anthropic.Client(api_key=self.api_key)
        self.email_db = email_db
        self.analysis_db = analysis_db

    def analyze_email(self, email: EmailRequest) -> EmailAnalysis:
        """Analyze a single email using Claude API and store the result."""
        try:
            start_time = time.time()
            
            # Get API response
            response_text = self._get_api_response(email)
            
            # Clean and parse JSON response
            try:
                # Remove any text before the actual JSON
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start == -1 or json_end == 0:
                    raise ValueError("No JSON object found in response")
                
                json_str = response_text[json_start:json_end]
                analysis_dict = json.loads(json_str)
                
                # Validate and create model
                try:
                    analysis_data = EmailAnalysisModel.model_validate(analysis_dict)
                except Exception as e:
                    logger.error(
                        "validation_error",
                        error_type="validation_error",
                        error=str(e),
                        response=json_str if json_str else "N/A"
                    )
                    raise
                
                # Create and store analysis
                analysis = EmailAnalysis.from_response(
                    email_id=email.id,
                    thread_id=email.id,  # Using email.id as thread_id for now
                    response=analysis_data
                )
                
                # Store in database
                with get_analysis_session() as session:
                    session.add(analysis)
                    session.commit()
                
                duration = time.time() - start_time
                logger.info("email_analysis_success", email_id=email.id, duration=duration)
                
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(
                    "json_decode_error",
                    error_type="json_decode_error",
                    error=str(e),
                    response=response_text if response_text else "N/A"
                )
                raise
            except Exception as e:
                logger.error(
                    "analysis_error",
                    error_type="analysis_error",
                    error=str(e),
                    response=response_text if response_text else "N/A"
                )
                raise
                
        except Exception as e:
            logger.error("email_analysis_error", error=str(e))
            raise

    def _get_api_response(self, email: EmailRequest):
        """Get API response for the given email."""
        prompt = self.ANALYSIS_PROMPT.format(
            text=email.truncated_body
        )
        
        # Add specific instructions about JSON formatting
        prompt += "\nIMPORTANT: Ensure all JSON strings are properly escaped and terminated. Keep URLs concise."
        
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.05,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        response_text = response.content[0].text
        
        # Clean the response text
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
            
        return response_text.strip()

    def save_analysis(self, email_id: str, thread_id: str, analysis: EmailAnalysisModel, raw_json: str):
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

    def _triage_email(self, email: EmailRequest):
        """Quick triage to determine if email needs detailed analysis."""
        prompt = self.TRIAGE_PROMPT.format(
            text=email.truncated_body[:1000]  # Use shorter content for triage
        )
        
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,  # Smaller token limit for faster response
            temperature=0.05,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        response_text = response.content[0].text.strip()
        
        # More aggressive JSON cleaning
        try:
            # Remove any markdown code block markers
            response_text = response_text.replace('```json', '').replace('```', '')
            
            # Remove any leading/trailing whitespace and newlines
            response_text = response_text.strip()
            
            # Try to find the JSON object if there's additional text
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = response_text[start:end]
            
            triage_result = json.loads(response_text)
            
            # Validate required fields
            required_fields = {"needs_analysis", "reason", "estimated_priority"}
            if not all(field in triage_result for field in required_fields):
                logger.error("triage_missing_fields", 
                           error="Missing required fields in triage response",
                           response=response_text)
                return {"needs_analysis": True, 
                       "reason": "Triage response missing fields", 
                       "estimated_priority": 3}
            
            # Validate field types
            if not isinstance(triage_result["needs_analysis"], bool):
                triage_result["needs_analysis"] = True
            if not isinstance(triage_result["estimated_priority"], int):
                triage_result["estimated_priority"] = 3
            if not isinstance(triage_result["reason"], str):
                triage_result["reason"] = str(triage_result["reason"])
                
            return triage_result
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("triage_json_error", 
                        error=str(e),
                        response=response_text)
            return {"needs_analysis": True, 
                   "reason": "Failed to parse triage response", 
                   "estimated_priority": 3}

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
                    # Rate limit: process 10 emails then wait
                    if i > 0 and i % 10 == 0:
                        logger.info("rate_limit_pause", processed=i)
                        time.sleep(30)  # Reduced wait time since triage is faster
                        
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
                            date=str(email_data['date']) if email_data['date'] else '',
                            labels=email_data['labels'] or '',
                            raw_data=email_data['raw_data'] or '',
                            email_type=email_type,
                            truncated_body=truncated_body
                        )
                        
                        # First do quick triage
                        triage_result = self._triage_email(email_request)
                        
                        if triage_result["needs_analysis"]:
                            # Do full analysis only if needed
                            analysis = self.analyze_email(email_request)
                            logger.info("email_analyzed", 
                                      email_id=email_request.id, 
                                      needs_analysis=True,
                                      reason=triage_result["reason"])
                        else:
                            # Create basic analysis for non-important emails
                            analysis = EmailAnalysis.from_triage(
                                email_id=email_request.id,
                                thread_id=email_data['thread_id'],
                                triage_result=triage_result
                            )
                            with get_analysis_session() as session:
                                session.add(analysis)
                                session.commit()
                            logger.info("email_skipped", 
                                      email_id=email_request.id,
                                      needs_analysis=False,
                                      reason=triage_result["reason"])
                            
                    except Exception as e:
                        logger.error("email_processing_error", 
                                   email_id=email_data.get('id', 'unknown'), 
                                   error=str(e))
                        continue
                        
        except Exception as e:
            logger.error("process_emails_error", error=str(e))
            raise

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
    parser.add_argument('--email_db', type=str, default=None,
                      help='Path to email database (default: None)')
    parser.add_argument('--analysis_db', type=str, default=None,
                      help='Path to analysis database (default: None)')
    args = parser.parse_args()

    try:
        # Initialize database if needed
        from database.config import init_db
        init_db()
        
        analyzer = EmailAnalyzer(email_db=args.email_db, analysis_db=args.analysis_db)
        analyzer.process_emails(batch_size=args.batch_size)
    except Exception as e:
        logger.error("main_error", error=str(e))
        raise

if __name__ == "__main__":
    main()
