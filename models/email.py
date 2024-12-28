"""Email database model.

This model is designed to store email data from Gmail. The Gmail API response format
is considered the source of truth for field types and meanings. For complete API
documentation, see: https://developers.google.com/gmail/api/reference/rest/v1/users.messages

Field Types from Gmail API:
- id: string (Gmail message ID)
- threadId: string
- labelIds: list[string]
- snippet: string
- payload.headers: list[{name: string, value: string}]
  - subject: string
  - from: string
  - to: string
  - date: string (RFC 2822 format)
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, func, CheckConstraint
from sqlalchemy.orm import Mapped, relationship
from models.base import Base
from typing import Optional
from datetime import datetime

# Constants used in this model
EMAIL_COLUMN_SIZES = {
    'EMAIL_LABELS': 500,  # Maximum size for labels string
    'EMAIL_SUBJECT': 500,  # Maximum size for subject
    'EMAIL_SENDER': 200,  # Maximum size for sender
    'EMAIL_THREAD': 100,   # Maximum size for thread ID
    'EMAIL_TO': 200,      # Maximum size for recipient
    'EMAIL_ID': 100,      # Maximum size for Gmail message ID
}

EMAIL_DEFAULTS = {
    'EMAIL_SUBJECT': '',
    'EMPTY_STRING': '',
    'HAS_ATTACHMENTS': False,
    'API_RESPONSE': '{}'
}

class Email(Base):
    """SQLAlchemy model for email storage.
    
    Maps to the 'emails' table in the database. This model stores processed email data
    from Gmail. For complete documentation on database design decisions and schema details,
    see docs/database_design.md.
    
    Key Fields (types match Gmail API):
    - id: Gmail message ID (VARCHAR(100))
    - threadId: Gmail thread ID (VARCHAR(100))
    - subject: Email subject (VARCHAR(500))
    - body: Email body (TEXT)
    - date: When the email was received (DATETIME with timezone)
    - labelIds: Comma-separated Gmail label IDs (VARCHAR(500))
    - snippet: Email snippet (TEXT)
    - from_: Sender email address (VARCHAR(200))
    - to: Recipient email address (VARCHAR(200))
    - has_attachments: Whether the email has attachments (BOOLEAN)
    - cc: CC recipient email address (TEXT)
    - bcc: BCC recipient email address (TEXT)
    - full_api_response: Complete Gmail API response (TEXT)
    """
    __tablename__ = 'emails'

    id: Mapped[str] = Column(String(100), primary_key=True)
    threadId: Mapped[Optional[str]] = Column(String(100))
    subject: Mapped[Optional[str]] = Column(String(500), default=EMAIL_DEFAULTS['EMAIL_SUBJECT'])
    body: Mapped[Optional[str]] = Column(Text)
    date: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    labelIds: Mapped[Optional[str]] = Column(String(500))  # Stored as JSON
    snippet: Mapped[Optional[str]] = Column(Text)
    from_: Mapped[Optional[str]] = Column('from', String(200), nullable=True)
    to: Mapped[Optional[str]] = Column(String(200), nullable=True)
    has_attachments: Mapped[Optional[bool]] = Column(Boolean, default=EMAIL_DEFAULTS['HAS_ATTACHMENTS'])
    cc: Mapped[Optional[str]] = Column(Text, server_default="''''''")
    bcc: Mapped[Optional[str]] = Column(Text, server_default="''''''")
    full_api_response: Mapped[Optional[str]] = Column(Text, server_default=EMAIL_DEFAULTS['API_RESPONSE'])

    # Relationships
    analysis = relationship("EmailAnalysis", back_populates="email", uselist=False)

    def __repr__(self):
        """Return string representation."""
        return f"<Email(id='{self.id}', subject='{self.subject}', threadId='{self.threadId}')>"
