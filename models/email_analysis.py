"""Email analysis models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship

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
    
    This model stores the analyzed data from emails, including:
    - Email identification (email_id, thread_id)
    - Analysis metadata (date, prompt version)
    - Content analysis (summary, categories, priority)
    - Action items and deadlines
    - Key information (points, people, URLs)
    - Classification (project, topic, sentiment)
    - Raw API response for debugging
    """
    __tablename__ = 'email_analysis'

    email_id = Column(Text, ForeignKey('emails.id'), primary_key=True)  # References emails.id
    thread_id = Column(Text, nullable=False)  # Gmail thread ID for grouping related emails
    analysis_date = Column(DateTime, default=datetime.utcnow)
    prompt_version = Column(Text)
    summary = Column(Text)
    category = Column(JSON)  # List of categories
    priority_score = Column(Integer)
    priority_reason = Column(Text)
    action_needed = Column(Boolean, default=False)
    action_type = Column(JSON)  # List of action types
    action_deadline = Column(Text)  # Optional YYYY-MM-DD
    key_points = Column(JSON)  # List of key points
    people_mentioned = Column(JSON)  # List of people
    links_found = Column(JSON)  # List of full URLs
    links_display = Column(JSON)  # List of truncated URLs
    project = Column(Text)
    topic = Column(Text)
    sentiment = Column(Text)
    confidence_score = Column(Float)
    raw_analysis = Column(JSON)  # Full API response
    email = relationship("Email", backref="analysis")

    @classmethod
    def from_response(cls, email_id: str, thread_id: str, response: EmailAnalysisResponse) -> 'EmailAnalysis':
        """Create an EmailAnalysis instance from an API response."""
        return cls(
            email_id=email_id,
            thread_id=thread_id,
            analysis_date=datetime.utcnow(),
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
            raw_analysis=response.dict()
        )
