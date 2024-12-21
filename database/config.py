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

def init_db():
    """Initialize database tables."""
    from models.base import Base
    from models.email_analysis import EmailAnalysis
    from models.email import Email
    from sqlalchemy import create_engine
    import os

    # Default paths match the actual database files
    analysis_db_url = os.getenv('ANALYSIS_DB_URL', 'sqlite:///db_email_analysis.db')
    email_db_url = os.getenv('EMAIL_DB_URL', 'sqlite:///db_email_store.db')

    # Create analysis database and tables
    analysis_engine = create_engine(analysis_db_url)
    Base.metadata.create_all(analysis_engine)

    # Create email database and tables
    email_engine = create_engine(email_db_url)
    Base.metadata.create_all(email_engine)

if __name__ == "__main__":
    init_db()
