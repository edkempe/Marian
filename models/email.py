"""Email model for storing email data."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
    JSON
)
from sqlalchemy.orm import Mapped, relationship

from models.base import Base
from shared_lib.config_loader import get_schema_config

# Get schema configuration
config = get_schema_config().email


class Email(Base):
    """SQLAlchemy model for email storage."""

    __tablename__ = "emails"

    # Primary key and identifiers
    id: Mapped[str] = Column(
        String(config.columns["id"].size),
        primary_key=True
    )
    thread_id: Mapped[str] = Column(
        String(config.columns["thread_id"].size),
        index=True
    )
    message_id: Mapped[str] = Column(
        String(config.columns["message_id"].size),
        unique=True
    )

    # Email content
    subject: Mapped[str] = Column(
        String(config.columns["subject"].size),
        server_default=config.defaults.subject
    )
    body: Mapped[Optional[str]] = Column(
        Text,
        nullable=True
    )
    snippet: Mapped[Optional[str]] = Column(
        String(config.columns["snippet"].size),
        nullable=True
    )

    # Metadata
    sender: Mapped[str] = Column(
        String(config.columns["sender"].size)
    )
    recipient: Mapped[str] = Column(
        String(config.columns["recipient"].size)
    )
    cc: Mapped[Optional[str]] = Column(
        String(config.columns["cc"].size),
        nullable=True
    )
    bcc: Mapped[Optional[str]] = Column(
        String(config.columns["bcc"].size),
        nullable=True
    )
    
    # Flags and status
    has_attachments: Mapped[bool] = Column(
        Boolean,
        server_default=str(config.defaults.has_attachments)
    )
    is_read: Mapped[bool] = Column(
        Boolean,
        server_default=str(config.defaults.is_read)
    )
    is_important: Mapped[bool] = Column(
        Boolean,
        server_default=str(config.defaults.is_important)
    )

    # Raw data and API responses
    raw_data: Mapped[Optional[dict]] = Column(
        JSON,
        nullable=True,
        server_default=config.defaults.api_response
    )

    # Timestamps
    received_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        nullable=False
    )
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
    analysis = relationship("EmailAnalysis", back_populates="email", uselist=False)
    labels = relationship("GmailLabel", secondary="email_labels", back_populates="emails")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Email(id={self.id}, subject={self.subject})>"

    @classmethod
    def from_api_response(cls, response: dict) -> "Email":
        """Create an Email instance from API response.

        Args:
            response: Dictionary containing email data from API

        Returns:
            Email instance
        """
        # Validate and truncate fields if needed
        subject = response.get("subject", config.defaults.subject)
        if len(subject) > config.validation.max_subject_length:
            subject = subject[:config.validation.max_subject_length]

        sender = response.get("from", "")[:config.columns["sender"].size]
        recipient = response.get("to", "")[:config.columns["recipient"].size]

        return cls(
            id=response["id"],
            thread_id=response.get("threadId", ""),
            message_id=response.get("messageId", ""),
            subject=subject,
            body=response.get("body"),
            snippet=response.get("snippet"),
            sender=sender,
            recipient=recipient,
            cc=response.get("cc"),
            bcc=response.get("bcc"),
            has_attachments=response.get("hasAttachments", config.defaults.has_attachments),
            is_read=response.get("isRead", config.defaults.is_read),
            is_important=response.get("isImportant", config.defaults.is_important),
            raw_data=response,
            received_at=datetime.fromisoformat(response["receivedAt"])
        )
