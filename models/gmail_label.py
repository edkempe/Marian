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
from shared_lib.config_loader import get_schema_config

# Get schema configuration
config = get_schema_config().label

# Association table for many-to-many relationship between emails and labels
email_labels = Table(
    "email_labels",
    Base.metadata,
    Column("email_id", String(100), ForeignKey("emails.id"), primary_key=True),
    Column("label_id", String(100), ForeignKey("gmail_labels.id"), primary_key=True),
)


class GmailLabel(Base):
    """SQLAlchemy model for Gmail label storage."""

    __tablename__ = "gmail_labels"

    # Primary key and identifiers
    id: Mapped[str] = Column(
        String(config.columns["id"].size),
        primary_key=True
    )
    name: Mapped[str] = Column(
        String(config.columns["name"].size),
        unique=True
    )

    # Label properties
    type: Mapped[str] = Column(
        String(config.columns["type"].size),
        server_default=config.defaults.type
    )
    message_list_visibility: Mapped[Optional[str]] = Column(
        String(config.columns["visibility"].size),
        nullable=True
    )
    label_list_visibility: Mapped[Optional[str]] = Column(
        String(config.columns["visibility"].size),
        nullable=True
    )
    
    # System flags
    is_system: Mapped[bool] = Column(
        Boolean,
        server_default=str(config.defaults.is_system)
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
        name = response.get("name", "")
        if len(name) > config.validation.max_name_length:
            name = name[:config.validation.max_name_length]

        # Validate label type
        label_type = response.get("type", config.defaults.type)
        if label_type not in config.validation.valid_types:
            label_type = config.defaults.type

        return cls(
            id=response["id"],
            name=name,
            type=label_type,
            message_list_visibility=response.get("messageListVisibility"),
            label_list_visibility=response.get("labelListVisibility"),
            is_system=response.get("type") == "system"
        )
