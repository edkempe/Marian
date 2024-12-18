#!/usr/bin/env python3
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class PromptManager:
    def __init__(self, db_path: str = "prompts.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_tables()

    def _ensure_tables(self):
        """Ensure all necessary tables exist"""
        # Drop existing tables and views
        self.conn.executescript('''
            DROP VIEW IF EXISTS prompt_performance;
            DROP TABLE IF EXISTS email_triage;
            DROP TABLE IF EXISTS prompts;
        ''')
        
        # Create tables from schema
        with open('schema/prompt_tracking.sql', 'r') as f:
            self.conn.executescript(f.read())
        self.conn.commit()

    def register_prompt(
        self,
        prompt_text: str,
        version: str,
        model_name: str,
        max_tokens: int,
        description: str,
        expected_response_format: Dict,
        required_input_fields: List[str],
        token_estimate: int,
        script_name: str,
        temperature: Optional[float] = None
    ) -> str:
        """Register a new prompt version and return its ID"""
        prompt_id = str(uuid.uuid4())
        
        self.conn.execute('''
            INSERT INTO prompts (
                prompt_id, prompt_text, version_number, model_name, 
                max_tokens, temperature, description, script_name,
                expected_response_format, required_input_fields,
                token_estimate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prompt_id, prompt_text, version,
            model_name, max_tokens, temperature, description, script_name,
            json.dumps(expected_response_format),
            json.dumps(required_input_fields),
            token_estimate
        ))
        self.conn.commit()
        return prompt_id

    def get_active_prompt(self, script_name: str, version: Optional[str] = None) -> Dict:
        """Get the most recent active prompt for a specific script, or a specific version"""
        query = """
            SELECT * FROM prompts 
            WHERE active = TRUE
            AND script_name = ?
        """
        params = [script_name]
        
        if version:
            query += " AND version_number = ?"
            params.append(version)
            cursor = self.conn.execute(query, params)
        else:
            query += " ORDER BY created_date DESC LIMIT 1"
            cursor = self.conn.execute(query, params)
        
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"No active prompt found for script: {script_name}")
        
        return dict(result)

    def update_prompt_stats(self, prompt_id: str, response_time_ms: int, 
                          confidence_score: float, was_successful: bool):
        """Update usage statistics for a prompt"""
        self.conn.execute('''
            UPDATE prompts 
            SET times_used = times_used + 1,
                last_used_date = ?,
                average_response_time_ms = (
                    (average_response_time_ms * times_used + ?) / (times_used + 1)
                ),
                average_confidence_score = (
                    (COALESCE(average_confidence_score, 0) * times_used + ?) / (times_used + 1)
                ),
                failure_rate = (
                    (failure_rate * times_used + ?) / (times_used + 1)
                )
            WHERE prompt_id = ?
        ''', (
            datetime.now().isoformat(),
            response_time_ms,
            confidence_score,
            0 if was_successful else 1,
            prompt_id
        ))
        self.conn.commit()

    def get_prompt_performance(self) -> List[Dict]:
        """Get performance metrics for all prompts"""
        cursor = self.conn.execute('''
            SELECT * FROM prompt_performance
            ORDER BY version_number DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def __del__(self):
        self.conn.close()

# Previous email analysis prompt (simpler version)
PREVIOUS_EMAIL_PROMPT = '''Analyze this email and extract key information:

Subject: {subject}
From: {sender}
Date: {date}
Body: {truncated_body}

Provide your analysis in JSON format with these fields:
- summary: A brief summary of the email content (50 words or less)
- category: The type of email (e.g., 'promotional', 'personal', 'business', etc.)
- priority: A number from 1-5 (1 being highest priority)
- action_needed: Whether this email requires a response or action (true/false)
- key_points: List of main points from the email (maximum 3 points)
- sentiment: The overall tone ('positive', 'negative', or 'neutral')'''

# Current email analysis prompt with expanded fields
CURRENT_EMAIL_PROMPT = """Analyze this email and extract key information within 1000 tokens total:
Subject: {subject}
From: {sender}
Email Type: {email_type}
Labels: {labels}
Thread ID: {thread_id}
Date: {date}
Has Attachments: {has_attachments}
Body: {truncated_body}

Provide your analysis in JSON format:
{
  "summary": "Brief summary (50 words max)",
  "category": ["primary_category", "secondary_category"],
  "priority": {
    "score": 1-5,
    "reason": "Brief justification for priority"
  },
  "action": {
    "needed": true/false,
    "type": ["reply", "task", "read", "file", "delegate"],
    "deadline": "suggested timeframe if applicable"
  },
  "key_points": [],
  "people_mentioned": [],
  "links_found": [],
  "context": {
    "project": "detected project name if any",
    "topic": "detected topic area",
    "references": "referenced emails/documents"
  },
  "sentiment": "positive/negative/neutral",
  "confidence_score": 0-1
}"""

CURRENT_RESPONSE_FORMAT = {
    "type": "object",
    "properties": {
        "summary": {"type": "string", "maxLength": 250},
        "category": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2},
        "priority": {
            "type": "object",
            "properties": {
                "score": {"type": "integer", "minimum": 1, "maximum": 5},
                "reason": {"type": "string"}
            },
            "required": ["score", "reason"]
        },
        "action": {
            "type": "object",
            "properties": {
                "needed": {"type": "boolean"},
                "type": {"type": "array", "items": {"type": "string"}},
                "deadline": {"type": "string"}
            },
            "required": ["needed", "type"]
        },
        "key_points": {"type": "array", "items": {"type": "string"}},
        "people_mentioned": {"type": "array", "items": {"type": "string"}},
        "links_found": {"type": "array", "items": {"type": "string"}},
        "context": {
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "topic": {"type": "string"},
                "references": {"type": "string"}
            }
        },
        "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
        "confidence_score": {"type": "number", "minimum": 0, "maximum": 1}
    },
    "required": ["summary", "category", "priority", "action", "sentiment", "confidence_score"]
}

PREVIOUS_RESPONSE_FORMAT = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "category": {"type": "string"},
        "priority": {"type": "integer", "minimum": 1, "maximum": 5},
        "action_needed": {"type": "boolean"},
        "key_points": {"type": "array", "items": {"type": "string"}},
        "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]}
    },
    "required": ["summary", "category", "priority", "action_needed", "sentiment"]
}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Register email analysis prompts')
    parser.add_argument('--prompt', type=str, choices=['current', 'previous', 'both'],
                       default='current', help='Which prompt version to register')
    
    args = parser.parse_args()
    
    # Initialize prompt manager
    manager = PromptManager()
    
    if args.prompt in ['previous', 'both']:
        # Register previous prompt version
        previous_id = manager.register_prompt(
            prompt_text=PREVIOUS_EMAIL_PROMPT,
            version="0.9.0",
            model_name="claude-3-haiku-20240307",
            max_tokens=1000,
            description="Basic email analysis prompt with simple JSON response format",
            expected_response_format=PREVIOUS_RESPONSE_FORMAT,
            required_input_fields=["subject", "sender", "date", "body"],
            token_estimate=500,
            script_name="test_anthropic_email.py",
            temperature=None
        )
        print(f"Registered previous prompt version 0.9.0 with ID: {previous_id}")
    
    if args.prompt in ['current', 'both']:
        # Register current prompt version
        current_id = manager.register_prompt(
            prompt_text=CURRENT_EMAIL_PROMPT,
            version="1.0.0",
            model_name="claude-3-haiku-20240307",
            max_tokens=1000,
            description="Email analysis prompt with comprehensive JSON response format",
            expected_response_format=CURRENT_RESPONSE_FORMAT,
            required_input_fields=[
                "subject", "sender", "email_type", "labels", 
                "thread_id", "date", "has_attachments", "body"
            ],
            token_estimate=800,
            script_name="test_anthropic_email.py",
            temperature=None
        )
        print(f"Registered current prompt version 1.0.0 with ID: {current_id}")
