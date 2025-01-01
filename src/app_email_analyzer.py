#!/usr/bin/env python3
import json
import logging
import re
import time
import argparse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import anthropic
from anthropic import Anthropic
from dotenv import load_dotenv
from structlog import get_logger

from models.email_analysis import EmailAnalysis
from shared_lib.anthropic_client_lib import get_anthropic_client, test_anthropic_connection
from shared_lib.chat_log_util import ChatLogger
from shared_lib.constants import API_CONFIG, CONFIG
from shared_lib.exceptions import APIError, ValidationError
from shared_lib.file_constants import DEFAULT_CHAT_LOG, LOGS_PATH
from shared_lib.gmail_lib import GmailAPI
from shared_lib.utils import normalize_response, extract_urls, sanitize_email_content
from shared_lib.database_session_util import get_analysis_session, get_email_session
from sqlalchemy import text

# Set up structured logging
logger = get_logger()
chat_logger = ChatLogger(str(LOGS_PATH / DEFAULT_CHAT_LOG))


def start_metrics_server(port: int = 8000) -> None:
    """Start metrics server."""
    pass  # Metrics server removed


class EmailAnalysisResponse:
    """Response from the email analysis API."""

    def __init__(
        self,
        summary: str = "",
        category: Optional[List[str]] = None,
        priority_score: int = 0,
        priority_reason: str = "",
        action_needed: bool = False,
        action_type: Optional[List[str]] = None,
        action_deadline: Optional[str] = None,
        key_points: Optional[List[str]] = None,
        people_mentioned: Optional[List[str]] = None,
        project: str = "",
        topic: str = "",
        sentiment: str = "neutral",
        confidence_score: float = 0.8,
        email_id: Optional[str] = None,
    ):
        self.summary = summary or ""
        self.category = category or []
        self.priority_score = priority_score or 0
        self.priority_reason = priority_reason or ""
        self.action_needed = bool(action_needed)
        self.action_type = action_type or []
        self.action_deadline = action_deadline
        self.key_points = key_points or []
        self.people_mentioned = people_mentioned or []
        self.project = project or ""
        self.topic = topic or ""
        self.sentiment = sentiment or "neutral"
        self.confidence_score = confidence_score or 0.8
        self.email_id = email_id


class EmailAnalyzer:
    """Analyzes emails using Claude-3-Haiku with improved error handling and validation."""

    def __init__(self, test_mode: bool = False):
        """Initialize the analyzer with API client."""
        load_dotenv(verbose=True)

        # Initialize API clients
        self.client = get_anthropic_client()
        self.test_mode = test_mode

        # Only initialize Gmail API in non-test mode
        self.gmail = None if test_mode else GmailAPI()

        # Test API connection
        if not test_anthropic_connection(self.client):
            raise RuntimeError("Failed to connect to Anthropic API")

        logger.info("analyzer_initialized", test_mode=test_mode)

    def analyze_email(self, email_data: Dict[str, str]) -> EmailAnalysisResponse:
        """Analyze an email using the Claude API.

        Args:
            email_data: Dictionary containing email data with 'subject' and 'body' keys

        Returns:
            EmailAnalysisResponse object containing the analysis results

        Raises:
            APIError: If there is an error calling the Claude API
            ValidationError: If the email data is invalid
        """
        try:
            # Input validation
            if not isinstance(email_data, dict):
                raise ValidationError("Email data must be a dictionary")
            
            required_fields = ["subject", "body"]
            for field in required_fields:
                if field not in email_data:
                    raise ValidationError(f"Missing required field: {field}")
                if not isinstance(email_data[field], str):
                    raise ValidationError(f"Field {field} must be a string")

            # Get the model
            model = API_CONFIG["TEST_MODEL"] if self.test_mode else API_CONFIG["MODEL"]

            # Get the model-specific prompt
            prompt = API_CONFIG["EMAIL_ANALYSIS_PROMPT"][model].format(
                email_content=f"Subject: {email_data['subject']}\n\nContent: {email_data['body']}"
            )

            # Call Claude API
            response = self.client.messages.create(
                model=model,
                max_tokens=API_CONFIG["MAX_TOKENS_TEST"] if self.test_mode else API_CONFIG["MAX_TOKENS"],
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=API_CONFIG["TEMPERATURE"]
            )

            # Parse and log the response
            response_content = response.content[0].text
            logging.info(f"API Response: {response_content}")
            
            try:
                response_data = json.loads(response_content)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse API response: {e}")
                raise APIError("Failed to parse API response") from e
                
            # Normalize the response data
            normalized_data = normalize_response(response_data)
            
            # Create and return EmailAnalysisResponse object
            return EmailAnalysisResponse(**normalized_data)

        except anthropic.APIError as e:
            logging.error(f"API error: {e}")
            raise APIError("Error calling Claude API") from e
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def save_analysis(
        self,
        email_id: str,
        threadId: str,
        analysis: EmailAnalysisResponse,
        raw_json: str,
    ) -> None:
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
                    created_at=datetime.now(timezone.utc),
                )
                session.add(email_analysis)
                session.commit()

        except Exception as e:
            logger.error("save_analysis_error", email_id=email_id, error=str(e))
            raise

    def process_unanalyzed_emails(self) -> None:
        """Process all unanalyzed emails from the email store."""
        try:
            with get_email_session() as session:
                # Get count of unanalyzed emails
                result = session.execute(
                    text(
                        """
                    SELECT COUNT(*) as count FROM emails e
                    LEFT JOIN email_analysis ea ON e.id = ea.email_id
                    WHERE ea.email_id IS NULL
                    """
                    )
                ).first()

                count = result[0] if result else 0
                logger.info("unanalyzed_emails_found", count=count)

                # Process in batches
                while count > 0:
                    self.process_emails(CONFIG["EMAIL"]["batch_size"])
                    count -= CONFIG["EMAIL"]["batch_size"]

        except Exception as e:
            logger.error("process_unanalyzed_error", error=str(e))
            raise

    def process_emails(self, count: int = CONFIG["EMAIL"]["batch_size"]) -> None:
        """Process a batch of unanalyzed emails."""
        try:
            with get_email_session() as session:
                # Get batch of unanalyzed emails
                result = session.execute(
                    text(
                        """
                    SELECT e.* FROM emails e
                    LEFT JOIN email_analysis ea ON e.id = ea.email_id
                    WHERE ea.email_id IS NULL
                    LIMIT :count
                    """
                    ),
                    {"count": count},
                ).fetchall()

                emails = result

                for email in emails:
                    email_dict = {
                        "id": email.id,
                        "threadId": email.thread_id,
                        "subject": email.subject,
                        "body": email.body,
                        "date": email.received_date.isoformat(),
                        "labels": email.labels.split(",") if email.labels else [],
                    }

                    analysis = self.analyze_email(email_dict)
                    if analysis:
                        self.save_analysis(
                            email.id, email.thread_id, analysis, json.dumps(email_dict)
                        )

                    # Sleep to respect rate limits
                    time.sleep(API_CONFIG["RATE_LIMIT_DELAY"])

        except Exception as e:
            logger.error("process_emails_error", error=str(e))
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process and analyze emails using Claude API"
    )
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()

    try:
        analyzer = EmailAnalyzer(test_mode=args.test)
        analyzer.process_unanalyzed_emails()
    except Exception as e:
        logger.error("main_error", error=str(e))
        raise


if __name__ == "__main__":
    main()
