"""Email analysis model for storing analysis results."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, relationship

from models.base import Base
from shared_lib.config_loader import get_schema_config

# Get schema configuration
config = get_schema_config().analysis


class EmailAnalysis(Base):
    """SQLAlchemy model for email analysis storage."""

    __tablename__ = "email_analysis"

    # Primary key is the email ID this analysis belongs to
    email_id: Mapped[str] = Column(String(100), ForeignKey("emails.id"), primary_key=True)
    
    # Analysis fields
    sentiment: Mapped[Optional[str]] = Column(
        String(config.columns["sentiment"].size),
        server_default=config.defaults.sentiment
    )
    category: Mapped[Optional[str]] = Column(
        String(config.columns["category"].size),
        server_default=config.defaults.category
    )
    summary: Mapped[Optional[str]] = Column(
        String(config.columns["summary"].size)
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
        return f"<EmailAnalysis(email_id={self.email_id}, sentiment={self.sentiment})>"

    @classmethod
    def from_api_response(cls, email_id: str, response: dict) -> "EmailAnalysis":
        """Create an EmailAnalysis instance from API response.

        Args:
            email_id: ID of the email this analysis belongs to
            response: Dictionary containing analysis results

        Returns:
            EmailAnalysis instance
        """
        # Validate sentiment
        sentiment = response.get("sentiment", config.defaults.sentiment)
        if sentiment not in config.validation.valid_sentiments:
            sentiment = config.defaults.sentiment

        # Validate and truncate summary if needed
        summary = response.get("summary", "")
        if len(summary) > config.validation.max_summary_length:
            summary = summary[:config.validation.max_summary_length]

        return cls(
            email_id=email_id,
            sentiment=sentiment,
            category=response.get("category", config.defaults.category),
            summary=summary
        )
