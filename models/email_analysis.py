"""SQLAlchemy model for analysis table."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, Table
from sqlalchemy.orm import relationship, validates
from models.base import Base
from shared_lib.schema_constants import COLUMN_SIZES


class EmailAnalysis(Base):
    """Model based on schema.yaml configuration."""

    __tablename__ = "email_analysis"

    # Table configuration
    __table_args__ = {"extend_existing": True}

    # Database configuration
    __database__ = "main"  # Default to catalog if not specified

    # Columns
    id = Column(
        String(100),
        nullable=False,
        primary_key=True,
        comment="Analysis ID"
    )

    email_id = Column(
        String(100),
        nullable=False,
        comment="Email ID reference"
    )

    summary = Column(
        String(1000),
        comment="Email summary"
    )

    sentiment = Column(
        String(20),
        comment="Sentiment analysis"
    )

    categories = Column(
        JSON,
        comment="Categories as JSON array"
    )

    key_points = Column(
        JSON,
        comment="Key points as JSON array"
    )

    action_items = Column(
        JSON,
        comment="Action items as JSON array"
    )

    priority_score = Column(
        Integer,
        comment="Priority score (1-5)"
    )

    confidence_score = Column(
        Float,
        comment="Confidence score (0-1)"
    )

    analysis_metadata = Column(
        JSON,
        comment="Analysis metadata as JSON"
    )

    model_version = Column(
        String(50),
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
        """Initialize a new record."""
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<EmailAnalysis(id={self.id!r})>"