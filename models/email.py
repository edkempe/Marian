"""Email database model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func, CheckConstraint
from sqlalchemy.orm import Mapped
from models.base import Base
from typing import Optional

class Email(Base):
    """SQLAlchemy model for email storage.
    
    Maps to the 'emails' table in the database. This model stores processed email data
    from Gmail. For complete documentation on database design decisions and schema details,
    see docs/database_design.md.
    
    Key Fields:
    - id: Gmail message ID (TEXT)
    - thread_id: Gmail thread ID (TEXT)
    - subject, sender, date: Basic metadata
    - body: Email content
    - labels: Comma-separated Gmail label IDs
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
    subject: Mapped[str] = Column(Text, server_default='No Subject')
    sender: Mapped[str] = Column(Text, nullable=False)
    date: Mapped[str] = Column(Text, nullable=False)  # Store as ISO format string
    body: Mapped[str] = Column(Text, server_default='')
    labels: Mapped[str] = Column(String(150), server_default='')
    has_attachments: Mapped[bool] = Column(Boolean, nullable=False, server_default='0')
    full_api_response: Mapped[str] = Column(Text, server_default='{}')

    def __repr__(self):
        """Return string representation."""
        return f"<Email(id={self.id}, subject='{self.subject}', sender='{self.sender}')>"
