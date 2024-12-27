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
    thread_id: Mapped[str] = Column(Text, nullable=True)  # Gmail thread ID for grouping related emails
    
    # Analysis metadata
    analysis_date: Mapped[str] = Column(Text, nullable=False)  # When the analysis was performed
    analyzed_date: Mapped[str] = Column(Text, nullable=False)  # When the email was analyzed
    prompt_version: Mapped[Optional[str]] = Column(Text, nullable=True)  # Version of the prompt used
    
    # Core analysis
    summary: Mapped[str] = Column(Text, nullable=False)  # Brief summary of the email
    _category: Mapped[str] = Column('category', Text, nullable=True)  # List of categories (serialized)
    priority_score: Mapped[int] = Column(Integer, nullable=False)  # Priority score from 1-5
    priority_reason: Mapped[str] = Column(Text, nullable=False)  # Reason for priority score
    
    # Action items
    action_needed: Mapped[bool] = Column(Boolean, nullable=False, default=False)  # Whether action is needed
    _action_type: Mapped[str] = Column('action_type', Text, nullable=True)  # List of action types (serialized)
    action_deadline: Mapped[Optional[str]] = Column(Text, nullable=True)  # When action is needed by
    
    # Extracted data
    _key_points: Mapped[str] = Column('key_points', Text, nullable=True)  # List of key points (serialized)
    _people_mentioned: Mapped[str] = Column('people_mentioned', Text, nullable=True)  # List of people (serialized)
    _links_found: Mapped[str] = Column('links_found', Text, nullable=True)  # List of links (serialized)
    _links_display: Mapped[str] = Column('links_display', Text, nullable=True)  # List of display links (serialized)
    
    # Classification
    project: Mapped[str] = Column(Text, nullable=True)  # Project name
    topic: Mapped[str] = Column(Text, nullable=True)  # Topic name
    sentiment: Mapped[str] = Column(Text, nullable=False)  # Sentiment analysis
    confidence_score: Mapped[float] = Column(Float, nullable=False)  # Analysis confidence
    
    # Raw response
    full_api_response: Mapped[str] = Column(Text, nullable=True)  # Complete API response

    # Relationships
    email = relationship("Email", back_populates="analysis")

    # List property getters and setters
    @property
    def category(self) -> List[str]:
        """Get the category list."""
        return json.loads(self._category) if self._category else []

    @category.setter
    def category(self, value: List[str]):
        """Set the category list."""
        self._category = json.dumps(value) if value else None

    @property
    def action_type(self) -> List[str]:
        """Get the action type list."""
        return json.loads(self._action_type) if self._action_type else []

    @action_type.setter
    def action_type(self, value: List[str]):
        """Set the action type list."""
        self._action_type = json.dumps(value) if value else None

    @property
    def key_points(self) -> List[str]:
        """Get the key points list."""
        return json.loads(self._key_points) if self._key_points else []

    @key_points.setter
    def key_points(self, value: List[str]):
        """Set the key points list."""
        self._key_points = json.dumps(value) if value else None

    @property
    def people_mentioned(self) -> List[str]:
        """Get the people mentioned list."""
        return json.loads(self._people_mentioned) if self._people_mentioned else []

    @people_mentioned.setter
    def people_mentioned(self, value: List[str]):
        """Set the people mentioned list."""
        self._people_mentioned = json.dumps(value) if value else None

    @property
    def links_found(self) -> List[str]:
        """Get the links found list."""
        return json.loads(self._links_found) if self._links_found else []

    @links_found.setter
    def links_found(self, value: List[str]):
        """Set the links found list."""
        self._links_found = json.dumps(value) if value else None

    @property
    def links_display(self) -> List[str]:
        """Get the links display list."""
        return json.loads(self._links_display) if self._links_display else []

    @links_display.setter
    def links_display(self, value: List[str]):
        """Set the links display list."""
        self._links_display = json.dumps(value) if value else None

    @classmethod
    def from_api_response(cls, email_id: str, thread_id: str, response: EmailAnalysisResponse, 
                         links_found: List[str] = None, links_display: List[str] = None) -> 'EmailAnalysis':
        """Create an EmailAnalysis instance from an API response."""
        return cls(
            email_id=email_id,
            thread_id=thread_id,
            analysis_date=datetime.now(UTC).isoformat(),
            prompt_version="1.0",  # TODO: Make this configurable
            summary=response.summary,
            category=response.category,
            priority_score=response.priority_score,
            priority_reason=response.priority_reason,
            action_needed=response.action_needed,
            action_type=response.action_type,
            action_deadline=response.action_deadline or '',  # Store deadline as string
            key_points=response.key_points,
            people_mentioned=response.people_mentioned,
            links_found=links_found or [],  # Use provided URLs or empty list
            links_display=links_display or [],  # Use provided display URLs or empty list
            project=response.project,
            topic=response.topic,
            sentiment=response.sentiment,
            confidence_score=response.confidence_score,
            full_api_response=response.model_dump()
        )
