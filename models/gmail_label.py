"""Gmail label database model."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped
from models.base import Base

class GmailLabel(Base):
    """SQLAlchemy model for Gmail label storage.
    
    Maps to the 'gmail_labels' table in the database. This model stores Gmail label data
    including:
    - Label metadata (id, name, type)
    - Visibility settings
    - History tracking (active status, timestamps)
    
    Gmail labels can be:
    - System labels: Built-in labels with simple IDs (e.g., "INBOX", "SENT", "DRAFT")
    - User-created labels: Custom labels with longer IDs (e.g., "Label_1234567890123456789")
    
    Each label has:
    - A unique ID from Gmail (up to 30 characters)
    - A display name (up to 100 characters)
    - Type ("system" or "user")
    - Visibility settings that control where it appears in the Gmail UI
    - History tracking to know when labels are added, modified, or removed
    """
    __tablename__ = 'gmail_labels'

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)  # Internal ID for history tracking
    label_id: Mapped[str] = Column(String(30), nullable=False)  # Gmail's label ID
    name: Mapped[str] = Column(String(100), nullable=False)  # Label display name
    type: Mapped[str] = Column(String(50))  # 'system' or 'user'
    message_list_visibility: Mapped[str] = Column(String(50))  # Controls visibility in message list
    label_list_visibility: Mapped[str] = Column(String(50))  # Controls visibility in label list
    is_active: Mapped[bool] = Column(Boolean, default=True)  # Whether label still exists in Gmail
    first_seen_at: Mapped[DateTime] = Column(DateTime, nullable=False)  # When label was first discovered
    last_seen_at: Mapped[DateTime] = Column(DateTime, nullable=False)  # Last time label was seen in Gmail
    deleted_at: Mapped[DateTime] = Column(DateTime)  # When label was removed from Gmail (if applicable)

    def __repr__(self):
        """Return string representation."""
        status = "active" if self.is_active else "deleted"
        return f"<GmailLabel(id={self.id}, label_id='{self.label_id}', name='{self.name}', status='{status}')>"
