#!/usr/bin/env python3
import sqlite3
import requests
import json
from datetime import datetime
import logging
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from tqdm import tqdm
import time
from typing import List, Dict, Any
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_environment():
    """Verify all required environment variables are set"""
    required_vars = ['ANTHROPIC_API_KEY']
    load_dotenv(verbose=True)
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    logging.info("Environment verification successful")

def get_api_key():
    """Get Anthropic API key from environment"""
    load_dotenv(verbose=True)
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise EnvironmentError("Failed to load ANTHROPIC_API_KEY from environment")
    return api_key

class EmailProcessor:
    def __init__(self, api_key: str):
        """Initialize EmailProcessor."""
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/complete"
        self.headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Connect to source email database
        self.email_db = sqlite3.connect('email_store.db')
        self.email_cursor = self.email_db.cursor()
        
        # Connect to analysis database
        self.analysis_db = sqlite3.connect('email_analysis.db')
        self.analysis_cursor = self.analysis_db.cursor()
        
        # Initialize analysis database tables
        self._init_analysis_db()

    def _init_analysis_db(self):
        """Initialize the analysis database tables"""
        self.analysis_cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_analysis (
                email_id TEXT PRIMARY KEY,
                analysis_result TEXT,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sentiment TEXT,
                topics TEXT,
                project TEXT,
                action_items TEXT,
                summary TEXT,
                confidence REAL DEFAULT 0.0
            )
        ''')
        self.analysis_db.commit()

    def analyze_email(self, email_id: str, subject: str, sender: str, date: str, body: str) -> Dict[str, Any]:
        """Analyze a single email using Anthropic's Claude API."""
        prompt = f"""Analyze this email and provide a structured analysis with the following information:

Email:
Subject: {subject}
From: {sender}
Date: {date}
Body:
{body}

Provide a JSON object with the following fields:
- intent: The main purpose of the email
- tone: The emotional tone (formal, friendly, urgent)
- urgency: How urgent is it (high, medium, low)
- importance: How important is it (high, medium, low)
- actions_required: List of specific actions needed
- deadlines: Any mentioned deadlines
- key_topics: Main topics (3-7 key topics)
- project: Related project name
- summary: Brief 1-2 sentence summary

Format your response as a valid JSON object."""

        try:
            # Call Anthropic API with retries
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        self.base_url,
                        headers=self.headers,
                        json={
                            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                            "model": "claude-2.1",
                            "max_tokens_to_sample": 1000,
                            "temperature": 0.0
                        }
                    )
                    response.raise_for_status()
                    completion = response.json()["completion"]
                    break
                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise
                    logging.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay * (attempt + 1))

            # Extract JSON from the response
            try:
                # Try to parse as JSON directly
                analysis = json.loads(completion)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the response
                json_match = re.search(r'\{[\s\S]*\}', completion)
                if json_match:
                    analysis = json.loads(json_match.group(0))
                else:
                    raise ValueError("Could not extract valid JSON from response")

            # Add confidence score based on completeness
            required_fields = ['intent', 'tone', 'urgency', 'importance', 'actions_required', 
                             'deadlines', 'key_topics', 'project', 'summary']
            completeness = sum(1 for field in required_fields if field in analysis) / len(required_fields)
            analysis['confidence'] = round(completeness, 2)

            # Store analysis results
            self.save_analysis(email_id, analysis)
            logging.info(f"Successfully analyzed email {email_id}")
            logging.info(f"Analysis: {json.dumps(analysis, indent=2)}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing email {email_id}: {str(e)}")
            return {
                'error': str(e),
                'intent': 'unknown',
                'tone': 'unknown',
                'urgency': 'low',
                'importance': 'low',
                'actions_required': [],
                'deadlines': [],
                'key_topics': [],
                'project': 'unknown',
                'summary': 'Failed to analyze email',
                'confidence': 0.0
            }

    def save_analysis(self, email_id: str, analysis_result: dict):
        """Save analysis results to the analysis database"""
        # Extract topics and sentiment from the analysis
        topics = json.dumps(analysis_result.get('key_topics', []))
        sentiment = json.dumps([analysis_result.get('tone', '')])
        action_items = json.dumps(analysis_result.get('actions_required', []))
        project = analysis_result.get('project', '')
        confidence = analysis_result.get('confidence', 0.85)  # Default confidence if not provided
        
        self.analysis_cursor.execute('''
            INSERT OR REPLACE INTO email_analysis
            (email_id, analysis_result, sentiment, topics, project, action_items, summary, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email_id,
            json.dumps(analysis_result),
            sentiment,
            topics,
            project,
            action_items,
            analysis_result.get('summary', ''),
            confidence
        ))
        self.analysis_db.commit()

    def get_unanalyzed_emails(self, limit: int = 50) -> List[Dict]:
        """Get emails that haven't been analyzed yet"""
        # Debug: Check total emails in source database
        self.email_cursor.execute('SELECT COUNT(*) FROM emails')
        total_emails = self.email_cursor.fetchone()[0]
        logging.info(f"Total emails in source database: {total_emails}")
        
        # Get list of already analyzed emails
        self.analysis_cursor.execute('SELECT email_id FROM email_analysis')
        analyzed_ids = {row[0] for row in self.analysis_cursor.fetchall()}
        logging.info(f"Already analyzed emails: {len(analyzed_ids)}")
        
        # Get emails from source database that haven't been analyzed
        query = '''
            SELECT id, subject, sender, date, body
            FROM emails
            ORDER BY date DESC
            LIMIT ?
        '''
        logging.info(f"Executing query: {query}")
        self.email_cursor.execute(query, (limit,))
        
        emails = []
        for row in self.email_cursor.fetchall():
            emails.append({
                'id': row[0],
                'subject': row[1],
                'sender': row[2],
                'date': row[3],
                'body': row[4]
            })
        logging.info(f"Found {len(emails)} emails to analyze")
        return emails

    def process_email(self, email_data, max_retries=3, retry_delay=2):
        """Process a single email"""
        try:
            email_id, subject, sender, date, body = email_data
            logging.info(f"Processing email {email_id}")
            
            # Truncate the body if it's too long
            max_body_length = 4000  # Reasonable limit for API
            truncated_body = body[:max_body_length] if body else ""
            
            # Format prompt with email data
            analysis_prompt = {
                'prompt_text': '''You are an expert email analyst. Analyze the following email and extract key information.

Consider:
1. The sender's intent and tone
2. The urgency and importance
3. Required actions or responses
4. Key dates or deadlines
5. Important entities or topics mentioned

Format your response as a JSON object with these fields:
- intent: Primary purpose of the email
- tone: Professional/casual/urgent/etc
- urgency: high/medium/low
- importance: high/medium/low
- actions_required: List of required actions
- deadlines: Any mentioned deadlines
- key_topics: Main topics or entities
- project: The project or initiative this email relates to (if any)
- summary: Brief summary of the email

Email details:
Subject: {0}
From: {1}
Date: {2}
Has Attachments: {3}
Body Length: {4} characters
Body truncated: {5}

Email body:
{6}

Analyze the above email and respond with a valid JSON object containing all the required fields.''',
                'prompt_name': 'test_anthropic_email.email.analysis',
                'purpose': 'email',
                'task': 'analysis',
                'model_name': 'claude-2.1',
                'max_tokens': 1500,
                'temperature': None,
                'expected_response_format': {
                    "intent": "string",
                    "tone": "string",
                    "urgency": "string",
                    "importance": "string",
                    "actions_required": ["string"],
                    "deadlines": ["string"],
                    "key_topics": ["string"],
                    "project": "string",
                    "summary": "string"
                }
            }
            raw_prompt = analysis_prompt['prompt_text'].format(
                subject,
                sender,
                date,
                bool(False),
                len(body) if body else 0,
                len(body) > max_body_length if body else False,
                truncated_body
            )
            
            # Call Anthropic API with retries
            for attempt in range(max_retries):
                try:
                    completion = self._call_anthropic_api(raw_prompt)
                    break  # Success, exit retry loop
                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise  # Re-raise the last error
                    logging.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            
            # Parse response and validate JSON
            response_text = completion
            try:
                # Try to parse as JSON directly
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    analysis = json.loads(json_match.group(0))
                else:
                    raise ValueError("Could not extract valid JSON from response")
            
            # Store analysis results
            self.save_analysis(email_id, analysis)
            logging.info(f"Successfully analyzed email {email_id}")
            logging.info(f"Analysis: {json.dumps(analysis, indent=2)}")
            return True
            
        except Exception as e:
            logging.error(f"Error processing email {email_id}: {str(e)}")
            return False

    def _call_anthropic_api(self, prompt: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """Make a direct API call to Anthropic's Claude API"""
        url = f"{self.base_url}"
        data = {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "model": "claude-2.1",
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()["completion"]

    def close(self):
        """Close database connections"""
        self.email_db.close()
        self.analysis_db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def test_email_analysis():
    """Test email analysis with a single test email"""
    try:
        # Initialize processor
        api_key = get_api_key()
        with EmailProcessor(api_key=api_key) as processor:
            # Insert a test email
            test_email = (
                'test123',  # id
                'Team Meeting Next Week',  # subject
                'alice@example.com',  # sender
                '2024-12-18',  # date
                '''Hi team,
                
                Let's have our weekly sync meeting next Tuesday at 2 PM PST.
                Please review the Q4 metrics before the meeting and come prepared
                with your updates.
                
                Important agenda items:
                1. Q4 Review
                2. 2024 Planning
                3. New Project Kickoff
                
                Best regards,
                Alice''',  # body
            )
            
            processor.email_cursor.execute('''
                INSERT OR REPLACE INTO emails (id, subject, sender, date, body)
                VALUES (?, ?, ?, ?, ?)
            ''', test_email)
            processor.email_db.commit()
            
            # Process the email
            logging.info("Processing test email...")
            if processor.process_email(test_email):
                # Fetch and display the analysis
                processor.analysis_cursor.execute('''
                    SELECT analysis_result
                    FROM email_analysis
                    WHERE email_id = ?
                ''', (test_email[0],))
                
                result = processor.analysis_cursor.fetchone()
                if result:
                    analysis = json.loads(result[0])
                    logging.info("Analysis results:")
                    logging.info(json.dumps(analysis, indent=2))
                else:
                    logging.error("No analysis found for test email")
            else:
                logging.error("Failed to process test email")
                
    except Exception as e:
        logging.error(f"Error in test: {str(e)}")
        raise

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        verify_environment()
        api_key = get_api_key()
        
        with EmailProcessor(api_key=api_key) as processor:
            # Get unanalyzed emails (testing with just 50 first)
            emails = processor.get_unanalyzed_emails(limit=50)
            logging.info(f"Found {len(emails)} unanalyzed emails")
            
            # Process each email
            for email in tqdm(emails, desc="Processing emails"):
                success = processor.process_email((
                    email['id'],
                    email['subject'],
                    email['sender'],
                    email['date'],
                    email['body']
                ))
                if not success:
                    logging.error(f"Failed to process email {email['id']}")
                
            # Show results
            processor.analysis_cursor.execute('''
                SELECT email_id, analysis_result
                FROM email_analysis
            ''')
            results = processor.analysis_cursor.fetchall()
            logging.info(f"\nProcessed {len(results)} emails:")
            for email_id, analysis in results:
                analysis_dict = json.loads(analysis)
                logging.info(f"\nEmail {email_id}:")
                logging.info(f"Summary: {analysis_dict.get('summary', 'No summary available')}")
            
            logging.info("\nEmail analysis complete")
            
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        raise