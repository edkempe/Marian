"""Email database model."""
from sqlalchemy import Column, String, Text
from models.base import Base

class Email(Base):
    """SQLAlchemy model for email storage.
    
    Maps to the 'emails' table in db_email_store.db.
    """
    __tablename__ = 'emails'

    id = Column(String, primary_key=True)  # Gmail message ID
    subject = Column(Text)
    body = Column(Text)
    sender = Column(String(200))
    date = Column(String)  # ISO format date string
    labels = Column(Text)  # JSON array as string
    raw_data = Column(Text)  # Raw email data as JSON string
