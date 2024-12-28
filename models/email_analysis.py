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

# Constants used in this model
ANALYSIS_VALIDATION = {
    'PRIORITY_SCORE': {'MIN': 1, 'MAX': 5},
    'TEXT_LENGTH': {'MIN': 1, 'MAX': 10000},
    'CONFIDENCE_SCORE': {'MIN': 0.0, 'MAX': 1.0}
}

ANALYSIS_DEFAULTS = {
    'ACTION_NEEDED': False,
    'EMPTY_STRING': '',
    'CONFIDENCE_SCORE': 0.8
}

ANALYSIS_SENTIMENT_TYPES = {
    'POSITIVE': 'positive',
    'NEGATIVE': 'negative',
    'NEUTRAL': 'neutral'
}

ANALYSIS_DATE_PATTERNS = {
    'ISO_DATE_OR_EMPTY': r'^(\d{4}-\d{2}-\d{2})?$',
    'ISO_DATE_OR_EMPTY_OR_ASAP': r'^(\d{4}-\d{2}-\d{2}|ASAP)?$'
}

class PriorityModel(BaseModel):
    """Priority information for an email."""
    score: int = Field(..., ge=ANALYSIS_VALIDATION['PRIORITY_SCORE']['MIN'], le=ANALYSIS_VALIDATION['PRIORITY_SCORE']['MAX'], 
                      description="Priority score from 1-5")
    reason: str = Field(..., min_length=ANALYSIS_VALIDATION['TEXT_LENGTH']['MIN'], 
                       max_length=ANALYSIS_VALIDATION['TEXT_LENGTH']['MAX'])

class ActionModel(BaseModel):
    """Action required for an email."""
    needed: bool = ANALYSIS_DEFAULTS['ACTION_NEEDED']
    type: List[str] = Field(default_factory=list)
    deadline: Optional[str] = Field(None, pattern=ANALYSIS_DATE_PATTERNS['ISO_DATE_OR_EMPTY'])

class ContextModel(BaseModel):
    """Context information for an email."""
    project: Optional[str] = ANALYSIS_DEFAULTS['EMPTY_STRING']
    topic: Optional[str] = ANALYSIS_DEFAULTS['EMPTY_STRING']

class EmailAnalysisResponse(BaseModel):
    """Pydantic model for API response validation."""
    summary: str = Field(..., min_length=ANALYSIS_VALIDATION['TEXT_LENGTH']['MIN'], 
                        description="Brief summary of the email")
    category: List[str] = Field(default_factory=list)
    priority_score: int = Field(..., ge=ANALYSIS_VALIDATION['PRIORITY_SCORE']['MIN'], 
                              le=ANALYSIS_VALIDATION['PRIORITY_SCORE']['MAX'], 
                              description="Priority score from 1-5")
    priority_reason: str = Field(..., min_length=ANALYSIS_VALIDATION['TEXT_LENGTH']['MIN'], 
                               max_length=ANALYSIS_VALIDATION['TEXT_LENGTH']['MAX'])
    action_needed: bool = Field(default=ANALYSIS_DEFAULTS['ACTION_NEEDED'])
    action_type: List[str] = Field(default_factory=list)  
    action_deadline: Optional[str] = Field(None, pattern=ANALYSIS_DATE_PATTERNS['ISO_DATE_OR_EMPTY_OR_ASAP'])
    key_points: List[str] = Field(default_factory=list)
    people_mentioned: List[str] = Field(default_factory=list)
    project: str = Field(default=ANALYSIS_DEFAULTS['EMPTY_STRING'])
    topic: str = Field(default=ANALYSIS_DEFAULTS['EMPTY_STRING'])
    sentiment: str = Field(..., pattern=f"^({'|'.join(ANALYSIS_SENTIMENT_TYPES.values())})$")
    confidence_score: float = Field(default=ANALYSIS_DEFAULTS['CONFIDENCE_SCORE'], 
                                  ge=ANALYSIS_VALIDATION['CONFIDENCE_SCORE']['MIN'], 
                                  le=ANALYSIS_VALIDATION['CONFIDENCE_SCORE']['MAX'])

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

    email_id = Column(Integer, ForeignKey('emails.id'), primary_key=True)
    analysis_date = Column(DateTime, nullable=True)
    analyzed_date = Column(DateTime, nullable=False)
    prompt_version = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    priority_score = Column(Integer, nullable=False)
    priority_reason = Column(Text, nullable=False)
    action_needed = Column(Boolean, nullable=False, default=ANALYSIS_DEFAULTS['ACTION_NEEDED'])
    action_type = Column(Text, nullable=False)
    action_deadline = Column(Text, nullable=True)
    key_points = Column(Text, nullable=False)
    people_mentioned = Column(Text, nullable=False)
    links_found = Column(Text, nullable=False)
    links_display = Column(Text, nullable=False)
    project = Column(Text, nullable=True)
    topic = Column(Text, nullable=True)
    ref_docs = Column(Text, nullable=True)
    sentiment = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)

    email = relationship("Email", back_populates="analysis")

    @classmethod
    def from_api_response(cls, email_id: str, thread_id: str, response: EmailAnalysisResponse, 
                         links_found: List[str] = None, links_display: List[str] = None) -> 'EmailAnalysis':
        """Create an EmailAnalysis instance from an API response."""
        now = datetime.now(UTC)
        
        return cls(
            email_id=email_id,
            analysis_date=now,
            analyzed_date=now,
            prompt_version="1.0",  # TODO: Make configurable
            summary=response.summary,
            category=json.dumps(response.category),
            priority_score=response.priority_score,
            priority_reason=response.priority_reason,
            action_needed=response.action_needed,
            action_type=json.dumps(response.action_type),
            action_deadline=response.action_deadline,
            key_points=json.dumps(response.key_points),
            people_mentioned=json.dumps(response.people_mentioned),
            links_found=json.dumps(links_found or []),
            links_display=json.dumps(links_display or []),
            project=response.project,
            topic=response.topic,
            sentiment=response.sentiment,
            confidence_score=response.confidence_score
        )
