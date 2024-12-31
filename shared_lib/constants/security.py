"""Security-related constants."""

# Password Requirements
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128
PASSWORD_COMPLEXITY = {
    "uppercase": 1,
    "lowercase": 1,
    "numbers": 1,
    "special": 1,
}

# Session Settings
SESSION_TIMEOUT = 3600  # 1 hour
MAX_SESSIONS = 5
SESSION_COOKIE = "session_id"

# Rate Limiting
RATE_LIMIT = {
    "default": "100/hour",
    "login": "5/minute",
    "api": "1000/day",
}
