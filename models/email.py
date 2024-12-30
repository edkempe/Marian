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
from shared_lib.schema_constants import COLUMN_SIZES, EmailDefaults

# Default values for email fields
EMAIL_DEFAULTS = vars(EmailDefaults())

class Email(Base):
    """SQLAlchemy model for email storage."""

    __tablename__ = "emails"

    # Primary key and identifiers
    id: Mapped[str] = Column(
        String(COLUMN_SIZES["EMAIL_ID"]),
        primary_key=True
    )
    thread_id: Mapped[str] = Column(
        String(COLUMN_SIZES["EMAIL_THREAD_ID"]),
        index=True
    )
    message_id: Mapped[str] = Column(
        String(COLUMN_SIZES["EMAIL_MESSAGE_ID"]),
        unique=True
    )

    # Email content
    subject: Mapped[str] = Column(
        String(COLUMN_SIZES["EMAIL_SUBJECT"]),
        server_default=EMAIL_DEFAULTS["subject"]
    )
    body: Mapped[Optional[str]] = Column(
        Text,
        nullable=True
    )
    snippet: Mapped[Optional[str]] = Column(
        Text,
        nullable=True
    )

    # Email addresses
    from_address: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["EMAIL_FROM"]),
        nullable=True
    )
    to_address: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["EMAIL_TO"]),
        nullable=True
    )
    cc_address: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["EMAIL_CC"]),
        nullable=True
    )
    bcc_address: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["EMAIL_BCC"]),
        nullable=True
    )

    # Flags and metadata
    has_attachments: Mapped[bool] = Column(
        Boolean,
        server_default=str(EMAIL_DEFAULTS["has_attachments"])
    )
    is_read: Mapped[bool] = Column(
        Boolean,
        server_default=str(EMAIL_DEFAULTS["is_read"])
    )
    is_important: Mapped[bool] = Column(
        Boolean,
        server_default=str(EMAIL_DEFAULTS["is_important"])
    )

    # API response storage
    api_response: Mapped[str] = Column(
        JSON,
        server_default=EMAIL_DEFAULTS["api_response"]
    )

    # Timestamps
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    received_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        nullable=False
    )

    # Relationships
    analysis = relationship("EmailAnalysis", back_populates="email", uselist=False)
    labels = relationship("EmailLabel", back_populates="email")

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
        subject = response.get("subject", EMAIL_DEFAULTS["subject"])
        if len(subject) > COLUMN_SIZES["EMAIL_SUBJECT"]:
            subject = subject[:COLUMN_SIZES["EMAIL_SUBJECT"]]

        from_address = response.get("from", "")[:COLUMN_SIZES["EMAIL_FROM"]]
        to_address = response.get("to", "")[:COLUMN_SIZES["EMAIL_TO"]]

        return cls(
            id=response["id"],
            thread_id=response.get("threadId", ""),
            message_id=response.get("messageId", ""),
            subject=subject,
            body=response.get("body"),
            snippet=response.get("snippet"),
            from_address=from_address,
            to_address=to_address,
            cc_address=response.get("cc"),
            bcc_address=response.get("bcc"),
            has_attachments=response.get("hasAttachments", EMAIL_DEFAULTS["has_attachments"]),
            is_read=response.get("isRead", EMAIL_DEFAULTS["is_read"]),
            is_important=response.get("isImportant", EMAIL_DEFAULTS["is_important"]),
            api_response=response,
            received_at=datetime.fromisoformat(response["receivedAt"])
        )
