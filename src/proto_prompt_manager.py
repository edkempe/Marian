#!/usr/bin/env python3
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from shared_lib.constants import DATABASE_CONFIG

# SQLAlchemy setup
Base = declarative_base()


class Prompt(Base):
    """SQLAlchemy model for prompts"""

    __tablename__ = "prompts"

    prompt_id = Column(String, primary_key=True)
    prompt_name = Column(String, nullable=False)
    prompt_text = Column(Text, nullable=False)
    version_number = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    model_name = Column(String)
    max_tokens = Column(Integer)
    description = Column(String)
    script_name = Column(String)
    purpose = Column(String)
    task = Column(String)
    expected_response_format = Column(Text)
    required_input_fields = Column(Text)
    token_estimate = Column(Integer)
    times_used = Column(Integer, default=0)
    average_confidence_score = Column(Float)
    average_response_time_ms = Column(Float)
    failure_rate = Column(Float, default=0.0)
    temperature = Column(Float)


class PromptManager:
    def __init__(self, db_path: str = DATABASE_CONFIG["PROMPTS_DB_PATH"]):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.Session = sessionmaker(bind=self.engine)
        self._ensure_tables()

    def _ensure_tables(self):
        """Ensure all necessary tables exist"""
        Base.metadata.create_all(self.engine)

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
        temperature: Optional[float] = None,
    ) -> str:
        """Register a new prompt in the database"""
        try:
            session = self.Session()

            # Generate prompt ID and name
            prompt_id = str(uuid.uuid4())
            prompt_name = f"{script_name}.{purpose}.{task}"

            # Get current version number
            current_version = (
                session.query(Prompt).filter_by(prompt_name=prompt_name).count()
            )

            # Create new prompt
            prompt = Prompt(
                prompt_id=prompt_id,
                prompt_name=prompt_name,
                prompt_text=prompt_text,
                version_number=current_version + 1,
                model_name=model_name,
                max_tokens=max_tokens,
                description=description,
                script_name=script_name,
                purpose=purpose,
                task=task,
                expected_response_format=json.dumps(expected_response_format),
                required_input_fields=json.dumps(required_input_fields),
                token_estimate=token_estimate,
                temperature=temperature,
            )

            # Mark previous versions as inactive
            session.query(Prompt).filter_by(prompt_name=prompt_name).update(
                {Prompt.active: False}
            )

            # Add new prompt
            session.add(prompt)
            session.commit()

            logging.info(
                f"Registered new prompt {prompt_name} v{prompt.version_number}"
            )
            return prompt_id

        except Exception as e:
            session.rollback()
            logging.error(f"Error registering prompt: {str(e)}")
            raise

        finally:
            session.close()

    def get_prompt(self, prompt_id: str) -> Optional[Dict]:
        """Get a prompt by ID"""
        try:
            session = self.Session()
            prompt = session.query(Prompt).filter_by(prompt_id=prompt_id).first()

            if not prompt:
                return None

            return {
                "prompt_id": prompt.prompt_id,
                "prompt_name": prompt.prompt_name,
                "prompt_text": prompt.prompt_text,
                "version_number": prompt.version_number,
                "created_date": prompt.created_date.isoformat(),
                "active": prompt.active,
                "model_name": prompt.model_name,
                "max_tokens": prompt.max_tokens,
                "description": prompt.description,
                "script_name": prompt.script_name,
                "purpose": prompt.purpose,
                "task": prompt.task,
                "expected_response_format": json.loads(prompt.expected_response_format),
                "required_input_fields": json.loads(prompt.required_input_fields),
                "token_estimate": prompt.token_estimate,
                "times_used": prompt.times_used,
                "average_confidence_score": prompt.average_confidence_score,
                "average_response_time_ms": prompt.average_response_time_ms,
                "failure_rate": prompt.failure_rate,
                "temperature": prompt.temperature,
            }

        finally:
            session.close()

    def update_metrics(
        self,
        prompt_id: str,
        confidence_score: Optional[float] = None,
        response_time_ms: Optional[float] = None,
        failed: bool = False,
    ):
        """Update usage metrics for a prompt"""
        try:
            session = self.Session()
            prompt = session.query(Prompt).filter_by(prompt_id=prompt_id).first()

            if not prompt:
                logging.error(f"Prompt {prompt_id} not found")
                return

            # Update times used
            prompt.times_used += 1

            # Update confidence score
            if confidence_score is not None:
                if prompt.average_confidence_score is None:
                    prompt.average_confidence_score = confidence_score
                else:
                    prompt.average_confidence_score = (
                        prompt.average_confidence_score * (prompt.times_used - 1)
                        + confidence_score
                    ) / prompt.times_used

            # Update response time
            if response_time_ms is not None:
                if prompt.average_response_time_ms is None:
                    prompt.average_response_time_ms = response_time_ms
                else:
                    prompt.average_response_time_ms = (
                        prompt.average_response_time_ms * (prompt.times_used - 1)
                        + response_time_ms
                    ) / prompt.times_used

            # Update failure rate
            if failed:
                if prompt.failure_rate is None:
                    prompt.failure_rate = 1.0
                else:
                    prompt.failure_rate = (
                        prompt.failure_rate * (prompt.times_used - 1) + 1.0
                    ) / prompt.times_used

            session.commit()

        except Exception as e:
            session.rollback()
            logging.error(f"Error updating metrics: {str(e)}")

        finally:
            session.close()


def register_test_prompts():
    """Register test prompts for development"""
    manager = PromptManager()

    # Test prompt 1: Email summarization
    manager.register_prompt(
        prompt_text="""
        Analyze the following email and provide a concise summary.

        Email: {{email_text}}

        Please provide:
        1. A brief summary (2-3 sentences)
        2. Key points or action items
        3. Priority level (1-5) with explanation
        4. Sentiment (positive/negative/neutral)
        """,
        model_name="gpt-4",
        max_tokens=500,
        description="Analyze and summarize email content",
        expected_response_format={
            "summary": "string",
            "key_points": ["string"],
            "priority": {"level": "integer", "explanation": "string"},
            "sentiment": "string",
        },
        required_input_fields=["email_text"],
        token_estimate=200,
        script_name="email_analysis",
        purpose="summarize",
        task="basic",
        temperature=0.3,
    )

    # Test prompt 2: Project categorization
    manager.register_prompt(
        prompt_text="""
        Analyze the following project description and categorize it.

        Project: {{project_description}}

        Please provide:
        1. Primary category
        2. Subcategories (if applicable)
        3. Estimated complexity (1-5)
        4. Required skills
        """,
        model_name="gpt-4",
        max_tokens=300,
        description="Categorize and analyze project descriptions",
        expected_response_format={
            "primary_category": "string",
            "subcategories": ["string"],
            "complexity": "integer",
            "required_skills": ["string"],
        },
        required_input_fields=["project_description"],
        token_estimate=150,
        script_name="project_analysis",
        purpose="categorize",
        task="basic",
        temperature=0.2,
    )


if __name__ == "__main__":
    register_test_prompts()
