"""SQLAlchemy model for tags table."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship, validates
from models.base import Base
from shared_lib.schema_constants import COLUMN_SIZES


class Tag(Base):
    """Model for tags based on schema.yaml configuration."""

    __tablename__ = "tags"

    # Columns
    id = Column(
        String(100),
        nullable=False, primary_key=True,
        comment="Tag ID"
    )
    name = Column(
        String(100),
        nullable=True,
        comment="Tag name"
    )
    description = Column(
        String(500),
        nullable=True,
        comment="Tag description"
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Validation methods
    @validates("name")
    def validate_name(self, key, value):
        """Validate name length."""
        if value is not None and len(value) > 100:
            raise ValueError(f"name cannot be longer than 100 characters")
        return value
    @validates("description")
    def validate_description(self, key, value):
        """Validate description length."""
        if value is not None and len(value) > 500:
            raise ValueError(f"description cannot be longer than 500 characters")
        return value

    def __init__(self, **kwargs):
        """Initialize a new tags record."""
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<Tag(id={self.id!r})>"
