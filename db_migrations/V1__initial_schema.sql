-- V1: Initial Catalog Schema
-- Migration ID: 1
-- Created: 2024-12-24

-- Schema Version Table
CREATE TABLE IF NOT EXISTS schema_versions (
    version INTEGER PRIMARY KEY,
    migration_id TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum TEXT NOT NULL  -- To verify migration integrity
);

-- Initial Schema Version
INSERT INTO schema_versions (version, migration_id, description, checksum) 
VALUES (1, 'V1__initial_schema', 'Initial catalog schema', 'initial');

-- Core Tables
CREATE TABLE IF NOT EXISTS catalog_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    content TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS catalog_tags (
    catalog_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (catalog_id) REFERENCES catalog_items (id),
    FOREIGN KEY (tag_id) REFERENCES tags (id),
    PRIMARY KEY (catalog_id, tag_id)
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

CREATE TABLE IF NOT EXISTS item_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    target_id INTEGER,
    relationship_type TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES catalog_items (id),
    FOREIGN KEY (target_id) REFERENCES catalog_items (id)
);

-- Indexes
CREATE INDEX idx_catalog_items_title ON catalog_items(title);
CREATE INDEX idx_catalog_items_created_at ON catalog_items(created_at);
CREATE INDEX idx_catalog_items_updated_at ON catalog_items(updated_at);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_chat_history_session ON chat_history(session_id);
CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp);
CREATE INDEX idx_relationships_source ON item_relationships(source_id);
CREATE INDEX idx_relationships_target ON item_relationships(target_id);
