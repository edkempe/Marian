"""Email database model."""
from sqlalchemy import Column, String, Text
from models.base import Base

class Email(Base):
    """SQLAlchemy model for email storage.
    
    Maps to the 'emails' table in db_email_store.db.
    This model stores raw email data from Gmail, including:
    - Basic metadata (id, subject, sender, date)
    - Content (body)
    - Organization (labels)
    - Raw data for debugging
    """
    __tablename__ = 'emails'
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)  # Gmail message ID
    subject = Column(Text)  # Email subject line
    body = Column(Text)  # Full email body content
    sender = Column(String(200))  # Email sender address
    date = Column(String)  # ISO format date string
    labels = Column(Text)  # JSON array of Gmail labels
    raw_data = Column(Text)  # Raw email data as JSON string for debugging
