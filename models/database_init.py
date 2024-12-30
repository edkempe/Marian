"""Database initialization and management."""

from typing import Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.registry import Base
from shared_lib.constants import DATABASE_CONFIG
from shared_lib.database_session_util import (
    AnalysisSession,
    CatalogSession,
    EmailSession,
    analysis_engine,
    catalog_engine,
    email_engine,
)


def init_db(testing: bool = False) -> None:
    """Initialize all database tables.

    Creates all tables defined in the SQLAlchemy models if they don't exist.
    This is safe to run multiple times as it will not recreate existing tables.

    Args:
        testing: If True, use in-memory databases for testing
    """
    if testing:
        engines = get_test_engines()
        for engine in engines:
            Base.metadata.create_all(engine)
    else:
        Base.metadata.create_all(email_engine)
        Base.metadata.create_all(analysis_engine)
        Base.metadata.create_all(catalog_engine)


def get_test_engines() -> Tuple[create_engine, create_engine, create_engine]:
    """Get SQLite in-memory engines for testing.

    Returns:
        Tuple of (email_engine, analysis_engine, catalog_engine)
    """
    email_engine = create_engine("sqlite:///:memory:", echo=False)
    analysis_engine = create_engine("sqlite:///:memory:", echo=False)
    catalog_engine = create_engine("sqlite:///:memory:", echo=False)

    return email_engine, analysis_engine, catalog_engine


def get_test_sessions() -> Tuple[sessionmaker, sessionmaker, sessionmaker]:
    """Get session factories for test databases.

    Returns:
        Tuple of (EmailSession, AnalysisSession, CatalogSession)
    """
    engines = get_test_engines()
    return tuple(sessionmaker(bind=engine) for engine in engines)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")
