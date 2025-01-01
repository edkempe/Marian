"""Error message constants."""

from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class ErrorMessageConstants:
    """Error message constants."""

    # Database errors
    DATABASE: Dict[str, str] = field(default_factory=lambda: {
        "connection_failed": "Failed to connect to database: {error}",
        "query_failed": "Database query failed: {error}",
        "transaction_failed": "Database transaction failed: {error}",
        "migration_failed": "Database migration failed: {error}",
    })

    # API errors
    API: Dict[str, str] = field(default_factory=lambda: {
        "request_failed": "API request failed: {error}",
        "response_invalid": "Invalid API response: {error}",
        "authentication_failed": "API authentication failed: {error}",
        "rate_limit_exceeded": "API rate limit exceeded: {error}",
    })

    # Email errors
    EMAIL: Dict[str, str] = field(default_factory=lambda: {
        "send_failed": "Failed to send email: {error}",
        "receive_failed": "Failed to receive email: {error}",
        "parse_failed": "Failed to parse email: {error}",
        "attachment_failed": "Failed to process email attachment: {error}",
    })

    # File system errors
    FILE: Dict[str, str] = field(default_factory=lambda: {
        "not_found": "File not found: {path}",
        "permission_denied": "Permission denied: {path}",
        "read_failed": "Failed to read file: {error}",
        "write_failed": "Failed to write file: {error}",
    })

    # Configuration errors
    CONFIG: Dict[str, str] = field(default_factory=lambda: {
        "missing_key": "Missing configuration key: {key}",
        "invalid_value": "Invalid configuration value: {value}",
        "load_failed": "Failed to load configuration: {error}",
        "save_failed": "Failed to save configuration: {error}",
    })

    # Security errors
    SECURITY: Dict[str, str] = field(default_factory=lambda: {
        "authentication_failed": "Authentication failed: {error}",
        "authorization_failed": "Authorization failed: {error}",
        "token_invalid": "Invalid token: {error}",
        "token_expired": "Token expired: {error}",
    })

    def __getitem__(self, key: str) -> Dict[str, str]:
        """Make the class subscriptable."""
        return getattr(self, key)

# Singleton instance
ErrorMessages = ErrorMessageConstants()
