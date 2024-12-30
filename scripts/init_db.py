#!/usr/bin/env python3
"""Initialize all database tables."""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from models.base import Base
from shared_lib.database_session_util import (
    analysis_engine,
    catalog_engine,
    email_engine,
    get_analysis_session,
    get_catalog_session,
    get_email_session,
)


def init_db():
    """Initialize all database tables."""
    # Create tables in email database
    with get_email_session() as session:
        Base.metadata.create_all(email_engine)
        session.commit()

    # Create tables in analysis database
    with get_analysis_session() as session:
        Base.metadata.create_all(analysis_engine)
        session.commit()

    # Create tables in catalog database
    with get_catalog_session() as session:
        Base.metadata.create_all(catalog_engine)
        session.commit()


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")
