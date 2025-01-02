"""Verify database schema."""

import os
import sqlite3
from typing import Dict, Set

from config.settings.database import database_settings

# Database configuration
DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATABASE_PATH = os.path.join(DATABASE_DIR, "jexi.db")

# Expected tables and their columns
EXPECTED_TABLES = {
    "email_messages": {
        "id": "TEXT",
        "thread_id": "TEXT",
        "message_id": "TEXT",
        "subject": "TEXT",
        "body": "TEXT",
        "snippet": "TEXT",
        "from_address": "TEXT",
        "to_address": "TEXT",
        "cc_address": "TEXT",
        "bcc_address": "TEXT",
        "received_at": "DATETIME",
        "history_id": "TEXT",
        "has_attachments": "INTEGER",
        "is_read": "INTEGER",
        "is_important": "INTEGER",
        "labels": "TEXT",
        "full_api_response": "TEXT",
        "created_at": "DATETIME",
        "updated_at": "DATETIME"
    },
    "email_analysis": {
        "id": "TEXT",
        "email_id": "TEXT",
        "sentiment": "TEXT",
        "categories": "TEXT",
        "summary": "TEXT",
        "key_points": "TEXT",
        "action_items": "TEXT",
        "priority_score": "TEXT",
        "confidence_score": "TEXT",
        "model_version": "TEXT",
        "analysis_metadata": "TEXT",
        "analyzed_at": "DATETIME",
        "created_at": "DATETIME",
        "updated_at": "DATETIME"
    },
    "gmail_labels": {
        "id": "TEXT",
        "name": "TEXT",
        "type": "TEXT",
        "message_list_visibility": "TEXT",
        "label_list_visibility": "TEXT",
        "messages_total": "INTEGER",
        "messages_unread": "INTEGER",
        "threads_total": "INTEGER",
        "threads_unread": "INTEGER",
        "created_at": "DATETIME",
        "updated_at": "DATETIME"
    },
    "catalog_items": {
        "id": "TEXT",
        "name": "TEXT",
        "description": "TEXT",
        "type": "TEXT",
        "status": "TEXT",
        "metadata": "TEXT",
        "created_at": "DATETIME",
        "updated_at": "DATETIME"
    },
    "tags": {
        "id": "TEXT",
        "name": "TEXT",
        "description": "TEXT",
        "created_at": "DATETIME",
        "updated_at": "DATETIME"
    },
    "item_relationships": {
        "id": "TEXT",
        "source_id": "TEXT",
        "target_id": "TEXT",
        "relationship_type": "TEXT",
        "metadata": "TEXT",
        "created_at": "DATETIME",
        "updated_at": "DATETIME"
    }
}

def get_existing_tables(conn: sqlite3.Connection) -> Set[str]:
    """Get existing tables in database."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return {row[0] for row in cursor.fetchall()}

def get_table_columns(conn: sqlite3.Connection, table: str) -> Dict[str, str]:
    """Get columns and their types for a table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1]: row[2] for row in cursor.fetchall()}

def verify_database_schema() -> None:
    """Verify database schema."""
    print(f"\nVerifying database at {database_settings.DATABASE_PATH}")
    
    # Connect to database
    conn = sqlite3.connect(database_settings.DATABASE_PATH)
    
    try:
        # Get existing tables
        existing_tables = get_existing_tables(conn)
        
        # Check for missing tables
        missing_tables = set(EXPECTED_TABLES.keys()) - existing_tables
        if missing_tables:
            print(f"\nMissing tables: {missing_tables}")
        
        # Check table schemas
        for table in existing_tables:
            if table not in EXPECTED_TABLES:
                print(f"\nUnexpected table: {table}")
                continue
                
            columns = get_table_columns(conn, table)
            expected_columns = EXPECTED_TABLES[table]
            
            # Check for missing columns
            missing_columns = set(expected_columns.keys()) - set(columns.keys())
            if missing_columns:
                print(f"\nMissing columns in {table}: {missing_columns}")
            
            # Check column types
            for col, type_ in columns.items():
                if col in expected_columns and expected_columns[col] != type_:
                    print(f"\nType mismatch in {table}.{col}: expected {expected_columns[col]}, got {type_}")
        
        if not missing_tables and all(table in EXPECTED_TABLES for table in existing_tables):
            print("\nDatabase schema verification completed successfully!")
        else:
            print("\nDatabase schema verification completed with errors.")
            
    finally:
        conn.close()

if __name__ == "__main__":
    verify_database_schema()
