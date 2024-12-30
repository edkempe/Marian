"""Database session utilities."""

import logging
from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from shared_lib.constants import DATABASE_CONFIG

logger = logging.getLogger(__name__)


def get_session_factory(db_path: str) -> sessionmaker:
    """Get a session factory for a database."""
    try:
        engine = create_engine(f"sqlite:///{db_path}")
        session_factory = sessionmaker(bind=engine)
        return session_factory
    except Exception as e:
        logging.error(f"Failed to create session factory for {db_path}: {str(e)}")
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
        logging.error(f"Database session error for {db_path}: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        logging.debug(f"Session closed for {db_path}")


# Create engines using URLs from constants
try:
    email_engine = create_engine(
        f"sqlite:///{DATABASE_CONFIG['email']['path']}", echo=False
    )
    analysis_engine = create_engine(
        f"sqlite:///{DATABASE_CONFIG['analysis']['path']}", echo=False
    )
    catalog_engine = create_engine(
        f"sqlite:///{DATABASE_CONFIG['catalog']['path']}", echo=False
    )
except Exception as e:
    logging.error(f"Failed to create database engines: {str(e)}")
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
        logging.error("Failed to create raw email session: {str(e)}")
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
        logging.error(f"Email session error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        logging.debug("Email session closed")


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
        logging.error(f"Analysis session error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        logging.debug("Analysis session closed")


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
        logging.error(f"Catalog session error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        logging.debug("Catalog session closed")


def init_db():
    """Initialize all database tables.

    Creates all tables defined in the SQLAlchemy models if they don't exist.
    This is safe to run multiple times as it will not recreate existing tables.
    """
    try:
        from models.registry import Base

        Base.metadata.create_all(email_engine)
        Base.metadata.create_all(analysis_engine)
        Base.metadata.create_all(catalog_engine)
    except Exception as e:
        logging.error(f"Failed to initialize database tables: {str(e)}")
        raise


if __name__ == "__main__":
    # Removed init_db() call as models.registry is not imported
    logging.info("Database tables creation skipped!")
