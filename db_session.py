"""Database session management and initialization."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os

# Import models first to ensure they are registered with SQLAlchemy
from models.base import Base
from models.email_analysis import EmailAnalysis
from models.email import Email
from config.constants import DATABASE_CONFIG

# Create engines using URLs from constants
email_engine = create_engine(os.getenv('EMAIL_DB_URL', DATABASE_CONFIG['EMAIL_DB_URL']), echo=False)
analysis_engine = create_engine(os.getenv('ANALYSIS_DB_URL', DATABASE_CONFIG['ANALYSIS_DB_URL']), echo=False)

# Create session factories
EmailSession = sessionmaker(bind=email_engine)
AnalysisSession = sessionmaker(bind=analysis_engine)

def get_email_session_raw() -> Session:
    """Get a raw SQLAlchemy session for the email database.
    
    Note: Caller is responsible for session management (commit/rollback/close).
    For automatic session management, use get_email_session() context manager instead.
    """
    return EmailSession()

def get_analysis_session_raw() -> Session:
    """Get a raw SQLAlchemy session for the analysis database.
    
    Note: Caller is responsible for session management (commit/rollback/close).
    For automatic session management, use get_analysis_session() context manager instead.
    """
    return AnalysisSession()

@contextmanager
def get_email_session() -> Generator:
    """Get a database session for email operations with automatic management.
    
    This context manager automatically handles commit, rollback, and cleanup.
    """
    session = EmailSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@contextmanager
def get_analysis_session() -> Generator:
    """Get a database session for analysis operations with automatic management.
    
    This context manager automatically handles commit, rollback, and cleanup.
    """
    session = AnalysisSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db() -> None:
    """Initialize all database tables.
    
    Creates all tables defined in the SQLAlchemy models if they don't exist.
    This is safe to run multiple times as it will not recreate existing tables.
    """
    # Create all tables
    Base.metadata.create_all(email_engine)
    Base.metadata.create_all(analysis_engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")
