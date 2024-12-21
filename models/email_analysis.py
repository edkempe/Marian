"""Email analysis models."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from pydantic import BaseModel, Field, model_validator
from model_base import Base
import json

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
    ref_docs: Optional[str] = "" # Default to empty string instead of None

class EmailAnalysisResponse(BaseModel):
    """Pydantic model for API response validation."""
    summary: str = Field(..., min_length=1, description="Brief summary of the email")
    category: List[str]
    priority: PriorityModel
    action: ActionModel
    key_points: List[str]
    people_mentioned: List[str]
    links_found: List[str]
    links_display: List[str]
    context: ContextModel
    sentiment: str = Field(..., pattern="^(positive|negative|neutral)$")
    confidence_score: float = Field(default=0.9, ge=0.0, le=1.0)

    @model_validator(mode='before')
    @classmethod
    def validate_urls(cls, data):
        """Validate URLs."""
        if not isinstance(data, dict):
            return data
        
        if 'links_found' in data:
            data['links_found'] = [
                url[:100] + '...' if len(url) > 100 else url
                for url in data['links_found']
            ]
        return data

class EmailAnalysis(Base):
    """SQLAlchemy model for email analysis storage."""
    __tablename__ = 'email_analysis'

    email_id = Column(String, primary_key=True)  # References emails.id
    analysis_date = Column(DateTime, default=datetime.utcnow)
    analyzed_date = Column(DateTime, nullable=False)  # Date when email was analyzed
    prompt_version = Column(String(50), nullable=False)  # Version of prompt used for analysis
    summary = Column(String, nullable=False)
    category = Column(String, nullable=False)  # JSON string
    priority_score = Column(Integer, nullable=False)
    priority_reason = Column(String, nullable=False)
    action_needed = Column(Boolean, nullable=False, default=False)
    action_type = Column(String, nullable=False)  # JSON string
    action_deadline = Column(String)
    key_points = Column(String, nullable=False)  # JSON string
    people_mentioned = Column(String, nullable=False)  # JSON string
    links_found = Column(String, nullable=False)  # JSON string
    links_display = Column(String, nullable=False)  # JSON string
    project = Column(String)
    topic = Column(String)
    ref_docs = Column(String)
    sentiment = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    raw_analysis = Column(String, nullable=False)  # JSON string

    @classmethod
    def from_response(cls, email_id: str, response: EmailAnalysisResponse) -> 'EmailAnalysis':
        """Create an EmailAnalysis instance from an API response."""
        return cls(
            email_id=email_id,
            analysis_date=datetime.utcnow(),
            analyzed_date=datetime.utcnow(),
            prompt_version="",
            summary=response.summary,
            category=json.dumps(response.category),  # Convert to JSON string for SQLite
            priority_score=response.priority.score,
            priority_reason=response.priority.reason,
            action_needed=response.action.needed,
            action_type=json.dumps(response.action.type),  # Convert to JSON string for SQLite
            action_deadline=response.action.deadline,
            key_points=json.dumps(response.key_points),  # Convert to JSON string for SQLite
            people_mentioned=json.dumps(response.people_mentioned),  # Convert to JSON string for SQLite
            links_found=json.dumps(response.links_found),  # Convert to JSON string for SQLite
            links_display=json.dumps(response.links_display),  # Convert to JSON string for SQLite
            project=response.context.project,
            topic=response.context.topic,
            ref_docs=response.context.ref_docs,
            sentiment=response.sentiment,
            confidence_score=response.confidence_score,
            raw_analysis=json.dumps(response.model_dump())  # Convert to JSON string for SQLite
        )
