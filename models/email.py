"""Email database model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func, ARRAY
from sqlalchemy.orm import Mapped, relationship
from models.base import Base
from models.gmail_label import GmailLabel

class Email(Base):
    """SQLAlchemy model for email storage.
    
    Maps to the 'emails' table in the database. This model stores processed email data
    from Gmail, including:
    - Basic metadata (id, subject, sender, received_date)
    - Content (body)
    - Organization (labels, thread_id)
    - Attachments flag
    
    The schema is optimized for:
    - Efficient querying with proper data types (DateTime for dates, Integer for IDs)
    - Storage efficiency with column size limits
    - Email threading support via thread_id
    
    Labels are stored as comma-separated Gmail label IDs (e.g., "Label_1234567890123456789,INBOX")
    with a maximum of 4 labels per email. The actual label metadata is stored in the gmail_labels table.
    Each Gmail label ID can be up to 30 characters:
    - System labels: Usually short (e.g., "INBOX", "SENT")
    - User labels: Up to ~25 chars (e.g., "Label_1234567890123456789")
    
    Note:
        This model uses SQLAlchemy's default table configuration without extend_existing
        since we manage schema changes through proper migrations rather than runtime
        table modifications.
    """
    __tablename__ = 'emails'

    id: Mapped[int] = Column(Integer, primary_key=True)
    subject: Mapped[str] = Column(String(500))  # Limited length for storage efficiency
    body: Mapped[str] = Column(Text)  # Full email content
    sender: Mapped[str] = Column(String(200))  # Email sender address
    received_date: Mapped[DateTime] = Column(DateTime)  # When the email was received
    labels: Mapped[str] = Column(String(150))  # Comma-separated label IDs (max 4 labels, ~30 chars each)
    thread_id: Mapped[str] = Column(String(100))  # For grouping related emails
    has_attachments: Mapped[bool] = Column(Boolean)  # Flag for emails with attachments

    def __repr__(self):
        """Return string representation."""
        return f"<Email(id={self.id}, subject='{self.subject}', sender='{self.sender}')>"
