-- Email analysis schema
DROP TABLE IF EXISTS email_analysis;
CREATE TABLE email_analysis (
    email_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,  -- Gmail thread ID for grouping related emails
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prompt_version TEXT,
    summary TEXT,
    category TEXT,  -- JSON array of categories
    priority_score INTEGER,
    priority_reason TEXT,
    action_needed BOOLEAN,
    action_type TEXT,  -- JSON array of action types
    action_deadline TEXT,  -- Optional YYYY-MM-DD
    key_points TEXT,  -- JSON array of key points
    people_mentioned TEXT,  -- JSON array of people
    links_found TEXT,  -- JSON array of full URLs
    links_display TEXT,  -- JSON array of truncated URLs
    project TEXT,
    topic TEXT,
    sentiment TEXT,
    confidence_score REAL,
    raw_analysis TEXT  -- Full JSON response
);
