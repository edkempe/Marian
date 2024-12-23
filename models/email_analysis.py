"""Email analysis models."""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator
from pytz import UTC
from models.base import Base
from models.email import Email
import json
from pydantic import BaseModel, Field, model_validator

class PriorityModel(BaseModel):
    """Priority information for an email."""
    score: int = Field(..., ge=1, le=5, description="Priority score from 1-5")
    reason: str = Field(..., min_length=1, max_length=500)

class ActionModel(BaseModel):
    """Action required for an email."""
    needed: bool = False
    type: List[str] = Field(default_factory=list)
    deadline: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$|^$')

class ContextModel(BaseModel):
    """Context information for an email."""
    project: Optional[str] = ""  # Default to empty string instead of None
    topic: Optional[str] = ""    # Default to empty string instead of None

class EmailAnalysisModel(BaseModel):
    """Pydantic model for API response validation."""
    summary: str = Field(..., min_length=1, max_length=2000)
    category: List[str] = Field(..., min_items=1)
    priority_score: int = Field(..., ge=1, le=5)
    priority_reason: str = Field(..., min_length=1)
    action_needed: bool = False
    action_type: List[str] = Field(default_factory=list)
    action_deadline: Optional[str] = None
    key_points: List[str] = Field(default_factory=list)
    people_mentioned: List[str] = Field(default_factory=list)
    links_found: List[str] = Field(default_factory=list)
    links_display: List[str] = Field(default_factory=list)
    project: Optional[str] = None
    topic: Optional[str] = None
    sentiment: str = Field(..., pattern=r'^(positive|negative|neutral)$')
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class EmailAnalysis(Base):
    """SQLAlchemy model for storing email analysis data."""
    __tablename__ = 'email_analysis'
    __table_args__ = {'extend_existing': True}

    email_id = Column(Text, ForeignKey('emails.id'), primary_key=True)
    thread_id = Column(Text, nullable=False)
    analysis_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    prompt_version = Column(Text)
    summary = Column(Text)
    category = Column(JSON)  # List of categories
    priority_score = Column(Integer)
    priority_reason = Column(Text)
    action_needed = Column(Boolean)
    action_type = Column(JSON)  # List of action types
    action_deadline = Column(DateTime(timezone=True), nullable=True)
    key_points = Column(JSON)
    people_mentioned = Column(JSON)
    links_found = Column(JSON)
    links_display = Column(JSON)
    project = Column(Text, nullable=True)
    topic = Column(Text, nullable=True)
    sentiment = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    raw_analysis = Column(JSON)
    email = relationship("Email", backref="analysis")

    @classmethod
    def from_triage(cls, email_id: str, thread_id: str, triage_result: dict) -> 'EmailAnalysis':
        """Create an EmailAnalysis instance from a triage result."""
        return cls(
            email_id=email_id,
            thread_id=thread_id,
            analysis_date=datetime.now(UTC),
            prompt_version="1.0",
            summary=triage_result.get("reason", "Low priority email"),
            category=["automated", "low_priority"],
            priority_score=triage_result.get("estimated_priority", 1),
            priority_reason=triage_result.get("reason", "Automated triage"),
            action_needed=False,
            action_type=[],
            action_deadline=None,
            key_points=[],
            people_mentioned=[],
            links_found=[],
            links_display=[],
            project=None,
            topic="automated",
            sentiment="neutral",
            confidence_score=0.9,
            raw_analysis=triage_result
        )

    @classmethod
    def from_response(cls, email_id: str, thread_id: str, response: EmailAnalysisModel) -> 'EmailAnalysis':
        """Create an EmailAnalysis instance from an API response."""
        # Convert action_deadline string to datetime if present
        action_deadline = None
        if response.action_deadline:
            try:
                action_deadline = datetime.strptime(response.action_deadline, '%Y-%m-%d')
            except (ValueError, TypeError):
                action_deadline = None
                
        return cls(
            email_id=email_id,
            thread_id=thread_id,
            analysis_date=datetime.now(UTC),
            prompt_version="1.0",  # TODO: Make this configurable
            summary=response.summary,
            category=response.category,
            priority_score=response.priority_score,
            priority_reason=response.priority_reason,
            action_needed=response.action_needed,
            action_type=response.action_type,
            action_deadline=action_deadline,
            key_points=response.key_points,
            people_mentioned=response.people_mentioned,
            links_found=response.links_found,
            links_display=response.links_display,
            project=response.project,
            topic=response.topic,
            sentiment=response.sentiment,
            confidence_score=response.confidence_score,
            raw_analysis=response.model_dump()
        )
