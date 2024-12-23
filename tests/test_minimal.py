"""Minimal test to isolate the stalling issue."""
import pytest
import sqlite3
import os
from unittest.mock import MagicMock

# Test database path
TEST_DB = "test_minimal.db"

@pytest.fixture(scope="function")
def setup_db():
    """Set up test database."""
    print("\nSetting up test database...")
    
    # Create and initialize database
    conn = sqlite3.connect(TEST_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS test_table
                 (id TEXT PRIMARY KEY,
                  value TEXT)''')
    conn.commit()
    conn.close()
    print("Database initialized")
    
    yield
    
    # Clean up
    print("\nCleaning up...")
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
            print(f"Removed {TEST_DB}")
        except Exception as e:
            print(f"Error removing {TEST_DB}: {e}")

def test_basic_db_operations(setup_db):
    """Test basic database operations."""
    print("\nStarting basic test...")
    
    # Connect to database
    conn = sqlite3.connect(TEST_DB)
    c = conn.cursor()
    
    # Insert test data
    c.execute("INSERT INTO test_table VALUES (?, ?)", ("test1", "value1"))
    conn.commit()
    
    # Query test data
    c.execute("SELECT * FROM test_table WHERE id = ?", ("test1",))
    result = c.fetchone()
    
    # Close connection
    conn.close()
    
    # Assert results
    assert result is not None
    assert result[0] == "test1"
    assert result[1] == "value1"
    print("Test completed successfully")
