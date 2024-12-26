"""Database utilities for Marian."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Database URLs
EMAIL_DB_URL = os.getenv('EMAIL_DB_URL', 'sqlite:///data/db_email_store.db')
ANALYSIS_DB_URL = os.getenv('ANALYSIS_DB_URL', 'sqlite:///data/db_email_analysis.db')

# Create engines
email_engine = create_engine(EMAIL_DB_URL)
analysis_engine = create_engine(ANALYSIS_DB_URL)

# Create session factories
EmailSession = sessionmaker(bind=email_engine)
AnalysisSession = sessionmaker(bind=analysis_engine)

def get_email_session() -> Session:
    """Get a SQLAlchemy session for the email database."""
    return EmailSession()

def get_analysis_session() -> Session:
    """Get a SQLAlchemy session for the analysis database."""
    return AnalysisSession()
