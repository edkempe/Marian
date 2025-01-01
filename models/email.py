"""Email model definitions."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class EmailMessage(Base):
    """Email message model."""
    
    __tablename__ = "email_messages"
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String, unique=True, nullable=False)
    subject = Column(String)
    from_address = Column(String)
    to_addresses = Column(JSON)  # List of email addresses
    cc_addresses = Column(JSON)  # List of email addresses
    bcc_addresses = Column(JSON)  # List of email addresses
    body_text = Column(String)
    body_html = Column(String)
    received_date = Column(DateTime, default=datetime.utcnow)
    sent_date = Column(DateTime)
    
    # Relationships
    analysis = relationship("EmailAnalysis", back_populates="email", uselist=False)
    catalog_entries = relationship("CatalogEntry", back_populates="email")
    
    def __repr__(self) -> str:
        """Get string representation."""
        return f"<EmailMessage(id={self.id}, subject='{self.subject}')>"
