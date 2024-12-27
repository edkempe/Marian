"""Email database model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func, CheckConstraint
from sqlalchemy.orm import Mapped, relationship
from models.base import Base
from typing import Optional
from datetime import datetime

# Constants used in this model
EMAIL_COLUMN_SIZES = {
    'EMAIL_LABELS': 1000  # Maximum size for labels string
}

EMAIL_DEFAULTS = {
    'EMAIL_SUBJECT': '',
    'EMPTY_STRING': '',
    'HAS_ATTACHMENTS': 'false',  # SQLite boolean default
    'API_RESPONSE': '{}'
}

class Email(Base):
    """SQLAlchemy model for email storage.
    
    Maps to the 'emails' table in the database. This model stores processed email data
    from Gmail. For complete documentation on database design decisions and schema details,
    see docs/database_design.md.
    
    Key Fields:
    - id: Gmail message ID (TEXT)
    - thread_id: Gmail thread ID (TEXT)
    - subject: Email subject
    - from_address: Sender email address
    - to_address: Recipient email address
    - cc_address: CC recipient email address
    - bcc_address: BCC recipient email address
    - received_date: When the email was received (as DateTime)
    - content: Email content
    - labels: Comma-separated Gmail label IDs
    - has_attachments: Whether the email has attachments
    - full_api_response: Complete Gmail API response
    
    Note: This model is the source of truth for the database schema.
    Any changes should be made here first, then migrated to the database.
    """
    __tablename__ = 'emails'
    __table_args__ = (
        CheckConstraint("id != ''", name='id_not_empty'),
        CheckConstraint("thread_id != ''", name='thread_id_not_empty'),
        {'extend_existing': True}
    )

    id: Mapped[str] = Column(Text, primary_key=True)
    thread_id: Mapped[str] = Column(Text, nullable=False)
    subject: Mapped[str] = Column(Text, server_default=EMAIL_DEFAULTS['EMAIL_SUBJECT'])
    from_address: Mapped[str] = Column(Text, nullable=False)
    to_address: Mapped[str] = Column(Text, nullable=False)
    cc_address: Mapped[str] = Column(Text, server_default=EMAIL_DEFAULTS['EMPTY_STRING'])
    bcc_address: Mapped[str] = Column(Text, server_default=EMAIL_DEFAULTS['EMPTY_STRING'])
    received_date: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    content: Mapped[str] = Column(Text, server_default=EMAIL_DEFAULTS['EMPTY_STRING'])
    labels: Mapped[str] = Column(String(EMAIL_COLUMN_SIZES['EMAIL_LABELS']), server_default=EMAIL_DEFAULTS['EMPTY_STRING'])
    has_attachments: Mapped[bool] = Column(Boolean, nullable=False, server_default=EMAIL_DEFAULTS['HAS_ATTACHMENTS'])
    full_api_response: Mapped[str] = Column(Text, server_default=EMAIL_DEFAULTS['API_RESPONSE'])

    # Relationships
    analysis = relationship("EmailAnalysis", back_populates="email", uselist=False)

    def __repr__(self):
        """Return string representation."""
        return f"<Email(id={self.id}, subject='{self.subject}', from_address='{self.from_address}')>"
