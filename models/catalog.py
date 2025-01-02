"""SQLAlchemy model for catalog table."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship, validates
from models.base import Base
from shared_lib.schema_constants import COLUMN_SIZES


class CatalogItem(Base):
    """Model for catalog based on schema.yaml configuration."""

    __tablename__ = "catalog"

    # Columns
    id = Column(
        String(100),
        nullable=False, primary_key=True,
        comment="Catalog item ID"
    )
    title = Column(
        String(255),
        nullable=True,
        comment="Item title"
    )
    description = Column(
        String(1000),
        nullable=True,
        comment="Item description"
    )
    type = Column(
        String(50),
        nullable=True, default="document",
        comment="Item type (code, document, test, config, script)"
    )
    created_at = Column(
        DateTime,
        nullable=True,
        comment="Creation timestamp"
    )
    updated_at = Column(
        DateTime,
        nullable=True,
        comment="Last update timestamp"
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Validation methods
    @validates("title")
    def validate_title(self, key, value):
        """Validate title length."""
        if value is not None and len(value) > 255:
            raise ValueError(f"title cannot be longer than 255 characters")
        return value
    @validates("description")
    def validate_description(self, key, value):
        """Validate description length."""
        if value is not None and len(value) > 1000:
            raise ValueError(f"description cannot be longer than 1000 characters")
        return value

    def __init__(self, **kwargs):
        """Initialize a new catalog record."""
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<CatalogItem(id={self.id!r})>"
