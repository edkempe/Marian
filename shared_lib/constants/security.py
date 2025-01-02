"""Security-related constants."""

from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class SecurityConstants:
    """Security-related constants."""
    
    # Password Requirements
    MIN_PASSWORD_LENGTH: int = 12
    MAX_PASSWORD_LENGTH: int = 128
    PASSWORD_COMPLEXITY: Dict[str, int] = field(default_factory=lambda: {
        "uppercase": 1,
        "lowercase": 1,
        "numbers": 1,
        "special": 1,
    })
    
    # Session Settings
    SESSION_TIMEOUT: int = 3600  # 1 hour
    MAX_SESSIONS: int = 5
    SESSION_COOKIE: str = "session_id"
    
    # Rate Limiting
    RATE_LIMIT: Dict[str, str] = field(default_factory=lambda: {
        "default": "100/hour",
        "login": "5/minute",
        "api": "1000/day",
    })
    
    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = field(default_factory=lambda: {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
    })
    
    # Authentication
    TOKEN_EXPIRY: int = 86400  # 24 hours
    REFRESH_TOKEN_EXPIRY: int = 2592000  # 30 days
    MAX_LOGIN_ATTEMPTS: int = 3
    LOCKOUT_DURATION: int = 900  # 15 minutes

# Singleton instance
SECURITY = SecurityConstants()
