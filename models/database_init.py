"""Database initialization and management."""

from pathlib import Path
from typing import Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.registry import Base
from shared_lib.constants import CONFIG
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
        testing: If True, use test databases
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
    """Get SQLite engines for testing.

    Returns:
        Tuple of (email_engine, analysis_engine, catalog_engine)
    """
    # Ensure test data directory exists
    test_data_dir = Path("tests/test_data")
    test_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create engines with file-based databases
    email_engine = create_engine(f"sqlite:///{test_data_dir}/test_email.db", echo=False)
    analysis_engine = create_engine(f"sqlite:///{test_data_dir}/test_analysis.db", echo=False)
    catalog_engine = create_engine(f"sqlite:///{test_data_dir}/test_catalog.db", echo=False)

    return email_engine, analysis_engine, catalog_engine


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")
