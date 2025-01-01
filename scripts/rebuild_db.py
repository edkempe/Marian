"""Initialize all databases for testing and development."""

import os
from pathlib import Path
from sqlalchemy import create_engine

from models.registry import Base
from config.test_settings import test_settings

def init_databases():
    """Initialize all databases."""
    # Ensure directories exist
    test_settings.TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    # Initialize test databases
    test_dbs = {
        "test": "sqlite:///tests/test_data/test.db",
        "test_email": "sqlite:///tests/test_data/test_email.db",
        "test_analysis": "sqlite:///tests/test_data/test_analysis.db",
        "test_catalog": "sqlite:///tests/test_data/test_catalog.db"
    }
    
    # Initialize development databases
    dev_dbs = {
        "email": "sqlite:///data/email.db",
        "analysis": "sqlite:///data/analysis.db",
        "catalog": "sqlite:///data/catalog.db"
    }
    
    # Create all databases
    for name, url in {**test_dbs, **dev_dbs}.items():
        print(f"Initializing {name} database...")
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        engine.dispose()

if __name__ == "__main__":
    init_databases()
