"""SQLAlchemy model for label table."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship, validates
from models.base import Base
from shared_lib.schema_constants import COLUMN_SIZES


class GmailLabel(Base):
    """Model for label based on schema.yaml configuration."""

    __tablename__ = "label"

    # Columns
    id = Column(
        String(100),
        nullable=False, primary_key=True,
        comment="Gmail API label ID"
    )
    name = Column(
        String(255),
        nullable=False, default="",
        comment="Display name of the label"
    )
    message_list_visibility = Column(
        String(20),
        nullable=True, default="show",
        comment="Show/hide the label in the message list"
    )
    label_list_visibility = Column(
        String(20),
        nullable=True, default="labelShow",
        comment="Show/hide the label in the label list"
    )
    type = Column(
        String(20),
        nullable=True, default="user",
        comment="Type of label (system/user)"
    )
    color = Column(
        String(20),
        nullable=True,
        comment="Label color (hex code)"
    )
    messages_total = Column(
        Integer,
        nullable=True,
        comment="Total number of messages with this label"
    )
    messages_unread = Column(
        Integer,
        nullable=True,
        comment="Number of unread messages with this label"
    )
    threads_total = Column(
        Integer,
        nullable=True,
        comment="Total number of threads with this label"
    )
    threads_unread = Column(
        Integer,
        nullable=True,
        comment="Number of unread threads with this label"
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
        """Initialize a new label record."""
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<GmailLabel(id={self.id!r})>"
