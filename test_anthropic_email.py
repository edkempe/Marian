# Part 1: Imports and first half of implementation

import sqlite3
from anthropic import Anthropic
import json
from datetime import datetime, timedelta
import time
import asyncio
from typing import List, Dict
import logging
import backoff
import pandas as pd
from tqdm import tqdm
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import concurrent.futures
import re

# Set up logging with more detail
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more verbose output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def verify_environment():
    """Verify all required files and configurations exist"""
    # Check .env file
    env_path = Path('.env')
    if not env_path.exists():
        raise FileNotFoundError(".env file not found. Please create one with your ANTHROPIC_API_KEY")
    
    # Check database
    db_path = Path('email_store.db')
    if not db_path.exists():
        raise FileNotFoundError("email_store.db not found. Please make sure the database exists")
    
    # Verify database has content
    conn = sqlite3.connect('email_store.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM emails")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        raise ValueError("Database exists but contains no emails")
    
    logging.info(f"Environment verified. Found {count} emails in database")
    return True

def get_api_key() -> str:
    """Get Anthropic API key from environment variables"""
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv()
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError(
            "Anthropic API key not found. Please set the ANTHROPIC_API_KEY "
            "environment variable or add it to .env file"
        )
    return api_key

class EmailBatchProcessor:
    def __init__(self, api_key: str, batch_size: int = 10, max_concurrent: int = 2, 
                 requests_per_minute: int = 15):
        self.client = Anthropic(api_key=api_key)
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.delay = 60 / requests_per_minute
        self.db_path = 'email_store.db'
        self.conn = self.get_db_connection()
        self.setup_database()
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_concurrent
        )
        
        logging.info(f"Initialized with batch_size={batch_size}, "
                    f"max_concurrent={max_concurrent}, "
                    f"requests_per_minute={requests_per_minute}")

    def get_db_connection(self):
        """Create a database connection with proper settings"""
        conn = sqlite3.connect(self.db_path, timeout=60)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def setup_database(self):
        """Initialize database tables and indices"""
        cursor = self.conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS email_triage
                         (email_id TEXT PRIMARY KEY,
                          priority TEXT,
                          category TEXT,
                          summary TEXT,
                          action_items TEXT,
                          sentiment TEXT,
                          analysis_date TEXT,
                          batch_id INTEGER,
                          processing_status TEXT,
                          error_message TEXT,
                          retry_count INTEGER DEFAULT 0,
                          raw_response TEXT)''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_processing_status ON email_triage(processing_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON email_triage(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_batch_id ON email_triage(batch_id)')
        
        self.conn.commit()
        logging.info("Database setup completed")

    def extract_json_from_text(self, text: str) -> str:
        """Extract JSON object from text that might contain additional content"""
        try:
            # Try to find JSON pattern with regex
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.finditer(json_pattern, text)
            
            # Get the largest matching JSON object
            valid_jsons = []
            for match in matches:
                try:
                    json_str = match.group()
                    # Verify it's valid JSON
                    json.loads(json_str)
                    valid_jsons.append(json_str)
                except json.JSONDecodeError:
                    continue
            
            if valid_jsons:
                # Return the largest valid JSON string found
                return max(valid_jsons, key=len)
            
        except Exception as e:
            logging.error(f"Error extracting JSON: {str(e)}")
        
        raise ValueError("No valid JSON found in response")

    def get_unprocessed_batch(self) -> List[Dict]:
        """Fetch a batch of unprocessed emails"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT e.id, e.subject, e.sender, e.date, e.body, e.labels
            FROM emails e
            LEFT JOIN email_triage t ON e.id = t.email_id
            WHERE t.email_id IS NULL
               OR (t.processing_status = 'failed' AND t.retry_count < 3)
            LIMIT ?
        ''', (self.batch_size,))
        
        emails = []
        for row in cursor.fetchall():
            emails.append({
                'id': row[0],
                'subject': row[1],
                'sender': row[2],
                'date': row[3],
                'body': row[4],
                'labels': row[5]
            })
        
        if emails:
            logging.info(f"Retrieved {len(emails)} emails for processing")
        return emails