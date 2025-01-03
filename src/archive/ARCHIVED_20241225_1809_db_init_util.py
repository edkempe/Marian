#!/usr/bin/env python3
"""Database initialization utilities."""
import os

from sqlalchemy import text

from models.base import Base
from models.email import Email
from models.email_analysis import EmailAnalysis
from shared_lib.database_session_util import analysis_engine, email_engine


def init_db():
    """Initialize the databases."""
    # Create email tables
    Base.metadata.create_all(email_engine)
    print("Email database initialized.")

    # Create analysis tables
    Base.metadata.create_all(analysis_engine)
    print("Analysis database initialized.")


if __name__ == "__main__":
    init_db()
