#!/usr/bin/env python3
import os
from datetime import datetime
from typing import Optional, Dict, Any
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from dotenv import load_dotenv
from contextlib import contextmanager
import time
import json
from sqlalchemy import text

from models.email import Email
from models.email_analysis import EmailAnalysis, EmailAnalysisResponse
from database.config import get_email_session, get_analysis_session
from utils.logging_config import setup_logging, log_error, log_api_response, log_db_operation
from config.constants import API_CONFIG, EMAIL_CONFIG

logger = setup_logging(__name__)

class EmailAnalyzer:
    """Analyzes emails using Claude-3-Haiku with improved error handling and validation.
    
    This analyzer uses the Claude-3-Haiku model exclusively for consistent performance and cost efficiency.
    Do not change to other models without thorough testing and approval.
    
    Known Issues:
    1. Claude API Response Formatting:
       - The API may prefix responses with text like "Here is the JSON response:"
       - This causes json.loads() to fail with "Expecting value: line 1 column 2 (char 1)"
       - Solution: Use _extract_json() to clean the response
    
    Model Requirements:
    - Always use claude-3-haiku-20240307
    - Keep max_tokens_to_sample at 1000 for consistent response sizes
    - Use temperature=0 for deterministic outputs
    """

    def __init__(self, api_key: str):
        """Initialize the analyzer with API client and start metrics server."""
        load_dotenv(verbose=True)
        
        # Verify environment
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY not found in environment")
            
        # Initialize API client
        self.client = Anthropic(api_key=api_key)
        self.model = API_CONFIG['ANTHROPIC_MODEL']  # Explicitly store model name
        
        # Start metrics server
        logger.info({'event': 'analyzer_initialized', 'metrics_port': EMAIL_CONFIG['METRICS_PORT']})

    def analyze_email(self, email_data: Dict[str, Any]) -> Optional[EmailAnalysis]:
        """Analyze a single email and return structured analysis."""
        try:
            # Format the email content for analysis
            email_content = f"Subject: {email_data.get('subject', '')}\n\nBody: {email_data.get('body', '')}"
            
            # Get analysis from Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,  # Increased to ensure we get complete responses
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": f"Analyze this email and respond with ONLY a JSON object. Do not include any other text, not even a single space before or after the JSON. Your response must be a complete, valid JSON object:\n" +
                    email_content + 
                    "\n\nRequired JSON format:\n" +
                    '{"summary": "brief summary", "category": ["category1"], "priority": {"score": 1, "reason": "reason"}, "action": {"needed": false, "type": [], "deadline": ""}, "key_points": ["point1"], "people_mentioned": ["person1"], "links_found": ["url1"], "links_display": ["url1"], "context": {"project": "", "topic": "", "ref_docs": ""}, "sentiment": "positive", "confidence_score": 0.9}' +
                    "\n\nRules:\n" +
                    "1. Start your response with { and end with } - no other characters before or after\n" +
                    "2. For any URLs in links_found, truncate them to maximum 100 characters and add ... at the end if longer\n" +
                    "3. Make sure all JSON fields are present\n" +
                    "4. Use empty arrays [] for missing lists\n" +
                    "5. Use empty string \"\" for missing context fields\n" +
                    "6. Use empty string \"\" for missing deadline\n" +
                    "7. Use empty arrays [] for missing action.type\n" +
                    "8. Priority score must be 1-5\n" +
                    "9. Sentiment must be exactly 'positive', 'negative', or 'neutral'\n" +
                    "10. Confidence score must be between 0.0 and 1.0\n" +
                    "11. YOUR RESPONSE MUST BE A COMPLETE, VALID JSON OBJECT\n" +
                    "12. Do not use null values - use empty string \"\" or empty array [] instead"
                }]
            )

            # Extract and validate the analysis
            try:
                # Clean the response by extracting just the JSON object
                response_text = response.content[0].text  # Get text from TextBlock
                analysis_json = self._extract_json(response_text)
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
                log_error(logger, 'json_decode_error', e, response=response_text)
                return None
            except Exception as e:
                log_error(logger, 'validation_error', e, response=response_text)
                return None

        except Exception as e:
            log_error(logger, 'api_call_error', e)
            return None

    def _extract_json(self, text: str) -> str:
        """Extract JSON object from text, removing any leading or trailing non-JSON content.
        
        Args:
            text: Text containing a JSON object, possibly with extra content
            
        Returns:
            Cleaned JSON string
            
        Example:
            Input: "Here is the JSON: {...} Hope this helps!"
            Output: "{...}"
        """
        if '{' not in text or '}' not in text:
            return text
            
        start = text.index('{')
        end = text.rindex('}') + 1
        return text[start:end]

    def process_emails(self, batch_size: Optional[int] = None) -> None:
        """Process a batch of unanalyzed emails."""
        if batch_size is None:
            batch_size = EMAIL_CONFIG['BATCH_SIZE']
            
        try:
            # Get database sessions
            with get_email_session() as email_session, get_analysis_session() as analysis_session:
                # Get unanalyzed emails
                unanalyzed = email_session.execute(text("""
                    SELECT e.id, e.subject, e.body, e.sender, e.date, 
                           e.labels
                    FROM emails e
                    LEFT JOIN email_analysis a ON e.id = a.email_id
                    WHERE a.email_id IS NULL
                    LIMIT :batch_size
                """), {"batch_size": batch_size}).mappings().all()
                
                logger.info({'event': 'processing_batch', 'count': len(unanalyzed)})
                
                # Process each email
                for email in unanalyzed:
                    try:
                        # Prepare email data for analysis
                        email_data = dict(email)
                        
                        # Extract email type from labels
                        email_type = self._determine_email_type(email_data['labels'])
                        
                        # Truncate body if needed
                        truncated_body = self._truncate_text(email_data['body'])
                        
                        # Create analysis prompt
                        prompt = self._create_analysis_prompt(
                            subject=email_data['subject'],
                            body=truncated_body,
                            sender=email_data['sender'],
                            email_type=email_type,
                            labels=email_data['labels'],
                            date=email_data['date']
                        )
                        
                        # Get analysis from Claude
                        response = self.client.messages.create(
                            model=self.model,
                            max_tokens=API_CONFIG['MAX_TOKENS'],
                            temperature=API_CONFIG['TEMPERATURE'],
                            messages=[{
                                "role": "user",
                                "content": prompt
                            }]
                        )

                        # Extract and validate the analysis
                        try:
                            # Get response content
                            response_content = response.content[0].text if isinstance(response.content, list) else response.content
                            
                            try:
                                # Parse response as JSON
                                analysis = json.loads(response_content)
                                
                                # Log API response
                                log_api_response(logger, 'claude_analysis', analysis, email_id=email.id)
                                
                                # Add links_display if missing
                                if 'links_found' in analysis and 'links_display' not in analysis:
                                    analysis['links_display'] = [
                                        url[:100] + '...' if len(url) > 100 else url
                                        for url in analysis['links_found']
                                    ]
                                
                                # Create EmailAnalysis object
                                email_analysis = EmailAnalysis.from_response(email.id, EmailAnalysisResponse(**analysis))
                                
                                # Check if email has already been analyzed
                                existing = analysis_session.query(EmailAnalysis).filter_by(email_id=email.id).first()
                                if existing:
                                    # Update existing analysis
                                    for key, value in email_analysis.__dict__.items():
                                        if not key.startswith('_'):
                                            setattr(existing, key, value)
                                    log_db_operation(logger, 'update_analysis', 'update', 'email_analysis', 
                                                  email_id=email.id)
                                else:
                                    # Add new analysis
                                    analysis_session.add(email_analysis)
                                    log_db_operation(logger, 'new_analysis', 'insert', 'email_analysis',
                                                  email_id=email.id)
                                
                                # Mark email as analyzed
                                email.analyzed = True
                                email_session.add(email)
                                log_db_operation(logger, 'mark_analyzed', 'update', 'emails',
                                              email_id=email.id)
                                
                            except json.JSONDecodeError as e:
                                log_error(logger, 'json_decode_error', e, 
                                        email_id=email.id, response=response_content)
                                continue
                            except Exception as e:
                                log_error(logger, 'validation_error', e,
                                        email_id=email.id, response=response_content)
                                continue
                        except Exception as e:
                            log_error(logger, 'process_email_error', e, email_id=email.id)
                            continue

        except Exception as e:
            log_error(logger, 'process_batch_error', e)
            raise

    def _determine_email_type(self, labels: str) -> str:
        # TO DO: implement email type determination logic
        return "unknown"

    def _truncate_text(self, text: str) -> str:
        # TO DO: implement text truncation logic
        return text

    def _create_analysis_prompt(self, subject: str, body: str, sender: str, email_type: str, labels: str, date: str) -> str:
        return (
            f"{HUMAN_PROMPT} Analyze this email and respond with ONLY a JSON object. Do not include any other text, not even a single space before or after the JSON:\n" +
            f"Subject: {subject}\n" +
            f"From: {sender}\n" +
            f"Type: {email_type}\n" +
            f"Labels: {labels}\n" +
            f"Date: {date}\n\n" +
            f"Content:\n{body}\n\n" +
            "Required JSON format:\n" +
            '{"summary": "brief summary", "category": ["category1"], "priority": {"score": 1-5, "reason": "reason"}, "action": {"needed": true/false, "type": ["action1"], "deadline": "YYYY-MM-DD"}, "key_points": ["point1"], "people_mentioned": ["person1"], "links_found": ["url1"], "context": {"project": "project name", "topic": "topic", "ref_docs": "references"}, "sentiment": "positive/negative/neutral", "confidence_score": 0.9}' +
            "\n\nRules:\n" +
            "1. Start your response with { and end with } - no other characters before or after\n" +
            "2. For any URLs in links_found, truncate them to maximum 100 characters and add ... at the end if longer\n" +
            "3. Make sure all JSON fields are present\n" +
            "4. Use empty arrays [] for missing lists\n" +
            "5. Use empty strings \"\" for missing text fields"
            f"{AI_PROMPT}"
        )

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
        analyzer = EmailAnalyzer(api_key=os.getenv('ANTHROPIC_API_KEY'))
        analyzer.process_emails(batch_size=5)  # Reduced from 50 to 5
    except Exception as e:
        logger.error("main_error", error=str(e))
        raise

if __name__ == "__main__":
    main()
