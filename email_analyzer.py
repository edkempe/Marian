#!/usr/bin/env python3
import sqlite3
from anthropic import Anthropic
import json
from datetime import datetime
import logging
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from tqdm import tqdm
import time
from typing import List, Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def verify_environment():
    """Verify all required environment variables are set"""
    required_vars = ['ANTHROPIC_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

def get_api_key():
    """Get Anthropic API key from environment"""
    load_dotenv()  # Load .env file if it exists
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    logging.info("Successfully loaded API key")
    return api_key

class EmailProcessor:
    def __init__(self, api_key: str, batch_size: int = 10):
        # Initialize Anthropic client
        self.client = Anthropic(api_key=api_key)
        self.batch_size = batch_size
        self.conn = sqlite3.connect('test_email_store.db')
        self.cursor = self.conn.cursor()
        
        # Initialize database tables
        self._init_db()
        
        # Hardcoded analysis prompt
        self.analysis_prompt = {
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
                "summary": "string"
            }
        }

    def _init_db(self):
        """Initialize database tables"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                subject TEXT,
                sender TEXT,
                date TEXT,
                body TEXT,
                has_attachments INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_triage (
                email_id TEXT PRIMARY KEY,
                analysis_json TEXT,
                processed_at TIMESTAMP,
                prompt_name TEXT NOT NULL,
                purpose TEXT NOT NULL,
                task TEXT NOT NULL,
                raw_prompt_text TEXT
            )
        ''')
        self.conn.commit()

    def get_unprocessed_emails(self):
        """Get list of emails that haven't been analyzed"""
        try:
            self.cursor.execute('''
                SELECT e.id, e.subject, e.sender, e.date, e.body, e.has_attachments
                FROM emails e
                LEFT JOIN email_triage t ON e.id = t.email_id
                WHERE t.email_id IS NULL
                ORDER BY e.date DESC
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error: {str(e)}")
            return []

    def process_email(self, email_data, max_retries=3, retry_delay=2):
        """Process a single email"""
        try:
            email_id, subject, sender, date, body, has_attachments = email_data
            logging.info(f"Processing email {email_id}")
            
            # Truncate the body if it's too long
            max_body_length = 4000  # Reasonable limit for API
            truncated_body = body[:max_body_length] if body else ""
            
            # Format prompt with email data
            raw_prompt = self.analysis_prompt['prompt_text'].format(
                subject,
                sender,
                date,
                bool(has_attachments),
                len(body) if body else 0,
                len(body) > max_body_length if body else False,
                truncated_body
            )
            
            # Call Anthropic API with retries
            for attempt in range(max_retries):
                try:
                    message = self.client.messages.create(
                        model=self.analysis_prompt['model_name'],
                        max_tokens=self.analysis_prompt['max_tokens'],
                        temperature=0.7 if self.analysis_prompt['temperature'] is None else self.analysis_prompt['temperature'],
                        messages=[{
                            "role": "user",
                            "content": raw_prompt
                        }]
                    )
                    break  # Success, exit retry loop
                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise  # Re-raise the last error
                    logging.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            
            # Parse response and validate JSON
            response_text = message.content[0].text
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
            self.cursor.execute('''
                INSERT OR REPLACE INTO email_triage (
                    email_id, analysis_json, processed_at,
                    prompt_name, purpose, task, raw_prompt_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                email_id, 
                json.dumps(analysis),  # Store the parsed and re-serialized JSON
                datetime.now().isoformat(),
                self.analysis_prompt['prompt_name'],
                self.analysis_prompt['purpose'],
                self.analysis_prompt['task'],
                raw_prompt
            ))
            
            self.conn.commit()
            logging.info(f"Successfully analyzed email {email_id}")
            logging.info(f"Analysis: {json.dumps(analysis, indent=2)}")
            return True
            
        except Exception as e:
            logging.error(f"Error processing email {email_id}: {str(e)}")
            return False

    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def test_email_analysis():
    """Test email analysis with a single test email"""
    try:
        # Initialize processor
        api_key = get_api_key()
        processor = EmailProcessor(api_key=api_key)
        
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
            0  # has_attachments
        )
        
        processor.cursor.execute('''
            INSERT OR REPLACE INTO emails (id, subject, sender, date, body, has_attachments)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', test_email)
        processor.conn.commit()
        
        # Process the email
        logging.info("Processing test email...")
        if processor.process_email(test_email):
            # Fetch and display the analysis
            processor.cursor.execute('''
                SELECT analysis_json
                FROM email_triage
                WHERE email_id = ?
            ''', (test_email[0],))
            
            result = processor.cursor.fetchone()
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
    test_email_analysis()