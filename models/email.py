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
    subject: Mapped[Optional[str]] = Column(Text, nullable=True, default=EMAIL_DEFAULTS['EMAIL_SUBJECT'])
    from_address: Mapped[Optional[str]] = Column(Text, nullable=True)
    to_address: Mapped[Optional[str]] = Column(Text, nullable=True)
    cc_address: Mapped[Optional[str]] = Column(Text, nullable=True)
    bcc_address: Mapped[Optional[str]] = Column(Text, nullable=True)
    received_date: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    content: Mapped[Optional[str]] = Column(Text, nullable=True)
    labels: Mapped[Optional[str]] = Column(Text, nullable=True)  # Store as comma-separated string
    has_attachments: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    full_api_response: Mapped[Optional[str]] = Column(Text, nullable=True, default=EMAIL_DEFAULTS['API_RESPONSE'])

    # Relationships
    analysis = relationship("EmailAnalysis", back_populates="email", uselist=False)

    def __repr__(self):
        """Return string representation of email."""
        return f"<Email(id='{self.id}', subject='{self.subject}', from='{self.from_address}')>"

    @property
    def label_list(self) -> list[str]:
        """Get labels as a list."""
        if not self.labels:
            return []
        return self.labels.split(',')

    @label_list.setter
    def label_list(self, labels: list[str]) -> None:
        """Set labels from a list."""
        if not labels:
            self.labels = None
        else:
            self.labels = ','.join(labels)
