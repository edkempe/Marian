"""SQLAlchemy model for analysis table."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship, validates
from models.base import Base
from shared_lib.schema_constants import COLUMN_SIZES


class EmailAnalysis(Base):
    """Model for analysis based on schema.yaml configuration."""

    __tablename__ = "analysis"

    # Columns
    id = Column(
        String(100),
        nullable=False, primary_key=True,
        comment="Analysis ID"
    )
    email_id = Column(
        String(100),
        nullable=False,
        comment="Email ID reference"
    )
    summary = Column(
        String(1000),
        nullable=True,
        comment="Email summary"
    )
    sentiment = Column(
        String(20),
        nullable=True, default="neutral",
        comment="Sentiment analysis"
    )
    categories = Column(
        JSON,
        nullable=True, default="[]",
        comment="Categories as JSON array"
    )
    key_points = Column(
        JSON,
        nullable=True, default="[]",
        comment="Key points as JSON array"
    )
    action_items = Column(
        JSON,
        nullable=True, default="[]",
        comment="Action items as JSON array"
    )
    priority_score = Column(
        Integer,
        nullable=True,
        comment="Priority score (1-5)"
    )
    confidence_score = Column(
        Float,
        nullable=True,
        comment="Confidence score (0-1)"
    )
    analysis_metadata = Column(
        JSON,
        nullable=True, default="{}",
        comment="Analysis metadata as JSON"
    )
    model_version = Column(
        String(50),
        nullable=True,
        comment="Model version used for analysis"
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Validation methods

    def __init__(self, **kwargs):
        """Initialize a new analysis record."""
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<EmailAnalysis(id={self.id!r})>"
