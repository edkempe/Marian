#!/usr/bin/env python3
"""Initialize the email database."""
from model_base import Base
from model_email import Email
from model_email_analysis import EmailAnalysis
from database.config import email_engine, analysis_engine

def init_db():
    """Initialize the databases."""
    # Create email tables
    Base.metadata.create_all(email_engine)
    print("Email database initialized.")

    # Create analysis tables
    Base.metadata.create_all(analysis_engine)
    print("Analysis database initialized.")

if __name__ == "__main__":
    init_db()
