"""Database session utilities."""

import logging
from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from shared_lib.constants import DATABASE_CONFIG

logger = logging.getLogger(__name__)


def get_engine_for_db_type(db_type: str) -> Engine:
    """Get SQLAlchemy engine for a database type.
    
    Args:
        db_type: Type of database ('email', 'analysis', or 'catalog')
        
    Returns:
        SQLAlchemy Engine instance
        
    Raises:
        ValueError: If db_type is invalid
    """
    if db_type not in DATABASE_CONFIG:
        raise ValueError(f"Invalid database type: {db_type}")
        
    return create_engine(DATABASE_CONFIG[db_type]["url"])


def get_session_factory(db_path: str) -> sessionmaker:
    """Get a session factory for a database."""
    try:
        engine = create_engine(f"sqlite:///{db_path}")
        session_factory = sessionmaker(bind=engine)
        return session_factory
    except Exception as e:
        logger.error(f"Failed to create session factory: {e}")
        raise


@contextmanager
def get_session(db_path: str) -> Generator[Session, Any, None]:
    """Get a database session."""
    session_factory = get_session_factory(db_path)
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database session error for {db_path}: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        logger.debug(f"Session closed for {db_path}")


# Create engines using get_engine_for_db_type
try:
    email_engine = get_engine_for_db_type("email")
    analysis_engine = get_engine_for_db_type("analysis")
    catalog_engine = get_engine_for_db_type("catalog")
except Exception as e:
    logger.error(f"Failed to create database engines: {e}")
    raise

# Create session factories
EmailSession = sessionmaker(bind=email_engine)
AnalysisSession = sessionmaker(bind=analysis_engine)
CatalogSession = sessionmaker(bind=catalog_engine)


def get_email_session_raw() -> Session:
    """Get a raw SQLAlchemy session for the email database.

    Note: Caller is responsible for session management (commit/rollback/close).
    For automatic session management, use get_email_session() context manager instead.
    """
    try:
        session = EmailSession()
        return session
    except Exception as e:
        logger.error("Failed to create raw email session: {str(e)}")
        raise


@contextmanager
def get_email_session() -> Generator[Session, Any, None]:
    """Get a database session for email operations with automatic management.

    This context manager automatically handles commit, rollback, and cleanup.
    """
    session = EmailSession()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Email session error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        logger.debug("Email session closed")


@contextmanager
def get_analysis_session() -> Generator[Session, Any, None]:
    """Get a database session for analysis operations with automatic management.

    This context manager automatically handles commit, rollback, and cleanup.
    """
    session = AnalysisSession()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Analysis session error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        logger.debug("Analysis session closed")


@contextmanager
def get_catalog_session() -> Generator[Session, Any, None]:
    """Get a database session for catalog operations with automatic management.

    This context manager automatically handles commit, rollback, and cleanup.
    """
    session = CatalogSession()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Catalog session error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        logger.debug("Catalog session closed")


if __name__ == "__main__":
    logger.info("Database session utilities loaded successfully!")
