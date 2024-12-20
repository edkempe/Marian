from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from model_base import Base

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    subject = Column(String(500))
    body = Column(Text)
    sender = Column(String(200))
    received_date = Column(DateTime)
    labels = Column(String(500))
    thread_id = Column(String(100))
    has_attachments = Column(Boolean, default=False)
