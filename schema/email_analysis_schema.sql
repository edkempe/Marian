-- Email analysis schema
DROP TABLE IF EXISTS email_analysis;
CREATE TABLE email_analysis (
    email_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,  -- Gmail thread ID for grouping related emails
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prompt_version TEXT,
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
    links_display TEXT,  -- JSON array
    project TEXT,
    topic TEXT,
    sentiment TEXT,
    confidence_score REAL,
    raw_analysis TEXT  -- Full JSON response
);
