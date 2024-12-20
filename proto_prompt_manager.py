#!/usr/bin/env python3
import sqlite3
import json
import uuid
import logging
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
        # Create tables if they don't exist
        with open('schema/prompt_tracking.sql', 'r') as f:
            schema = f.read()
            # Remove any DROP statements
            schema = '\n'.join(line for line in schema.split('\n') 
                             if not line.strip().lower().startswith('drop'))
            self.conn.executescript(schema)
        self.conn.commit()

    def register_prompt(
        self,
        prompt_text: str,
        model_name: str,
        max_tokens: int,
        description: str,
        expected_response_format: Dict,
        required_input_fields: List[str],
        token_estimate: int,
        script_name: str,
        purpose: str,
        task: str,
        temperature: Optional[float] = None
    ) -> str:
        """Register a new prompt in the database"""
        try:
            prompt_id = str(uuid.uuid4())
            
            # Generate prompt name
            prompt_name = f"{script_name}.{purpose}.{task}"
            
            # Convert JSON fields to strings
            expected_response_format_str = json.dumps(expected_response_format)
            required_input_fields_str = json.dumps(required_input_fields)
            
            # Debug log
            logging.info(f"Registering prompt: {prompt_name}")
            logging.info(f"Script: {script_name}, Purpose: {purpose}, Task: {task}")
            
            # Deactivate any existing prompts for this script/purpose/task
            self.conn.execute('''
                UPDATE prompts
                SET active = 0
                WHERE script_name = ?
                AND purpose = ?
                AND task = ?
            ''', (script_name, purpose, task))
            
            # Insert new prompt
            self.conn.execute('''
                INSERT INTO prompts (
                    prompt_id, prompt_name, prompt_text,
                    created_date, active, model_name, max_tokens,
                    temperature, description, script_name, purpose,
                    task, expected_response_format, required_input_fields,
                    token_estimate
                ) VALUES (
                    ?, ?, ?, CURRENT_TIMESTAMP, 1, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                prompt_id, prompt_name, prompt_text,
                model_name, max_tokens, temperature, description,
                script_name, purpose, task, expected_response_format_str,
                required_input_fields_str, token_estimate
            ))
            
            self.conn.commit()
            return prompt_id
            
        except sqlite3.Error as e:
            logging.error(f"Database error in register_prompt: {str(e)}")
            self.conn.rollback()
            raise
        except Exception as e:
            logging.error(f"Error in register_prompt: {str(e)}")
            self.conn.rollback()
            raise

    def get_active_prompt(self, script_name: str, purpose: str, task: str) -> Optional[Dict]:
        """Get the active prompt for a specific purpose within a script"""
        try:
            # Debug log
            logging.info(f"Getting active prompt for: {script_name}.{purpose}.{task}")
            
            cursor = self.conn.execute('''
                SELECT *
                FROM prompts
                WHERE script_name = ?
                AND purpose = ?
                AND task = ?
                AND active = 1
                ORDER BY created_date DESC
                LIMIT 1
            ''', (script_name, purpose, task))
            
            row = cursor.fetchone()
            if row:
                prompt_data = dict(row)
                # Parse JSON fields
                prompt_data['expected_response_format'] = json.loads(prompt_data['expected_response_format'])
                prompt_data['required_input_fields'] = json.loads(prompt_data['required_input_fields'])
                logging.info(f"Found active prompt: {prompt_data['prompt_name']}")
                return prompt_data
                
            logging.warning(f"No active prompt found for {script_name}.{purpose}.{task}")
            return None
            
        except sqlite3.Error as e:
            logging.error(f"Database error: {str(e)}")
            return None

    def log_prompt_call(self, prompt_id: str, input_data: Dict, raw_prompt: str,
                       response: Optional[str], response_time_ms: int,
                       confidence_score: float, success: bool,
                       error_message: Optional[str] = None) -> str:
        """Log an individual prompt API call"""
        call_id = str(uuid.uuid4())
        
        # Get prompt details
        cursor = self.conn.execute('SELECT prompt_name, script_name, purpose, task FROM prompts WHERE prompt_id = ?', 
                                 (prompt_id,))
        prompt_info = cursor.fetchone()
        
        self.conn.execute('''
            INSERT INTO prompt_calls (
                call_id, prompt_id, prompt_name, script_name, purpose, task,
                input_data, raw_prompt, response, response_time_ms,
                confidence_score, success, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            call_id, prompt_id, prompt_info['prompt_name'], 
            prompt_info['script_name'], prompt_info['purpose'], 
            prompt_info['task'], json.dumps(input_data), raw_prompt,
            response, response_time_ms, confidence_score,
            1 if success else 0, error_message
        ))
        self.conn.commit()
        return call_id

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
            ORDER BY created_date DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def __del__(self):
        self.conn.close()

def register_test_prompts():
    """Register test prompts for development"""
    prompt_manager = PromptManager()
    
    # Previous version prompt
    previous_prompt = """
    You are an AI assistant analyzing an email. Based on the email content, provide a structured analysis in JSON format.
    
    Email details:
    Subject: {subject}
    Sender: {sender}
    Type: {email_type}
    Labels: {labels}
    Thread ID: {thread_id}
    Date: {date}
    Has Attachments: {has_attachments}
    
    Email Body:
    {truncated_body}
    
    Provide your analysis in the following JSON format:
    {
        "priority": "high|medium|low",
        "category": "string",
        "requires_response": true|false,
        "suggested_action": "string",
        "confidence_score": float between 0-1,
        "key_points": ["string"],
        "sentiment": "positive|neutral|negative"
    }
    """
    
    previous_id = prompt_manager.register_prompt(
        prompt_text=previous_prompt,
        model_name="claude-2.1",
        max_tokens=1000,
        description="Basic email analysis prompt",
        expected_response_format={
            "type": "object",
            "properties": {
                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                "category": {"type": "string"},
                "requires_response": {"type": "boolean"},
                "suggested_action": {"type": "string"},
                "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                "key_points": {"type": "array", "items": {"type": "string"}},
                "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]}
            }
        },
        required_input_fields=["subject", "sender", "date", "body"],
        token_estimate=500,
        script_name="test_anthropic_email",
        purpose="email",
        task="analysis",
        temperature=None
    )
    print(f"Registered previous prompt with ID: {previous_id}")
    
    # Current version prompt with enhanced analysis
    current_prompt = """
    You are an AI assistant performing detailed email analysis. Based on the email content, provide a comprehensive structured analysis in JSON format.
    
    Email details:
    Subject: {subject}
    Sender: {sender}
    Type: {email_type}
    Labels: {labels}
    Thread ID: {thread_id}
    Date: {date}
    Has Attachments: {has_attachments}
    
    Email Body:
    {truncated_body}
    
    Provide your analysis in the following JSON format:
    {
        "priority": "high|medium|low",
        "category": "string",
        "requires_response": true|false,
        "response_deadline": "YYYY-MM-DD|null",
        "suggested_action": "string",
        "confidence_score": float between 0-1,
        "key_points": ["string"],
        "entities": ["string"],
        "sentiment": "positive|neutral|negative",
        "topics": ["string"],
        "next_steps": ["string"]
    }
    """
    
    current_id = prompt_manager.register_prompt(
        prompt_text=current_prompt,
        model_name="claude-2.1",
        max_tokens=1500,
        description="Enhanced email analysis prompt with additional fields",
        expected_response_format={
            "type": "object",
            "properties": {
                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                "category": {"type": "string"},
                "requires_response": {"type": "boolean"},
                "response_deadline": {"type": "string", "format": "date-time"},
                "suggested_action": {"type": "string"},
                "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                "key_points": {"type": "array", "items": {"type": "string"}},
                "entities": {"type": "array", "items": {"type": "string"}},
                "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
                "topics": {"type": "array", "items": {"type": "string"}},
                "next_steps": {"type": "array", "items": {"type": "string"}}
            }
        },
        required_input_fields=[
            "subject", "sender", "email_type", "labels",
            "thread_id", "date", "has_attachments", "body"
        ],
        token_estimate=800,
        script_name="test_anthropic_email",
        purpose="email",
        task="analysis",
        temperature=None
    )
    print(f"Registered current prompt with ID: {current_id}")

if __name__ == "__main__":
    register_test_prompts()
