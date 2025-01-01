"""Email analysis model definitions."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from sqlalchemy import Column, DateTime, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class EmailAnalysis(Base):
    """Email analysis model."""
    
    __tablename__ = "email_analyses"
    
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey("email_messages.id"), nullable=False)
    sentiment = Column(String)
    categories = Column(JSON)  # List of categories
    summary = Column(String)
    key_points = Column(JSON)  # List of key points
    action_items = Column(JSON)  # List of action items
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    email = relationship("EmailMessage", back_populates="analysis")
    
    def __repr__(self) -> str:
        """Get string representation."""
        return f"<EmailAnalysis(id={self.id}, email_id={self.email_id})>"


@dataclass
class EmailAnalysisResponse:
    """Response model for email analysis API."""
    
    email_id: str
    sentiment: str
    categories: List[str]
    summary: str
    key_points: List[str]
    action_items: List[str]
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "EmailAnalysisResponse":
        """Create instance from API response."""
        return cls(
            email_id=response["email_id"],
            sentiment=response.get("sentiment", ""),
            categories=response.get("categories", []),
            summary=response.get("summary", ""),
            key_points=response.get("key_points", []),
            action_items=response.get("action_items", [])
        )
