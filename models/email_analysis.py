"""Email analysis models."""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator
from pytz import UTC
from models.base import Base
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

class EmailAnalysisResponse(BaseModel):
    """Pydantic model for API response validation."""
    summary: str = Field(..., min_length=1, description="Brief summary of the email")
    category: List[str] = Field(default_factory=list)
    priority_score: int = Field(..., ge=1, le=5, description="Priority score from 1-5")
    priority_reason: str = Field(..., min_length=1, max_length=500)
    action_needed: bool = Field(default=False)
    action_type: List[str] = Field(default_factory=list)  
    action_deadline: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$|^$|^ASAP$')
    key_points: List[str] = Field(default_factory=list)
    people_mentioned: List[str] = Field(default_factory=list)
    project: str = Field(default="")
    topic: str = Field(default="")
    sentiment: str = Field(..., pattern="^(positive|negative|neutral)$")
    confidence_score: float = Field(default=0.9, ge=0.0, le=1.0)

    @model_validator(mode='before')
    @classmethod
    def validate_urls(cls, data):
        """Validate and process URLs.
        
        - Ensures links_found contains complete URLs
        - Creates truncated versions in links_display for UI
        - Validates URLs are strings
        """
        if not isinstance(data, dict):
            return {}
        
        # Remove links fields if present - they're handled by EmailAnalyzer now
        if 'links_found' in data:
            del data['links_found']
        if 'links_display' in data:
            del data['links_display']
            
        # Ensure action_type is never None
        if 'action_type' not in data or data['action_type'] is None:
            data['action_type'] = []
            
        return data

class EmailAnalysis(Base):
    """SQLAlchemy model for storing email analysis data.
    
    Maps to the 'email_analysis' table in the database. This model stores analysis data
    for each email, including:
    - Email identification (email_id, thread_id)
    - Analysis metadata (dates, prompt version)
    - Core analysis (summary, category, priority)
    - Action items (needed, type, deadline)
    - Extracted data (key points, people, links)
    - Classification (project, topic, sentiment)
    - Analysis quality (confidence score)
    - full_api_response: Complete analysis response
    
    Note: This model is the source of truth for the database schema.
    Any changes should be made here first, then migrated to the database.
    """
    __tablename__ = 'email_analysis'
    __table_args__ = {'extend_existing': True}

    # Email identification
    email_id: Mapped[str] = Column(Text, ForeignKey('emails.id'), primary_key=True)  # References emails.id
    thread_id: Mapped[str] = Column(Text, nullable=False)  # Gmail thread ID for grouping related emails
    
    # Analysis metadata
    analysis_date: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    analyzed_date: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  # When analysis was performed
    prompt_version: Mapped[str] = Column(Text)  # Version of the prompt used for analysis
    
    # Content analysis
    summary: Mapped[str] = Column(Text)  # Brief summary of the email
    category: Mapped[str] = Column(Text)  # List of categories as comma-separated string
    priority_score: Mapped[int] = Column(Integer)  # Priority score (1-5)
    priority_reason: Mapped[str] = Column(Text)  # Explanation for priority score
    
    # Action items
    action_needed: Mapped[bool] = Column(Boolean)  # Whether action is required
    action_type: Mapped[str] = Column(Text)  # List of action types as comma-separated string
    action_deadline: Mapped[Optional[str]] = Column(Text, nullable=True)  # When action is needed by
    
    # Key information
    key_points: Mapped[str] = Column(Text)  # List of key points as comma-separated string
    people_mentioned: Mapped[str] = Column(Text)  # List of people as comma-separated string
    links_found: Mapped[str] = Column(Text)  # List of links as comma-separated string
    links_display: Mapped[str] = Column(Text)  # List of display text as comma-separated string
    
    # Classification
    project: Mapped[Optional[str]] = Column(Text, nullable=True)  # Project name if email is project-related
    topic: Mapped[Optional[str]] = Column(Text, nullable=True)  # Topic classification
    sentiment: Mapped[Optional[str]] = Column(Text, nullable=True)  # Sentiment analysis
    confidence_score: Mapped[Optional[float]] = Column(Float, nullable=True)  # Confidence score of the analysis
    
    # Raw data
    full_api_response: Mapped[Dict] = Column(JSON)  # Full API response for debugging
    
    # Relationships
    email = relationship("models.email.Email", backref="analysis", foreign_keys=[email_id])

    @classmethod
    def from_api_response(cls, email_id: str, thread_id: str, response: EmailAnalysisResponse, 
                         links_found: List[str] = None, links_display: List[str] = None) -> 'EmailAnalysis':
        """Create an EmailAnalysis instance from an API response."""
        return cls(
            email_id=email_id,
            thread_id=thread_id,
            analysis_date=datetime.now(UTC),
            prompt_version="1.0",  # TODO: Make this configurable
            summary=response.summary,
            category=','.join(response.category),
            priority_score=response.priority_score,
            priority_reason=response.priority_reason,
            action_needed=response.action_needed,
            action_type=','.join(response.action_type) if response.action_type else '',
            action_deadline=response.action_deadline or '',  # Store deadline as string
            key_points=','.join(response.key_points),
            people_mentioned=','.join(response.people_mentioned),
            links_found=','.join(links_found or []),  # Use provided URLs or empty list
            links_display=','.join(links_display or []),  # Use provided display URLs or empty list
            project=response.project,
            topic=response.topic,
            sentiment=response.sentiment,
            confidence_score=response.confidence_score,
            full_api_response=response.model_dump()
        )
