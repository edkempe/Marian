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
        server_default=LABEL_DEFAULTS["name"]
    )

    # Label properties
    type: Mapped[str] = Column(
        String(COLUMN_SIZES["LABEL_TYPE"]),
        server_default=LABEL_DEFAULTS["type"]
    )
    message_list_visibility: Mapped[Optional[str]] = Column(
        String(20),  # Fixed size for visibility settings
        server_default=LABEL_DEFAULTS["message_list_visibility"],
        nullable=True
    )
    label_list_visibility: Mapped[Optional[str]] = Column(
        String(20),  # Fixed size for visibility settings
        server_default=LABEL_DEFAULTS["label_list_visibility"],
        nullable=True
    )
    
    # System flags
    is_system: Mapped[bool] = Column(
        Boolean,
        server_default=str(LABEL_DEFAULTS["is_system"])
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

    # Relationships
    emails = relationship("Email", secondary=email_labels, back_populates="labels")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<GmailLabel(id={self.id}, name={self.name})>"

    @classmethod
    def from_api_response(cls, response: dict) -> "GmailLabel":
        """Create a GmailLabel instance from API response.

        Args:
            response: Dictionary containing label data from API

        Returns:
            GmailLabel instance
        """
        # Validate and truncate name if needed
        name = response.get("name", LABEL_DEFAULTS["name"])
        if len(name) > COLUMN_SIZES["LABEL_NAME"]:
            name = name[:COLUMN_SIZES["LABEL_NAME"]]

        # Get label type with default
        label_type = response.get("type", LABEL_DEFAULTS["type"])
        if len(label_type) > COLUMN_SIZES["LABEL_TYPE"]:
            label_type = label_type[:COLUMN_SIZES["LABEL_TYPE"]]

        return cls(
            id=response["id"],
            name=name,
            type=label_type,
            message_list_visibility=response.get("messageListVisibility", LABEL_DEFAULTS["message_list_visibility"]),
            label_list_visibility=response.get("labelListVisibility", LABEL_DEFAULTS["label_list_visibility"]),
            is_system=response.get("type") == "system"
        )
