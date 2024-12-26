#!/usr/bin/env python3
from sqlalchemy import create_engine
from models.base import Base
from models.email import Email
from models.email_analysis import EmailAnalysis
from shared_lib.database_session_util import email_engine, analysis_engine

def init_databases():
    """Initialize all database tables."""
    # Create all tables
    Base.metadata.create_all(email_engine)
    Base.metadata.create_all(analysis_engine)

    print("Database tables created successfully!")

if __name__ == "__main__":
    init_databases()
