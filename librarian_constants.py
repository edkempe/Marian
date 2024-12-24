"""Constants for the Marian Librarian/Catalog system."""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class CatalogConfig:
    """Type hints for catalog configuration."""
    CATALOG_DB_FILE: str
    CATALOG_DB_URL: str
    CHAT_LOG_FILE: str
    MAX_ITEMS_PER_PAGE: int
    DEFAULT_SEARCH_LIMIT: int

@dataclass
class TableConfig:
    """Type hints for database table configuration."""
    CATALOG_TABLE: str
    TAGS_TABLE: str
    CATALOG_TAGS_TABLE: str
    CHAT_HISTORY_TABLE: str
    RELATIONSHIPS_TABLE: str

@dataclass
class SearchConfig:
    """Type hints for search configuration."""
    MIN_SEARCH_CHARS: int
    MAX_SEARCH_TERMS: int
    RELEVANCE_THRESHOLD: float
    MAX_RELATED_ITEMS: int

CATALOG_CONFIG = {
    # Database Files and URLs
    'CATALOG_DB_FILE': 'db_catalog.db',
    'CATALOG_DB_URL': 'sqlite:///db_catalog.db',
    'CHAT_LOG_FILE': 'chat_logs.jsonl',
    
    # Pagination and Limits
    'MAX_ITEMS_PER_PAGE': 50,
    'DEFAULT_SEARCH_LIMIT': 10,
}

TABLE_CONFIG = {
    # Table Names
    'CATALOG_TABLE': 'catalog_items',
    'TAGS_TABLE': 'tags',
    'CATALOG_TAGS_TABLE': 'catalog_tags',
    'CHAT_HISTORY_TABLE': 'chat_history',
    'RELATIONSHIPS_TABLE': 'item_relationships'
}

SEARCH_CONFIG = {
    # Search Parameters
    'MIN_SEARCH_CHARS': 3,
    'MAX_SEARCH_TERMS': 10,
    'RELEVANCE_THRESHOLD': 0.7,
    'MAX_RELATED_ITEMS': 5,
}

RELATIONSHIP_TYPES = [
    'related_to',
    'parent_of',
    'child_of',
    'references',
    'referenced_by',
    'derived_from',
    'supersedes',
    'superseded_by',
]

# SQL Queries
CREATE_CATALOG_TABLE = """
CREATE TABLE IF NOT EXISTS catalog_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL COLLATE NOCASE,
    description TEXT,
    content TEXT,
    deleted INTEGER DEFAULT 0,
    archived_date INTEGER,  -- UTC Unix timestamp
    created_date INTEGER DEFAULT (strftime('%s', 'now')),
    modified_date INTEGER DEFAULT (strftime('%s', 'now')),
    UNIQUE(title) ON CONFLICT FAIL
)
"""

CREATE_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL COLLATE NOCASE,
    deleted INTEGER DEFAULT 0,
    archived_date INTEGER,  -- UTC Unix timestamp
    created_date INTEGER DEFAULT (strftime('%s', 'now')),
    modified_date INTEGER DEFAULT (strftime('%s', 'now')),
    UNIQUE(name) ON CONFLICT FAIL
)
"""

CREATE_CATALOG_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS catalog_tags (
    catalog_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (catalog_id) REFERENCES catalog_items (id),
    FOREIGN KEY (tag_id) REFERENCES tags (id),
    PRIMARY KEY (catalog_id, tag_id)
)
"""

CREATE_CHAT_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSON,
    created_date INTEGER DEFAULT (strftime('%s', 'now'))
)
"""

CREATE_RELATIONSHIPS_TABLE = """
CREATE TABLE IF NOT EXISTS item_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    target_id INTEGER,
    relationship_type TEXT NOT NULL,
    metadata JSON,
    created_date INTEGER DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (source_id) REFERENCES catalog_items (id),
    FOREIGN KEY (target_id) REFERENCES catalog_items (id)
)
"""

# Error Messages
ERRORS = {
    'ITEM_NOT_FOUND': 'Item not found in catalog',
    'TAG_NOT_FOUND': 'Tag not found',
    'INVALID_RELATIONSHIP': 'Invalid relationship type',
    'DUPLICATE_ITEM': 'Item already exists in catalog',
    'DUPLICATE_TAG': 'Tag already exists',
    'INVALID_SEARCH': 'Invalid search query',
    'DATABASE_ERROR': 'Database operation failed',
}
