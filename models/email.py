"""Email message model definitions."""

from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import Column, DateTime, Integer, String, JSON, Boolean, ARRAY
from sqlalchemy.orm import relationship

from models.base import Base
from models.validators.api_schema import api_validator
from shared_lib.schema_constants import COLUMN_SIZES, MessageDefaults


class EmailMessage(Base):
    """Email message model.
    
    Based on Gmail API Message resource.
    See: https://developers.google.com/gmail/api/reference/rest/v1/users.messages#Message
    """
    
    __tablename__ = "email_messages"
    
    # Core Gmail API fields (exact field names from API)
    id = Column(
        String(COLUMN_SIZES["MESSAGE_ID"]),
        primary_key=True,
        comment="Gmail message ID"
    )
    threadId = Column(
        String(COLUMN_SIZES["THREAD_ID"]),
        nullable=False,
        comment="Gmail thread ID"
    )
    labelIds = Column(
        ARRAY(String(COLUMN_SIZES["LABEL_ID"])),
        nullable=True,
        comment="Gmail label IDs"
    )
    snippet = Column(
        String(COLUMN_SIZES["SNIPPET"]),
        nullable=True,
        comment="Email preview snippet"
    )
    historyId = Column(
        String(COLUMN_SIZES["HISTORY_ID"]),
        nullable=True,
        comment="Gmail history ID"
    )
    internalDate = Column(
        DateTime,
        nullable=True,
        comment="Internal message timestamp"
    )
    sizeEstimate = Column(
        Integer,
        nullable=True,
        comment="Estimated size in bytes"
    )
    raw = Column(
        String,
        nullable=True,
        comment="Raw MIME message"
    )
    payload = Column(
        JSON,
        nullable=True,
        comment="Parsed email structure"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Record creation time"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last update time"
    )
    
    # Relationships
    analysis = relationship("EmailAnalysis", back_populates="email", uselist=False)
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "EmailMessage":
        """Create model instance from Gmail API response."""
        return cls(
            id=response["id"],
            threadId=response["threadId"],
            labelIds=response.get("labelIds", []),
            snippet=response.get("snippet"),
            historyId=response.get("historyId"),
            internalDate=datetime.fromtimestamp(int(response["internalDate"])/1000) if "internalDate" in response else None,
            sizeEstimate=response.get("sizeEstimate"),
            raw=response.get("raw"),
            payload=response.get("payload", {})
        )
    
    def to_api_response(self) -> Dict[str, Any]:
        """Convert model instance to Gmail API response format."""
        return {
            "id": self.id,
            "threadId": self.threadId,
            "labelIds": self.labelIds or [],
            "snippet": self.snippet,
            "historyId": self.historyId,
            "internalDate": int(self.internalDate.timestamp() * 1000) if self.internalDate else None,
            "sizeEstimate": self.sizeEstimate,
            "raw": self.raw,
            "payload": self.payload or {}
        }
    
    def __init__(self, **kwargs):
        """Initialize with defaults from MessageDefaults."""
        defaults = MessageDefaults()
        for key, value in defaults.__dict__.items():
            if key not in kwargs:
                kwargs[key] = value
        super().__init__(**kwargs)
