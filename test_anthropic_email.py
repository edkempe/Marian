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
from prompt_manager import PromptManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def verify_environment():
    """Verify environment is set up correctly"""
    env_path = Path('.env')
    if not env_path.exists():
        raise FileNotFoundError(".env file not found. Please create one with your ANTHROPIC_API_KEY")
    
    db_path = "test_email_store.db"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database {db_path} not found")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM emails")
    email_count = cursor.fetchone()[0]
    logging.info(f"Found {email_count} emails in database")
    conn.close()

def get_api_key():
    """Get Anthropic API key from environment variables"""
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    return api_key

class EmailProcessor:
    def __init__(self, api_key: str, batch_size: int = 10):
        self.client = Anthropic(api_key=api_key)
        self.batch_size = batch_size
        self.conn = sqlite3.connect('test_email_store.db')
        self.cursor = self.conn.cursor()
        self.prompt_manager = PromptManager('prompts.db')
        
        # Get the current active prompt for this script
        self.current_prompt = self.prompt_manager.get_active_prompt(
            script_name=os.path.basename(__file__)
        )
        
        # Create email_triage table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_triage (
                email_id TEXT PRIMARY KEY,
                analysis_json TEXT,
                processed_at TIMESTAMP,
                prompt_id TEXT,
                raw_prompt_text TEXT,
                FOREIGN KEY (email_id) REFERENCES emails (id)
            )
        ''')
        self.conn.commit()

    def get_unprocessed_emails(self):
        """Get a batch of unprocessed emails"""
        try:
            self.cursor.execute('''
                SELECT e.id, e.subject, e.sender, e.date, e.body, 
                       e.email_type, e.labels, e.thread_id, e.has_attachments
                FROM emails e
                LEFT JOIN email_triage t ON e.id = t.email_id
                WHERE t.email_id IS NULL
                ORDER BY e.date DESC
                LIMIT 200  -- Process 200 emails
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error: {str(e)}")
            return []

    def process_email(self, email_data):
        """Process a single email"""
        try:
            email_id, subject, sender, date, body, email_type, labels, thread_id, has_attachments = email_data
            logging.info(f"Processing email {email_id}")
            
            # Truncate the body if it's too long
            max_body_length = 4000  # Reasonable limit for API
            truncated_body = body[:max_body_length] if body else ""
            if body and len(body) > max_body_length:
                truncated_body += "... [truncated]"
            
            # Format prompt with email data
            raw_prompt = self.current_prompt['prompt_text'].format(
                subject=subject,
                sender=sender,
                email_type=email_type or "unknown",
                labels=labels or "none",
                thread_id=thread_id or "none",
                date=date,
                has_attachments=bool(has_attachments),
                truncated_body=truncated_body
            )

            # Record start time for response time tracking
            start_time = time.time()
            
            # Make API call
            response = self.client.messages.create(
                max_tokens=self.current_prompt['max_tokens'],
                messages=[{"role": "user", "content": raw_prompt}],
                model=self.current_prompt['model_name']
            )
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Get the analysis from the response
            analysis = response.content[0].text
            analysis_json = json.loads(analysis)
            
            # Store in database with prompt tracking
            self.cursor.execute('''
                INSERT INTO email_triage (
                    email_id, analysis_json, processed_at,
                    prompt_id, raw_prompt_text
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                email_id, 
                analysis,
                datetime.now().isoformat(),
                self.current_prompt['prompt_id'],
                raw_prompt
            ))
            
            # Update prompt statistics
            self.prompt_manager.update_prompt_stats(
                prompt_id=self.current_prompt['prompt_id'],
                response_time_ms=response_time_ms,
                confidence_score=analysis_json.get('confidence_score', 0),
                was_successful=True
            )
            
            self.conn.commit()
            logging.info(f"Successfully analyzed email {email_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error processing email {email_id}: {str(e)}")
            if 'prompt_id' in self.current_prompt:
                self.prompt_manager.update_prompt_stats(
                    prompt_id=self.current_prompt['prompt_id'],
                    response_time_ms=0,  # No valid response time for errors
                    confidence_score=0,
                    was_successful=False
                )
            return False

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    try:
        verify_environment()
        api_key = get_api_key()
        
        processor = EmailProcessor(api_key=api_key, batch_size=20)
        emails = processor.get_unprocessed_emails()
        
        if not emails:
            logging.info("No new emails to process")
            sys.exit(0)
        
        logging.info(f"Starting analysis of {len(emails)} emails...")
        
        success_count = 0
        for email in tqdm(emails, desc="Processing emails"):
            if processor.process_email(email):
                success_count += 1
        
        logging.info(f"Successfully analyzed {success_count} out of {len(emails)} emails")
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        sys.exit(1)