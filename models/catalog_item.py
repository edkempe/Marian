"""SQLAlchemy model for catalog table."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, Table
from sqlalchemy.orm import relationship, validates
from models.base import Base
from shared_lib.schema_constants import COLUMN_SIZES


class CatalogItem(Base):
    """Model based on schema.yaml configuration."""

    __tablename__ = "catalog_items"

    # Table configuration
    __table_args__ = {"extend_existing": True}

    # Database configuration
    __database__ = "main"  # Default to catalog if not specified

    # Columns
    id = Column(
        String(100),
        nullable=False,
        primary_key=True,
        comment="Catalog item ID"
    )

    title = Column(
        String(255),
        comment="Item title"
    )

    description = Column(
        String(1000),
        comment="Item description"
    )

    type = Column(
        String(50),
        comment="Item type (code, document, test, config, script)"
    )

    created_at = Column(
        DateTime,
        comment="Creation timestamp"
    )

    updated_at = Column(
        DateTime,
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
    def __init__(self, **kwargs):
        """Initialize a new record."""
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<CatalogItem(id={self.id!r})>"