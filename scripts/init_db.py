#!/usr/bin/env python3
"""Initialize database tables."""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from models.base import Base
from shared_lib.database_session_util import engine

def init_db():
    """Initialize database tables."""
    # Drop all existing tables
    Base.metadata.drop_all(engine)
    
    # Create tables
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")
