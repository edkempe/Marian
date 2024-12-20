#!/usr/bin/env python3
import sqlite3
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
import anthropic

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

class EmailAnalyzer:
    """Analyzes emails using Claude-3-Haiku."""

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

    def __init__(self):
        """Initialize the analyzer with database connections."""
        self.email_db_path = "email_store.db"
        self.analysis_db_path = "email_analysis.db"
        
        # Connect to email database
        self.email_db = sqlite3.connect(self.email_db_path)
        self.email_db.row_factory = sqlite3.Row
        self.cursor = self.email_db.cursor()
        
        # Attach analysis database
        self.cursor.execute(f"ATTACH DATABASE '{self.analysis_db_path}' AS analysis")
        
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # Set up database schema
        self._setup_analysis_db()
        
    def _setup_analysis_db(self):
        """Set up the analysis database schema."""
        try:
            # Drop existing table if it exists
            self.cursor.execute("DROP TABLE IF EXISTS analysis.email_analysis")
            self.email_db.commit()
            
            # Create new table with strict schema matching
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis.email_analysis (
                email_id TEXT PRIMARY KEY,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                summary TEXT NOT NULL,
                category TEXT NOT NULL CHECK(json_valid(category)),  -- JSON array
                priority_score INTEGER NOT NULL CHECK(priority_score BETWEEN 1 AND 5),
                priority_reason TEXT NOT NULL,
                action_needed INTEGER NOT NULL CHECK(action_needed IN (0, 1)),  -- Boolean
                action_type TEXT NOT NULL CHECK(json_valid(action_type)),  -- JSON array
                action_deadline TEXT,  -- Optional
                key_points TEXT NOT NULL CHECK(json_valid(key_points)),  -- JSON array
                people_mentioned TEXT NOT NULL CHECK(json_valid(people_mentioned)),  -- JSON array
                links_found TEXT NOT NULL CHECK(json_valid(links_found)),  -- JSON array of full URLs
                links_display TEXT NOT NULL CHECK(json_valid(links_display)),  -- JSON array of truncated URLs
                project TEXT,  -- Optional
                topic TEXT,  -- Optional
                ref_docs TEXT,  -- Optional
                sentiment TEXT NOT NULL CHECK(sentiment IN ('positive', 'negative', 'neutral')),
                confidence_score REAL NOT NULL CHECK(confidence_score BETWEEN 0 AND 1),
                raw_analysis TEXT NOT NULL CHECK(json_valid(raw_analysis))  -- Full JSON response
            )""")
            self.email_db.commit()
            
            # Verify table exists
            self.cursor.execute("SELECT name FROM analysis.sqlite_master WHERE type='table' AND name='email_analysis'")
            if not self.cursor.fetchone():
                raise Exception("Failed to create email_analysis table")
            logger.info("Successfully created email_analysis table")
            
        except Exception as e:
            logger.error(f"Error setting up database: {str(e)}")
            self.email_db.rollback()
            raise
            
    def analyze_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze email content using Claude-3-Haiku."""
        try:
            # Format the prompt with email data
            prompt_data = {
                'subject': email_data.get('subject', 'No Subject'),
                'sender': email_data.get('sender', 'Unknown'),
                'email_type': email_data.get('type', 'Unknown'),
                'labels': email_data.get('labels', []),
                'thread_id': email_data.get('thread_id', ''),
                'date': email_data.get('date', 'Unknown'),
                'has_attachments': email_data.get('has_attachments', False),
                'truncated_body': email_data.get('content', '')[:2000]  # Truncate long emails
            }
            
            formatted_prompt = self.ANALYSIS_PROMPT.format(**prompt_data)

            # Make API call to Claude-3-Haiku
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": formatted_prompt}
                ]
            )

            # Parse and validate the response
            try:
                # Extract JSON from response
                text = response.content[0].text if isinstance(response.content, list) else response.content
                
                # Try to parse as JSON directly first
                try:
                    analysis = json.loads(text)
                except json.JSONDecodeError:
                    # If that fails, try to extract JSON from text
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start >= 0 and end > start:
                        raw_analysis = text[start:end]
                        analysis = json.loads(raw_analysis)
                    else:
                        logger.error(f"Could not find JSON in response: {text}")
                        return None

                # Validate and normalize the response
                try:
                    # Helper function to safely convert to JSON array
                    def safe_json_array(value, field_name):
                        if not value:
                            return json.dumps([])
                        if isinstance(value, str):
                            try:
                                value = json.loads(value)
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid JSON in {field_name}, using empty array")
                                return json.dumps([])
                        if not isinstance(value, list):
                            logger.warning(f"Expected list for {field_name}, got {type(value)}, using empty array")
                            return json.dumps([])
                        return json.dumps(value)

                    # Helper function to safely convert to int within range
                    def safe_int_range(value, min_val, max_val, default, field_name):
                        try:
                            if isinstance(value, str):
                                value = int(float(value))
                            elif isinstance(value, float):
                                value = int(value)
                            elif not isinstance(value, int):
                                raise ValueError(f"Cannot convert {type(value)} to int")
                            return max(min_val, min(max_val, value))
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid {field_name}: {value}, using default {default}")
                            return default

                    # Helper function to safely convert to float within range
                    def safe_float_range(value, min_val, max_val, default, field_name):
                        try:
                            if isinstance(value, str):
                                value = float(value)
                            elif not isinstance(value, (int, float)):
                                raise ValueError(f"Cannot convert {type(value)} to float")
                            return max(min_val, min(max_val, float(value)))
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid {field_name}: {value}, using default {default}")
                            return default

                    normalized = {
                        'summary': str(analysis.get('summary', '')).strip(),
                        'category': safe_json_array(analysis.get('category'), 'category'),
                        'priority': {
                            'score': safe_int_range(
                                analysis.get('priority', {}).get('score'), 
                                1, 5, 3, 
                                'priority score'
                            ),
                            'reason': str(analysis.get('priority', {}).get('reason', 'Default priority')).strip()
                        },
                        'action': {
                            'needed': bool(analysis.get('action', {}).get('needed', False)),
                            'type': safe_json_array(analysis.get('action', {}).get('type'), 'action type'),
                            'deadline': str(analysis.get('action', {}).get('deadline', '')).strip()
                        },
                        'key_points': safe_json_array(analysis.get('key_points'), 'key_points'),
                        'people_mentioned': safe_json_array(analysis.get('people_mentioned'), 'people_mentioned'),
                        'links_found': safe_json_array(analysis.get('links_found'), 'links_found'),
                        'links_display': json.dumps([
                            url[:100] + '...' if len(url) > 100 else url 
                            for url in (analysis.get('links_found', []) if isinstance(analysis.get('links_found'), list) else [])
                        ]),
                        'context': {
                            'project': str(analysis.get('context', {}).get('project', '')).strip(),
                            'topic': str(analysis.get('context', {}).get('topic', '')).strip(),
                            'ref_docs': str(analysis.get('context', {}).get('ref_docs', '')).strip()
                        },
                        'sentiment': str(analysis.get('sentiment', 'neutral')).lower().strip(),
                        'confidence_score': safe_float_range(
                            analysis.get('confidence_score'), 
                            0.0, 1.0, 0.9, 
                            'confidence score'
                        ),
                        'raw_analysis': json.dumps(analysis)
                    }

                    # Final sentiment validation
                    if normalized['sentiment'] not in ('positive', 'negative', 'neutral'):
                        logger.warning(f"Invalid sentiment: {normalized['sentiment']}, using neutral")
                        normalized['sentiment'] = 'neutral'

                except Exception as e:
                    logger.error(f"Error normalizing response: {str(e)}")
                    logger.error(f"Raw response: {text}")
                    return None

                return normalized

            except Exception as e:
                logger.error(f"Error parsing response: {str(e)}")
                logger.error(f"Raw response: {text}")
                return None

        except Exception as e:
            logger.error(f"Error analyzing email: {str(e)}")
            return None

    def process_emails(self, batch_size: int = 10) -> None:
        """Process a batch of unanalyzed emails."""
        try:
            # Get unanalyzed emails
            self.cursor.execute("""
                SELECT id, subject, sender, date, body, labels
                FROM emails 
                WHERE id NOT IN (
                    SELECT email_id FROM analysis.email_analysis
                )
                LIMIT ?
            """, (batch_size,))
            
            emails = self.cursor.fetchall()
            if not emails:
                logger.info("No new emails to analyze")
                return

            logger.info(f"Found {len(emails)} emails to analyze")
            for email in tqdm(emails, desc="Analyzing emails"):
                email_data = {
                    'id': email['id'],
                    'subject': email['subject'],
                    'sender': email['sender'],
                    'date': email['date'],
                    'content': email['body'],
                    'thread_id': '',  # Not available in schema
                    'labels': email['labels']
                }

                analysis = self.analyze_email(email_data)
                if analysis:
                    # Store analysis results
                    insert_query = """
                        INSERT INTO analysis.email_analysis (
                            email_id, summary, category, priority_score, priority_reason,
                            action_needed, action_type, action_deadline, key_points,
                            people_mentioned, links_found, links_display, project, topic, ref_docs,
                            sentiment, confidence_score, raw_analysis
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    logger.info(f"Inserting analysis for email {email_data['id']}")
                    self.cursor.execute(insert_query, (
                        email_data['id'],
                        analysis.get('summary', ''),
                        analysis.get('category', ''),
                        analysis['priority']['score'],
                        analysis['priority']['reason'],
                        1 if analysis['action']['needed'] else 0,
                        analysis['action']['type'],
                        analysis['action']['deadline'],
                        analysis.get('key_points', ''),
                        analysis.get('people_mentioned', ''),
                        analysis.get('links_found', ''),
                        analysis.get('links_display', ''),
                        analysis['context']['project'],
                        analysis['context']['topic'],
                        analysis['context']['ref_docs'],
                        analysis.get('sentiment', 'neutral'),
                        analysis.get('confidence_score', 0.9),
                        analysis.get('raw_analysis', '')
                    ))
                    self.email_db.commit()

                # Add delay to respect rate limits
                time.sleep(1)

        except Exception as e:
            logger.error(f"Error processing emails: {str(e)}")
            self.email_db.rollback()
            raise

    def close(self):
        """Close database connections."""
        self.email_db.close()

def main():
    try:
        verify_environment()
        analyzer = EmailAnalyzer()
        analyzer.process_emails(batch_size=10)  # Process 10 emails
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()