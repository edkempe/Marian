"""SQLAlchemy model for email table."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship, validates
from models.base import Base
from shared_lib.schema_constants import COLUMN_SIZES


class EmailMessage(Base):
    """Model for email based on schema.yaml configuration."""

    __tablename__ = "email"

    # Columns
    id = Column(
        String(100),
        nullable=False, primary_key=True,
        comment="Email ID"
    )
    thread_id = Column(
        String(100),
        nullable=True,
        comment="Thread ID"
    )
    message_id = Column(
        String(100),
        nullable=True,
        comment="Message ID"
    )
    subject = Column(
        String(500),
        nullable=True, default="",
        comment="Email subject"
    )
    body = Column(
        Text,
        nullable=True,
        comment="Email body content"
    )
    from_address = Column(
        String(255),
        nullable=True,
        comment="Sender email address"
    )
    to_address = Column(
        String(255),
        nullable=True,
        comment="Recipient email address"
    )
    cc_address = Column(
        String(255),
        nullable=True,
        comment="CC recipients"
    )
    bcc_address = Column(
        String(255),
        nullable=True,
        comment="BCC recipients"
    )
    snippet = Column(
        String(1000),
        nullable=True,
        comment="Email preview snippet"
    )
    history_id = Column(
        String(100),
        nullable=True,
        comment="Gmail history ID"
    )
    labels = Column(
        JSON,
        nullable=True, default="[]",
        comment="Email labels as JSON array"
    )
    has_attachments = Column(
        Boolean,
        nullable=True, default=False,
        comment="Whether email has attachments"
    )
    is_read = Column(
        Boolean,
        nullable=True, default=False,
        comment="Whether email has been read"
    )
    is_important = Column(
        Boolean,
        nullable=True, default=False,
        comment="Whether email is marked important"
    )
    full_api_response = Column(
        JSON,
        nullable=True, default="{}",
        comment="Full Gmail API response as JSON"
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    catalog_entry = relationship(
        "CatalogEntry",
        back_populates="email",
        cascade="all, delete-orphan"
    )
    labels = relationship(
        "GmailLabel",
        back_populates="emails",
        cascade="all",
        secondary="email_labels"
    )

    # Validation methods
    @validates("subject")
    def validate_subject(self, key, value):
        """Validate subject length."""
        if value is not None and len(value) > 500:
            raise ValueError(f"subject cannot be longer than 500 characters")
        return value

    def __init__(self, **kwargs):
        """Initialize a new email record."""
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<EmailMessage(id={self.id!r})>"
