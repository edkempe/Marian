"""Gmail label model for storing label data.

Based on Gmail API Label resource:
https://developers.google.com/gmail/api/reference/rest/v1/users.labels#Label
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    func,
    event
)
from sqlalchemy.orm import Mapped, relationship

from models.base import Base
from models.validators import APISchemaValidator
from config.settings.label import (
    label_settings,
    LabelType,
    MessageListVisibility,
    LabelListVisibility
)

# Initialize API schema validator
api_validator = APISchemaValidator()

@event.listens_for(Base.metadata, 'after_create')
def validate_schemas(target, connection, **kw):
    """Validate all models against their API schemas."""
    api_validator.validate_model(GmailLabel, "gmail", "v1", "label")

# Association table for many-to-many relationship between emails and labels
email_labels = Table(
    "email_labels",
    Base.metadata,
    Column(
        "email_id",
        Integer,
        ForeignKey("email_messages.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "label_id",
        String(label_settings.NAME_MAX_LENGTH),
        ForeignKey("gmail_labels.id", ondelete="CASCADE"),
        primary_key=True
    ),
    extend_existing=True
)


class GmailLabel(Base):
    """SQLAlchemy model for Gmail label storage.
    
    Attributes match the Gmail API Label resource structure:
    https://developers.google.com/gmail/api/reference/rest/v1/users.labels#Label
    """

    __tablename__ = "gmail_labels"

    # Primary key and identifiers
    id: Mapped[str] = Column(
        String(label_settings.NAME_MAX_LENGTH),
        primary_key=True
    )
    name: Mapped[str] = Column(
        String(label_settings.NAME_MAX_LENGTH),
        unique=True,
        nullable=False
    )

    # Label properties from Gmail API
    type: Mapped[str] = Column(
        String(20),
        nullable=False,
        default=label_settings.TYPE.value
    )
    message_list_visibility: Mapped[Optional[str]] = Column(
        String(20),
        nullable=True,
        default=label_settings.MESSAGE_LIST_VISIBILITY.value
    )
    label_list_visibility: Mapped[Optional[str]] = Column(
        String(20),
        nullable=True,
        default=label_settings.LABEL_LIST_VISIBILITY.value
    )

    # Color settings (only for user labels)
    color: Mapped[Optional[str]] = Column(
        String(label_settings.COLOR_MAX_LENGTH),
        nullable=True
    )
    background_color: Mapped[Optional[str]] = Column(
        String(label_settings.COLOR_MAX_LENGTH),
        nullable=True,
        default=label_settings.DEFAULT_BACKGROUND_COLOR
    )
    text_color: Mapped[Optional[str]] = Column(
        String(label_settings.COLOR_MAX_LENGTH),
        nullable=True,
        default=label_settings.DEFAULT_TEXT_COLOR
    )

    # Counters for messages and threads (nullable as per Gmail API)
    messages_total: Mapped[Optional[int]] = Column(
        Integer,
        nullable=True,
        default=label_settings.DEFAULT_MESSAGES_TOTAL
    )
    messages_unread: Mapped[Optional[int]] = Column(
        Integer,
        nullable=True,
        default=label_settings.DEFAULT_MESSAGES_UNREAD
    )
    threads_total: Mapped[Optional[int]] = Column(
        Integer,
        nullable=True,
        default=label_settings.DEFAULT_THREADS_TOTAL
    )
    threads_unread: Mapped[Optional[int]] = Column(
        Integer,
        nullable=True,
        default=label_settings.DEFAULT_THREADS_UNREAD
    )

    # Timestamps
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    emails = relationship(
        "EmailMessage",
        secondary=email_labels,
        back_populates="labels",
        cascade="all",
        passive_deletes=True
    )

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "GmailLabel":
        """Create a GmailLabel instance from an API response."""
        return cls(
            id=response["id"],
            name=response["name"],
            type=response["type"],
            message_list_visibility=response.get("messageListVisibility"),
            label_list_visibility=response.get("labelListVisibility"),
            background_color=response.get("backgroundColor"),
            text_color=response.get("textColor"),
            is_system=response["type"] == "system"
        )

    def __init__(self, **kwargs):
        """Initialize a new Gmail label."""
        super().__init__(**kwargs)
        self.validate()

    def validate(self):
        """Validate label attributes."""
        if self.name is None:
            raise ValueError("Label name cannot be None")
            
        if len(self.name) > label_settings.NAME_MAX_LENGTH:
            raise ValueError(f"Label name exceeds maximum length of {label_settings.NAME_MAX_LENGTH}")

        if self.type not in [t.value for t in LabelType]:
            raise ValueError(f"Invalid label type: {self.type}")

        if self.message_list_visibility and self.message_list_visibility not in [v.value for v in MessageListVisibility]:
            raise ValueError(f"Invalid message list visibility: {self.message_list_visibility}")

        if self.label_list_visibility and self.label_list_visibility not in [v.value for v in LabelListVisibility]:
            raise ValueError(f"Invalid label list visibility: {self.label_list_visibility}")

    def __repr__(self) -> str:
        """Get string representation."""
        return f"<GmailLabel(id='{self.id}', name='{self.name}', type='{self.type}')>"
