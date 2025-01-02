"""SQLAlchemy model for relationships table."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship, validates
from models.base import Base
from shared_lib.schema_constants import COLUMN_SIZES


class ItemRelationship(Base):
    """Model for relationships based on schema.yaml configuration."""

    __tablename__ = "relationships"

    # Columns
    id = Column(
        String(100),
        nullable=False, primary_key=True,
        comment="Relationship ID"
    )
    source_id = Column(
        String(100),
        nullable=True,
        comment="Source item ID"
    )
    target_id = Column(
        String(100),
        nullable=True,
        comment="Target item ID"
    )
    type = Column(
        String(50),
        nullable=True, default="related",
        comment="Relationship type"
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
        """Initialize a new relationships record."""
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<ItemRelationship(id={self.id!r})>"
