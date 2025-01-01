"""Thread model definition."""

from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import Column, DateTime, Integer, String, event, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base
from models.validators import APISchemaValidator
from shared_lib.schema_constants import COLUMN_SIZES


# Initialize API schema validator
api_validator = APISchemaValidator()

@event.listens_for(Base.metadata, 'after_create')
def validate_schemas(target, connection, **kw):
    """Validate all models against their API schemas."""
    api_validator.validate_model(Thread, "gmail", "v1", "thread")


class Thread(Base):
    """Email thread model.
    
    Based on Gmail API Thread resource:
    https://developers.google.com/gmail/api/reference/rest/v1/users.threads#Thread
    """
    
    __tablename__ = "email_threads"
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(
        String(COLUMN_SIZES["EMAIL_THREAD_ID"]),
        unique=True,
        nullable=False,
        comment="Gmail API thread ID"
    )
    snippet = Column(
        String(COLUMN_SIZES["THREAD_SNIPPET"]),
        nullable=True,
        comment="Short snippet from the thread"
    )
    history_id = Column(
        String(COLUMN_SIZES["HISTORY_ID"]),
        nullable=True,
        comment="Last history ID that modified this thread"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        comment="Thread creation time"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last update time"
    )
    
    # Relationships
    messages = relationship(
        "EmailMessage",
        back_populates="thread",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Thread(id={self.id}, thread_id='{self.thread_id}')>"
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "Thread":
        """Create a Thread instance from an API response."""
        return cls(
            thread_id=response["id"],
            snippet=response.get("snippet"),
            history_id=response.get("historyId")
        )
