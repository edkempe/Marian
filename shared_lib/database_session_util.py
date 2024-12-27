"""Database session management and initialization."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator, Dict, Optional
import os
import json

# Import models first to ensure they are registered with SQLAlchemy
from models.base import Base
from models.email_analysis import EmailAnalysis
from models.email import Email
from shared_lib.constants import DATABASE_CONFIG

def create_db_engine(config: Dict[str, str], env_var: str):
    """Create a database engine from config or environment variable."""
    url = os.getenv(env_var)
    if not url and 'test_path' in config:
        # Use in-memory SQLite for testing
        url = f"sqlite:///{config['test_path']}"
    elif not url:
        # Use file path from config
        url = f"sqlite:///{config['path']}"
    return create_engine(url, echo=False)

# Create engines using URLs from constants
email_engine = create_db_engine(DATABASE_CONFIG['email'], 'EMAIL_DB_URL')
analysis_engine = create_db_engine(DATABASE_CONFIG['analysis'], 'ANALYSIS_DB_URL')

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
def get_email_session(config: Optional[Dict[str, str]] = None) -> Generator:
    """Get a database session for email operations with automatic management.
    
    This context manager automatically handles commit, rollback, and cleanup.
    
    Args:
        config: Optional database configuration override
    """
    if config:
        engine = create_db_engine(config, 'EMAIL_DB_URL')
        session = sessionmaker(bind=engine)()
    else:
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
def get_analysis_session(config: Optional[Dict[str, str]] = None) -> Generator:
    """Get a database session for analysis operations with automatic management.
    
    This context manager automatically handles commit, rollback, and cleanup.
    
    Args:
        config: Optional database configuration override
    """
    if config:
        engine = create_db_engine(config, 'ANALYSIS_DB_URL')
        session = sessionmaker(bind=engine)()
    else:
        session = AnalysisSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db():
    """Initialize all database tables.
    
    Creates all tables defined in the SQLAlchemy models if they don't exist.
    This is safe to run multiple times as it will not recreate existing tables.
    """
    Base.metadata.create_all(email_engine)
    Base.metadata.create_all(analysis_engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")
