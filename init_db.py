#!/usr/bin/env python3
from sqlalchemy import create_engine
from model_base import Base
from model_email import Email
from model_email_analysis import EmailAnalysis
from database.config import EMAIL_DB_URL, ANALYSIS_DB_URL

def init_databases():
    """Initialize all database tables."""
    # Create engines
    email_engine = create_engine(EMAIL_DB_URL)
    analysis_engine = create_engine(ANALYSIS_DB_URL)

    # Create all tables
    Base.metadata.create_all(email_engine)
    Base.metadata.create_all(analysis_engine)

    print("Database tables created successfully!")

if __name__ == "__main__":
    init_databases()
