"""Initialize database for testing and development."""

import os
from pathlib import Path
from sqlalchemy import create_engine

from models.registry import Base
from config.settings.database import database_settings
from config.test_settings import test_settings

def init_databases():
    """Initialize databases."""
    # Ensure directories exist
    test_settings.TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    # Initialize test database
    test_url = "sqlite:///tests/test_data/test.db"
    print(f"Initializing test database...")
    test_engine = create_engine(test_url)
    Base.metadata.create_all(test_engine)
    test_engine.dispose()
    
    # Initialize development database
    print(f"Initializing development database...")
    dev_engine = create_engine(database_settings.DATABASE_URL)
    Base.metadata.create_all(dev_engine)
    dev_engine.dispose()

if __name__ == "__main__":
    init_databases()
