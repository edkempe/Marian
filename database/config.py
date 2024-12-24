from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator
import os

# Import models first to ensure they are registered with SQLAlchemy
from models.base import Base
from models.email_analysis import EmailAnalysis
from models.email import Email

# Database URLs
EMAIL_DB_URL = os.getenv('EMAIL_DB_URL', 'sqlite:///db_email_store.db')
ANALYSIS_DB_URL = os.getenv('ANALYSIS_DB_URL', 'sqlite:///db_email_analysis.db')

# Create engines
email_engine = create_engine(EMAIL_DB_URL, echo=False)
analysis_engine = create_engine(ANALYSIS_DB_URL, echo=False)

# Create session factories
EmailSession = sessionmaker(bind=email_engine)
AnalysisSession = sessionmaker(bind=analysis_engine)

@contextmanager
def get_email_session() -> Generator:
    """Get a database session for email operations."""
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
    """Get a database session for analysis operations."""
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
    """Initialize database tables."""
    # Drop all tables
    Base.metadata.drop_all(bind=email_engine)
    Base.metadata.drop_all(bind=analysis_engine)

    # Create all tables
    Base.metadata.create_all(bind=email_engine)
    Base.metadata.create_all(bind=analysis_engine)

if __name__ == "__main__":
    init_db()
