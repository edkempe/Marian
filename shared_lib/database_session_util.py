"""Database session utilities."""

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings.database import database_settings
from shared_lib.constants import CONFIG


logger = logging.getLogger(__name__)


class EmailSession(Session):
    """Custom session class for email database."""
    
    def __init__(self, *args, **kwargs):
        """Initialize email session with custom settings."""
        super().__init__(*args, **kwargs)
        self.email_config = CONFIG["DATABASE"]["email"]
    
    def get_batch_size(self) -> int:
        """Get configured batch size for email operations."""
        return self.email_config.get("batch_size", 100)


class AnalysisSession(Session):
    """Custom session class for analysis database."""
    
    def __init__(self, *args, **kwargs):
        """Initialize analysis session with custom settings."""
        super().__init__(*args, **kwargs)
        self.analysis_config = CONFIG["DATABASE"]["analysis"]
    
    def get_timeout(self) -> int:
        """Get configured timeout for analysis operations."""
        return self.analysis_config.get("timeout", 60)


class CatalogSession(Session):
    """Custom session class for catalog database."""
    
    def __init__(self, *args, **kwargs):
        """Initialize catalog session with custom settings."""
        super().__init__(*args, **kwargs)
        self.catalog_config = CONFIG["DATABASE"]["catalog"]
    
    def get_batch_size(self) -> int:
        """Get configured batch size for catalog operations."""
        return self.catalog_config.get("batch_size", 100)
    
    def get_max_retries(self) -> int:
        """Get configured maximum retry attempts."""
        return self.catalog_config.get("max_retries", 3)


def get_engine(db_url: str = None) -> Engine:
    """Get SQLAlchemy engine using configured settings.
    
    Args:
        db_url: Optional database URL. If not provided, uses configured URL.
    
    Returns:
        SQLAlchemy Engine instance
    """
    if db_url is None:
        db_url = str(database_settings.URL)
    
    return create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=database_settings.ECHO_SQL
    )


def get_session_factory(db_url: str = None, session_class: type = Session) -> sessionmaker:
    """Get a session factory for a database.
    
    Args:
        db_url: Optional database URL. If not provided, uses configured URL.
        session_class: Optional session class to use. Defaults to Session.
    
    Returns:
        SQLAlchemy sessionmaker instance
    """
    engine = get_engine(db_url)
    return sessionmaker(
        bind=engine,
        class_=session_class,
        expire_on_commit=False,
        autocommit=False,
        autoflush=True
    )


@contextmanager
def get_session(db_url: str = None, session_class: type = Session) -> Generator[Session, None, None]:
    """Get a database session with automatic management.
    
    Args:
        db_url: Optional database URL. If not provided, uses configured URL.
        session_class: Optional session class to use. Defaults to Session.
    
    Yields:
        SQLAlchemy Session
    """
    Session = get_session_factory(db_url, session_class)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_test_session() -> Generator[Session, None, None]:
    """Get a database session for testing.
    
    Uses file-based SQLite database for testing.
    
    Yields:
        SQLAlchemy Session
    """
    test_db_path = Path("tests/test_data/test_default.db")
    test_db_path.parent.mkdir(parents=True, exist_ok=True)
    
    with get_session(f"sqlite:///{test_db_path}") as session:
        yield session


@contextmanager
def get_email_session() -> Generator[EmailSession, None, None]:
    """Get a session for the email database.
    
    Yields:
        EmailSession
    """
    with get_session(
        db_url=str(database_settings.EMAIL_DB_URL),
        session_class=EmailSession
    ) as session:
        yield session


@contextmanager
def get_analysis_session() -> Generator[AnalysisSession, None, None]:
    """Get a session for the analysis database.
    
    Yields:
        AnalysisSession
    """
    with get_session(
        db_url=str(database_settings.ANALYSIS_DB_URL),
        session_class=AnalysisSession
    ) as session:
        yield session


@contextmanager
def get_catalog_session() -> Generator[CatalogSession, None, None]:
    """Get a session for the catalog database.
    
    Yields:
        CatalogSession
    """
    with get_session(
        db_url=str(database_settings.CATALOG_DB_URL),
        session_class=CatalogSession
    ) as session:
        yield session


def get_engine_for_db_type(db_type: str) -> Engine:
    """Get SQLAlchemy engine for a specific database type.
    
    Args:
        db_type: Type of database to get engine for (email, analysis, catalog)
    
    Returns:
        SQLAlchemy Engine instance
    """
    if db_type == "email":
        url = str(database_settings.EMAIL_DB_URL)
    elif db_type == "analysis":
        url = str(database_settings.ANALYSIS_DB_URL)
    elif db_type == "catalog":
        url = str(database_settings.CATALOG_DB_URL)
    else:
        url = str(database_settings.URL)
    
    return get_engine(url)


# Create engines for each database type
email_engine = get_engine_for_db_type("email")
analysis_engine = get_engine_for_db_type("analysis")
catalog_engine = get_engine_for_db_type("catalog")

# Create session factories
EmailSessionFactory = get_session_factory(
    str(database_settings.EMAIL_DB_URL),
    EmailSession
)
AnalysisSessionFactory = get_session_factory(
    str(database_settings.ANALYSIS_DB_URL),
    AnalysisSession
)
CatalogSessionFactory = get_session_factory(
    str(database_settings.CATALOG_DB_URL),
    CatalogSession
)
