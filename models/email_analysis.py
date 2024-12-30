"""Email analysis model for storing analysis results."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, relationship

from models.base import Base
from shared_lib.schema_constants import COLUMN_SIZES, AnalysisDefaults

# Default values for analysis fields
ANALYSIS_DEFAULTS = vars(AnalysisDefaults())

class EmailAnalysis(Base):
    """SQLAlchemy model for email analysis storage."""

    __tablename__ = "email_analysis"

    # Primary key is the email ID this analysis belongs to
    email_id: Mapped[str] = Column(
        String(COLUMN_SIZES["EMAIL_ID"]),
        ForeignKey("emails.id"),
        primary_key=True
    )
    
    # Analysis fields
    sentiment: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["ANALYSIS_SENTIMENT"]),
        server_default=ANALYSIS_DEFAULTS["sentiment"]
    )
    category: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["ANALYSIS_CATEGORY"]),
        server_default=ANALYSIS_DEFAULTS["category"]
    )
    summary: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["ANALYSIS_SUMMARY"])
    )
    priority: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["ANALYSIS_PRIORITY"]),
        server_default=ANALYSIS_DEFAULTS["priority"]
    )
    
    # Metadata
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    email = relationship("Email", back_populates="analysis")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<EmailAnalysis(email_id={self.email_id}, sentiment={self.sentiment}, category={self.category})>"

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "EmailAnalysis":
        """Create instance from API response."""
        # Validate and truncate fields if needed
        sentiment = response.get("sentiment", ANALYSIS_DEFAULTS["sentiment"])
        if len(sentiment) > COLUMN_SIZES["ANALYSIS_SENTIMENT"]:
            sentiment = sentiment[:COLUMN_SIZES["ANALYSIS_SENTIMENT"]]
            
        category = response.get("category", ANALYSIS_DEFAULTS["category"])
        if len(category) > COLUMN_SIZES["ANALYSIS_CATEGORY"]:
            category = category[:COLUMN_SIZES["ANALYSIS_CATEGORY"]]
            
        summary = response.get("summary")
        if summary and len(summary) > COLUMN_SIZES["ANALYSIS_SUMMARY"]:
            summary = summary[:COLUMN_SIZES["ANALYSIS_SUMMARY"]]
            
        priority = response.get("priority", ANALYSIS_DEFAULTS["priority"])
        if len(priority) > COLUMN_SIZES["ANALYSIS_PRIORITY"]:
            priority = priority[:COLUMN_SIZES["ANALYSIS_PRIORITY"]]
            
        return cls(
            email_id=response["email_id"],
            sentiment=sentiment,
            category=category,
            summary=summary,
            priority=priority
        )


@dataclass
class EmailAnalysisResponse:
    """Response model for email analysis API."""
    
    email_id: str
    sentiment: str
    category: str
    summary: str
    priority: str
    analyzed_at: datetime
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "EmailAnalysisResponse":
        """Create instance from API response."""
        return cls(
            email_id=response["email_id"],
            sentiment=response["sentiment"],
            category=response["category"],
            summary=response["summary"],
            priority=response["priority"],
            analyzed_at=datetime.fromisoformat(response["analyzed_at"])
            if isinstance(response["analyzed_at"], str)
            else response["analyzed_at"],
        )
