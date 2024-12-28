"""Gmail label database model."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import Mapped
from models.base import Base
from typing import Optional
from datetime import datetime
from shared_lib.constants import COLUMN_SIZES

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
    - A unique ID from Gmail (up to 100 characters)
    - A display name (up to 100 characters)
    - Type ("system" or "user")
    - Active status and tracking timestamps
    """
    __tablename__ = 'gmail_labels'

    id: Mapped[str] = Column(String(100), primary_key=True)  # Gmail's label ID
    name: Mapped[str] = Column(String(100), nullable=False)  # Label display name
    type: Mapped[str] = Column(String(50), nullable=False)  # 'system' or 'user'
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    first_seen_at: Mapped[datetime] = Column(DateTime, default=func.now(), nullable=False)
    last_seen_at: Mapped[datetime] = Column(DateTime, default=func.now(), 
                                          onupdate=func.now(), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime)

    def __repr__(self):
        """Return string representation."""
        status = "active" if self.is_active else "inactive"
        return f"<GmailLabel(id='{self.id}', name='{self.name}', type='{self.type}', status='{status}')>"
