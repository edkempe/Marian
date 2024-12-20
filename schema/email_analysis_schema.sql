-- Email analysis schema
DROP TABLE IF EXISTS email_analysis;
CREATE TABLE email_analysis (
    email_id TEXT PRIMARY KEY,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    summary TEXT,
    category TEXT,  -- JSON array
    priority_score INTEGER,
    priority_reason TEXT,
    action_needed BOOLEAN,
    action_type TEXT,  -- JSON array
    action_deadline TEXT,
    key_points TEXT,  -- JSON array
    people_mentioned TEXT,  -- JSON array
    links_found TEXT,  -- JSON array
    project TEXT,
    topic TEXT,
    ref_docs TEXT,  -- Changed from 'references'
    sentiment TEXT,
    confidence_score REAL,
    raw_analysis TEXT  -- Full JSON response
);
