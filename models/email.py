"""Email database model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func, CheckConstraint
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
    
    Key Fields:
    - id: Internal ID (INTEGER)
    - subject: Email subject (VARCHAR(500))
    - body: Email body (TEXT)
    - sender: Sender email address (VARCHAR(200))
    - to_address: Recipient email address (VARCHAR(200))
    - received_date: When the email was received (DATETIME)
    - labels: Comma-separated Gmail label IDs (VARCHAR(500))
    - thread_id: Gmail thread ID (VARCHAR(100))
    - has_attachments: Whether the email has attachments (BOOLEAN)
    - cc_address: CC recipient email address (TEXT)
    - bcc_address: BCC recipient email address (TEXT)
    - full_api_response: Complete Gmail API response (TEXT)
    """
    __tablename__ = 'emails'

    id: Mapped[int] = Column(Integer, primary_key=True)
    subject: Mapped[Optional[str]] = Column(String(EMAIL_COLUMN_SIZES['EMAIL_SUBJECT']), 
                                          default=EMAIL_DEFAULTS['EMAIL_SUBJECT'])
    body: Mapped[Optional[str]] = Column(Text)
    sender: Mapped[Optional[str]] = Column(String(EMAIL_COLUMN_SIZES['EMAIL_SENDER']))
    to_address: Mapped[Optional[str]] = Column(String(EMAIL_COLUMN_SIZES['EMAIL_TO']))
    received_date: Mapped[Optional[datetime]] = Column(DateTime)
    labels: Mapped[Optional[str]] = Column(String(EMAIL_COLUMN_SIZES['EMAIL_LABELS']))
    thread_id: Mapped[Optional[str]] = Column(String(EMAIL_COLUMN_SIZES['EMAIL_THREAD']))
    has_attachments: Mapped[Optional[bool]] = Column(Boolean, default=EMAIL_DEFAULTS['HAS_ATTACHMENTS'])
    cc_address: Mapped[Optional[str]] = Column(Text, server_default="''''''")
    bcc_address: Mapped[Optional[str]] = Column(Text, server_default="''''''")
    full_api_response: Mapped[Optional[str]] = Column(Text, default=EMAIL_DEFAULTS['API_RESPONSE'])

    # Relationships
    analysis = relationship("EmailAnalysis", back_populates="email", uselist=False)

    def __repr__(self):
        """Return string representation."""
        return f"<Email(id='{self.id}', subject='{self.subject}', thread='{self.thread_id}')>"
