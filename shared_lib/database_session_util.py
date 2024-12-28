"""Database session utilities."""

from contextlib import contextmanager
from typing import Generator, Any
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from shared_lib.constants import DATABASE_CONFIG

def get_session_factory(db_path: str) -> sessionmaker:
    """Get a session factory for a database."""
    engine = create_engine(f'sqlite:///{db_path}')
    return sessionmaker(bind=engine)

@contextmanager
def get_session(db_path: str) -> Generator[Session, Any, None]:
    """Get a database session."""
    session_factory = get_session_factory(db_path)
    session = session_factory()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# Create engines using URLs from constants
email_engine = create_engine(f"sqlite:///{DATABASE_CONFIG['email']['path']}", echo=False)
analysis_engine = create_engine(f"sqlite:///{DATABASE_CONFIG['analysis']['path']}", echo=False)
catalog_engine = create_engine(f"sqlite:///{DATABASE_CONFIG['catalog']['path']}", echo=False)

# Create session factories
EmailSession = sessionmaker(bind=email_engine)
AnalysisSession = sessionmaker(bind=analysis_engine)
CatalogSession = sessionmaker(bind=catalog_engine)

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

def get_catalog_session_raw() -> Session:
    """Get a raw SQLAlchemy session for the catalog database.
    
    Note: Caller is responsible for session management (commit/rollback/close).
    For automatic session management, use get_catalog_session() context manager instead.
    """
    return CatalogSession()

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

@contextmanager
def get_catalog_session() -> Generator:
    """Get a database session for catalog operations with automatic management.
    
    This context manager automatically handles commit, rollback, and cleanup.
    """
    session = CatalogSession()
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
    # Removed Base.metadata.create_all() calls as models.registry is not imported

if __name__ == "__main__":
    # Removed init_db() call as models.registry is not imported
    print("Database tables creation skipped!")
