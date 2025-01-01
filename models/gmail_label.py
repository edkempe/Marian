"""Gmail label model for storing label data."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    func
)
from sqlalchemy.orm import Mapped, relationship

from models.base import Base
from shared_lib.schema_constants import COLUMN_SIZES, LabelDefaults

# Association table for many-to-many relationship between emails and labels
email_labels = Table(
    "email_labels",
    Base.metadata,
    Column("email_id", String(COLUMN_SIZES["EMAIL_ID"]), ForeignKey("emails.id"), primary_key=True),
    Column("label_id", String(COLUMN_SIZES["LABEL_ID"]), ForeignKey("gmail_labels.id"), primary_key=True),
)

# Default values for label fields
LABEL_DEFAULTS = vars(LabelDefaults())


class GmailLabel(Base):
    """SQLAlchemy model for Gmail label storage."""

    __tablename__ = "gmail_labels"

    # Primary key and identifiers
    id: Mapped[str] = Column(
        String(COLUMN_SIZES["LABEL_ID"]),
        primary_key=True
    )
    name: Mapped[str] = Column(
        String(COLUMN_SIZES["LABEL_NAME"]),
        unique=True,
        nullable=False
    )

    # Label properties
    type: Mapped[str] = Column(
        String(COLUMN_SIZES["LABEL_TYPE"]),
        nullable=False
    )
    message_list_visibility: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["LABEL_VISIBILITY"]),
        nullable=True
    )
    label_list_visibility: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["LABEL_VISIBILITY"]),
        nullable=True
    )
    background_color: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["COLOR_CODE"]),
        nullable=True
    )
    text_color: Mapped[Optional[str]] = Column(
        String(COLUMN_SIZES["COLOR_CODE"]),
        nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    emails = relationship(
        "EmailMessage",
        secondary="email_labels",
        back_populates="labels",
        cascade="all",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<GmailLabel(id='{self.id}', name='{self.name}')>"
