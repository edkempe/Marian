from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator
import os

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
