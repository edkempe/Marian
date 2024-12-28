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
    """SQLAlchemy model for email analysis results."""
    __tablename__ = 'email_analysis'
    
    id = Column(Integer, primary_key=True)
    email_id = Column(String(100), ForeignKey('emails.id'), unique=True, nullable=False)
    thread_id = Column(String(100))
    summary = Column(String(500))
    category = Column(String(100))
    priority_score = Column(Integer)
    priority_reason = Column(String(200))
    action_needed = Column(Boolean)
    action_type = Column(String(100))
    key_points = Column(String(500))  # Stored as JSON
    sentiment = Column(String(20))
    links_found = Column(String(1000))  # Stored as JSON
    links_display = Column(String(1000))  # Stored as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    email = relationship("Email", back_populates="analysis")

    @classmethod
    def from_api_response(cls, email_id: str, thread_id: str, response: EmailAnalysisResponse, 
                         links_found: List[str] = None, links_display: List[str] = None) -> 'EmailAnalysis':
        """Create an EmailAnalysis instance from an API response."""
        now = datetime.utcnow()
        
        return cls(
            email_id=email_id,
            thread_id=thread_id,
            summary=response.summary,
            category=json.dumps(response.category),
            priority_score=response.priority_score,
            priority_reason=response.priority_reason,
            action_needed=response.action_needed,
            action_type=json.dumps(response.action_type),
            key_points=json.dumps(response.key_points),
            sentiment=response.sentiment,
            links_found=json.dumps(links_found or []),
            links_display=json.dumps(links_display or []),
            created_at=now,
            updated_at=now
        )
