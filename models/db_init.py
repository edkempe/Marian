"""Database initialization utilities."""

import logging

from shared_lib.database_session_util import (
    email_engine,
    analysis_engine,
    catalog_engine,
)
from models.registry import Base


def init_db():
    """Initialize all database tables.

    Creates all tables defined in the SQLAlchemy models if they don't exist.
    This is safe to run multiple times as it will not recreate existing tables.
    """
    try:
        Base.metadata.create_all(email_engine)
        Base.metadata.create_all(analysis_engine)
        Base.metadata.create_all(catalog_engine)
    except Exception as e:
        logging.error(f"Failed to initialize database tables: {str(e)}")
        raise


if __name__ == "__main__":
    init_db()
    logging.info("Database tables created successfully!")
