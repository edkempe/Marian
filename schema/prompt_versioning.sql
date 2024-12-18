-- Prompt versioning system schema

CREATE TABLE IF NOT EXISTS prompt_versions (
    prompt_id TEXT PRIMARY KEY,
    prompt_version TEXT NOT NULL,
    prompt_name TEXT NOT NULL,
    prompt_template TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Parameters
    required_parameters JSON NOT NULL,
    optional_parameters JSON,
    max_input_tokens INTEGER,
    expected_output_format JSON,
    
    -- Model Configuration
    model_name TEXT NOT NULL,
    max_tokens INTEGER,
    temperature REAL,
    other_model_params JSON,
    
    -- Usage Statistics
    last_used_at TIMESTAMP,
    total_uses INTEGER DEFAULT 0,
    average_response_time REAL,
    error_rate REAL,
    
    -- Validation and Fallback
    validation_rules JSON,
    success_criteria JSON,
    fallback_prompt_id TEXT,
    
    FOREIGN KEY (fallback_prompt_id) REFERENCES prompt_versions (prompt_id)
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_prompt_versions_name ON prompt_versions(prompt_name);
CREATE INDEX IF NOT EXISTS idx_prompt_versions_active ON prompt_versions(is_active);

-- Table to track prompt usage in email analysis
CREATE TABLE IF NOT EXISTS email_prompt_usage (
    usage_id TEXT PRIMARY KEY,
    email_id TEXT NOT NULL,
    prompt_id TEXT NOT NULL,
    used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    was_successful BOOLEAN,
    error_message TEXT,
    
    FOREIGN KEY (email_id) REFERENCES emails (id),
    FOREIGN KEY (prompt_id) REFERENCES prompt_versions (prompt_id)
);

-- Index for tracking prompt usage
CREATE INDEX IF NOT EXISTS idx_email_prompt_usage_email ON email_prompt_usage(email_id);
CREATE INDEX IF NOT EXISTS idx_email_prompt_usage_prompt ON email_prompt_usage(prompt_id);

-- View for prompt usage analytics
CREATE VIEW IF NOT EXISTS prompt_usage_analytics AS
SELECT 
    pv.prompt_name,
    pv.prompt_version,
    COUNT(epu.usage_id) as total_uses,
    AVG(CASE WHEN epu.was_successful THEN 1 ELSE 0 END) as success_rate,
    AVG(epu.response_time_ms) as avg_response_time_ms,
    MAX(epu.used_at) as last_used_at
FROM prompt_versions pv
LEFT JOIN email_prompt_usage epu ON pv.prompt_id = epu.prompt_id
GROUP BY pv.prompt_id, pv.prompt_name, pv.prompt_version;
