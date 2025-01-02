"""SQLAlchemy model for email table."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, Table
from sqlalchemy.orm import relationship, validates
from models.base import Base
from shared_lib.schema_constants import COLUMN_SIZES


# Define email_labels if it does not exist
try:
    email_labels
except NameError:
    email_labels = Table(
        "email_labels",
        Base.metadata,
        Column("source_id", String(100), ForeignKey("email.id"), primary_key=True),
        Column("target_id", String(100), ForeignKey("gmaillabel.id"), primary_key=True),
        extend_existing=True
    )

class EmailMessage(Base):
    """Model based on schema.yaml configuration."""

    __tablename__ = "email_messages"

    # Table configuration
    __table_args__ = {"extend_existing": True}

    # Database configuration
    __database__ = "main"  # Default to catalog if not specified

    # Columns
    id = Column(
        String(100),
        nullable=False,
        primary_key=True,
        comment="Email ID"
    )

    thread_id = Column(
        String(100),
        comment="Thread ID"
    )

    message_id = Column(
        String(100),
        comment="Message ID"
    )

    subject = Column(
        String(500),
        comment="Email subject"
    )

    body = Column(
        Text,
        comment="Email body content"
    )

    from_address = Column(
        String(255),
        comment="Sender email address"
    )

    to_address = Column(
        String(255),
        comment="Recipient email address"
    )

    cc_address = Column(
        String(255),
        comment="CC recipients"
    )

    bcc_address = Column(
        String(255),
        comment="BCC recipients"
    )

    snippet = Column(
        String(1000),
        comment="Email preview snippet"
    )

    history_id = Column(
        String(100),
        comment="Gmail history ID"
    )

    labels = Column(
        JSON,
        comment="Email labels as JSON array"
    )

    has_attachments = Column(
        Boolean,
        comment="Whether email has attachments"
    )

    is_read = Column(
        Boolean,
        comment="Whether email has been read"
    )

    is_important = Column(
        Boolean,
        comment="Whether email is marked important"
    )

    full_api_response = Column(
        JSON,
        comment="Full Gmail API response as JSON"
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
        secondary=email_labels
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
        return f"<EmailMessage(id={self.id!r})>"