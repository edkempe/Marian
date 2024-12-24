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
    category: List[str]
    priority_score: int = Field(..., ge=1, le=5, description="Priority score from 1-5")
    priority_reason: str = Field(..., min_length=1, max_length=500)
    action_needed: bool = Field(default=False)
    action_type: List[str] = Field(default_factory=list)
    action_deadline: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$|^$')
    key_points: List[str]
    people_mentioned: List[str]
    links_found: List[str]  # Full URLs
    links_display: List[str]  # Truncated URLs for display
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
            return data
        
        if 'links_found' in data:
            # Ensure links_found is a list
            if not isinstance(data['links_found'], list):
                data['links_found'] = []
            
            # Convert all URLs to strings and store full versions
            data['links_found'] = [str(url).strip() for url in data['links_found']]
            
            # Create truncated versions for display
            data['links_display'] = []
            for url in data['links_found']:
                if len(url) > 100:
                    # Keep the first 97 chars and add ...
                    truncated = url[:97] + '...'
                    data['links_display'].append(truncated)
                else:
                    data['links_display'].append(url)
        else:
            # Initialize empty lists if no links found
            data['links_found'] = []
            data['links_display'] = []
            
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
    category: Mapped[Dict] = Column(JSON)  # List of categories
    priority_score: Mapped[int] = Column(Integer)  # Priority score (1-5)
    priority_reason: Mapped[str] = Column(Text)  # Explanation for priority score
    
    # Action items
    action_needed: Mapped[bool] = Column(Boolean)  # Whether action is required
    action_type: Mapped[List] = Column(JSON)  # List of action types
    action_deadline: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)  # When action is needed by
    
    # Key information
    key_points: Mapped[List] = Column(JSON)  # List of key points from email
    people_mentioned: Mapped[List] = Column(JSON)  # List of people mentioned
    links_found: Mapped[List] = Column(JSON)  # List of links found in the email
    links_display: Mapped[List] = Column(JSON)  # List of display text for links
    
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
    def from_api_response(cls, email_id: str, thread_id: str, response: EmailAnalysisResponse) -> 'EmailAnalysis':
        """Create an EmailAnalysis instance from an API response."""
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
            action_deadline=response.action_deadline,
            key_points=response.key_points,
            people_mentioned=response.people_mentioned,
            links_found=response.links_found,
            links_display=response.links_display,
            project=response.project,
            topic=response.topic,
            sentiment=response.sentiment,
            confidence_score=response.confidence_score,
            full_api_response=response.model_dump()
        )
