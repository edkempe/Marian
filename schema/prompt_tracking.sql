-- Prompt tracking system schema

-- Store prompt definitions and metadata
CREATE TABLE IF NOT EXISTS prompts (
    prompt_id TEXT PRIMARY KEY,
    prompt_name TEXT NOT NULL,      -- Format: script.purpose.task
    prompt_text TEXT NOT NULL,
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active INTEGER NOT NULL DEFAULT 1,
    model_name TEXT NOT NULL,
    max_tokens INTEGER NOT NULL,
    temperature REAL,
    description TEXT NOT NULL,
    script_name TEXT NOT NULL,
    purpose TEXT NOT NULL,          -- Specific purpose within the script (e.g., 'classify', 'analyze')
    task TEXT NOT NULL,            -- Specific task (e.g., 'subject', 'body')
    
    -- Configuration
    expected_response_format TEXT NOT NULL,  -- JSON schema of expected response
    required_input_fields TEXT NOT NULL,     -- Array of required parameters
    token_estimate INTEGER NOT NULL         -- Approximate tokens needed
);

-- Indexes for quick lookups
CREATE INDEX IF NOT EXISTS idx_prompts_active ON prompts(active);
CREATE INDEX IF NOT EXISTS idx_prompts_name ON prompts(prompt_name);
CREATE INDEX IF NOT EXISTS idx_prompts_purpose ON prompts(script_name, purpose, task);

-- Store email analysis results
CREATE TABLE IF NOT EXISTS email_triage (
    email_id TEXT PRIMARY KEY,
    analysis_json TEXT,
    processed_at TIMESTAMP,
    prompt_id TEXT NOT NULL,
    prompt_name TEXT NOT NULL,
    purpose TEXT NOT NULL,
    task TEXT NOT NULL,
    raw_prompt_text TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts (prompt_id)
);

-- Store all API calls and their results
CREATE TABLE IF NOT EXISTS prompt_calls (
    call_id TEXT PRIMARY KEY,
    prompt_id TEXT NOT NULL,
    prompt_name TEXT NOT NULL,
    script_name TEXT NOT NULL,
    purpose TEXT NOT NULL,
    task TEXT NOT NULL,
    call_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    input_data TEXT NOT NULL,      -- JSON of input parameters
    raw_prompt TEXT NOT NULL,      -- Actual prompt sent to API
    response TEXT,                -- Raw API response
    response_time_ms INTEGER,
    confidence_score REAL,
    success INTEGER NOT NULL,     -- 1 if successful, 0 if failed
    error_message TEXT,           -- Error message if failed
    FOREIGN KEY (prompt_id) REFERENCES prompts (prompt_id)
);

-- View for prompt performance analytics
CREATE VIEW IF NOT EXISTS prompt_performance AS
SELECT 
    p.prompt_id,
    p.prompt_name,
    p.script_name,
    p.purpose,
    p.task,
    COUNT(pc.call_id) as total_calls,
    AVG(CASE WHEN pc.success = 1 THEN 1.0 ELSE 0.0 END) as success_rate,
    AVG(pc.response_time_ms) as avg_response_time_ms,
    AVG(pc.confidence_score) as avg_confidence_score,
    MAX(pc.call_time) as last_used
FROM prompts p
LEFT JOIN prompt_calls pc ON p.prompt_id = pc.prompt_id
GROUP BY p.prompt_id;
