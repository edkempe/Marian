-- V2: Add Status and User Tracking
-- Migration ID: 2
-- Created: 2024-12-24

-- Update Schema Version
INSERT INTO schema_versions (version, migration_id, description, checksum) 
VALUES (2, 'V2__add_status_and_tracking', 'Add status and user tracking fields', 'v2');

-- Add Status and User Tracking to Catalog Items
ALTER TABLE catalog_items ADD COLUMN status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived'));
ALTER TABLE catalog_items ADD COLUMN created_by TEXT;
ALTER TABLE catalog_items ADD COLUMN updated_by TEXT;

-- Add Status Index
CREATE INDEX idx_catalog_items_status ON catalog_items(status);
