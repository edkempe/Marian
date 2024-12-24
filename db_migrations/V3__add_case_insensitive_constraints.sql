-- Add case-insensitive unique constraints to catalog_items and tags tables

-- Temporarily disable foreign key constraints
PRAGMA foreign_keys=OFF;

-- Create new catalog_items table with case-insensitive constraint
CREATE TABLE catalog_items_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL COLLATE NOCASE,
    description TEXT,
    content TEXT,
    deleted INTEGER DEFAULT 0,
    archived_date INTEGER,
    created_date INTEGER DEFAULT (strftime('%s', 'now')),
    modified_date INTEGER DEFAULT (strftime('%s', 'now')),
    UNIQUE(title) ON CONFLICT FAIL
);

-- Copy data from old table
INSERT INTO catalog_items_new 
SELECT * FROM catalog_items;

-- Drop old table and rename new one
DROP TABLE catalog_items;
ALTER TABLE catalog_items_new RENAME TO catalog_items;

-- Create new tags table with case-insensitive constraint
CREATE TABLE tags_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL COLLATE NOCASE,
    deleted INTEGER DEFAULT 0,
    archived_date INTEGER,
    created_date INTEGER DEFAULT (strftime('%s', 'now')),
    modified_date INTEGER DEFAULT (strftime('%s', 'now')),
    UNIQUE(name) ON CONFLICT FAIL
);

-- Copy data from old table
INSERT INTO tags_new 
SELECT * FROM tags;

-- Drop old table and rename new one
DROP TABLE tags;
ALTER TABLE tags_new RENAME TO tags;

-- Re-enable foreign key constraints
PRAGMA foreign_keys=ON;

-- Add indexes for commonly searched fields
CREATE INDEX IF NOT EXISTS idx_catalog_items_title ON catalog_items(title COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_deleted_items ON catalog_items(deleted);
CREATE INDEX IF NOT EXISTS idx_deleted_tags ON tags(deleted);
