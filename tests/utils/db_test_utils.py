"""Database utilities for testing."""

import os
import shutil
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import Base
from shared_lib.constants import ROOT_DIR, TESTING_CONFIG

@contextmanager
def create_test_db_session() -> Generator[Session, None, None]:
    """Create a test database session with proper cleanup.
    
    This context manager:
    1. Creates a test database file
    2. Sets up SQLAlchemy session
    3. Yields the session for test use
    4. Cleans up the database file after tests
    
    Yields:
        SQLAlchemy session
    """
    # Create test database
    test_db_path = os.path.join(ROOT_DIR, TESTING_CONFIG["TEST_DB_PATH"])
    test_db_dir = os.path.dirname(test_db_path)
    
    try:
        # Ensure test directory exists
        os.makedirs(test_db_dir, exist_ok=True)
        
        # Initialize database
        engine = create_engine(f"sqlite:///{test_db_path}")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        yield session
        
        session.close()
        
    finally:
        # Always clean up
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        if os.path.exists(test_db_dir):
            shutil.rmtree(test_db_dir)
