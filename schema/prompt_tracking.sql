-- Prompt tracking system schema

CREATE TABLE IF NOT EXISTS prompts (
    prompt_id TEXT PRIMARY KEY,
    prompt_text TEXT NOT NULL,
    version_number TEXT NOT NULL,
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active INTEGER NOT NULL DEFAULT 1,
    model_name TEXT NOT NULL,
    max_tokens INTEGER NOT NULL,
    temperature REAL,
    description TEXT NOT NULL,
    script_name TEXT NOT NULL,
    
    -- Configuration
    expected_response_format TEXT NOT NULL,  -- JSON schema of expected response
    required_input_fields TEXT NOT NULL,     -- Array of required parameters
    token_estimate INTEGER NOT NULL,         -- Approximate tokens needed
    
    -- Usage Statistics (updated periodically)
    last_used_date TIMESTAMP,
    times_used INTEGER DEFAULT 0,
    average_confidence_score REAL,
    average_response_time_ms REAL,
    failure_rate REAL DEFAULT 0.0
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_prompts_active ON prompts(active);
CREATE INDEX IF NOT EXISTS idx_prompts_version ON prompts(version_number);

-- Add prompt tracking columns to email_triage if they don't exist
CREATE TABLE IF NOT EXISTS email_triage (
    email_id TEXT PRIMARY KEY,
    analysis_json TEXT,
    processed_at TIMESTAMP,
    prompt_id TEXT REFERENCES prompts(prompt_id),
    raw_prompt_text TEXT,
    FOREIGN KEY (email_id) REFERENCES emails (id)
);

-- View for prompt performance analytics
CREATE VIEW IF NOT EXISTS prompt_performance AS
SELECT 
    p.prompt_id,
    p.version_number,
    p.model_name,
    COUNT(et.email_id) as total_uses,
    AVG(CAST(json_extract(et.analysis_json, '$.confidence_score') AS REAL)) as avg_confidence,
    p.average_response_time_ms,
    p.failure_rate,
    MAX(et.processed_at) as last_used
FROM prompts p
LEFT JOIN email_triage et ON p.prompt_id = et.prompt_id
GROUP BY p.prompt_id;
