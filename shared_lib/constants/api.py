"""API-related constants."""

from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(frozen=True)
class ApiConstants:
    """API-related constants."""
    
    # API configuration
    CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "version": "v1",
        "base_url": "http://localhost:8000",
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 5,
    })
    
    # API endpoints
    ENDPOINTS: Dict[str, str] = field(default_factory=lambda: {
        "email": "/api/v1/email",
        "analysis": "/api/v1/analysis",
        "catalog": "/api/v1/catalog",
    })
    
    # API methods
    METHODS: Dict[str, str] = field(default_factory=lambda: {
        "GET": "get",
        "POST": "post",
        "PUT": "put",
        "DELETE": "delete",
    })
    
    # API response codes
    RESPONSE_CODES: Dict[int, str] = field(default_factory=lambda: {
        200: "OK",
        201: "Created",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error",
    })
    
    def __getitem__(self, key: str) -> Any:
        """Make the class subscriptable."""
        if key in self.CONFIG:
            return self.CONFIG[key]
        return getattr(self, key)

# Singleton instance
API = ApiConstants()
API_CONFIG = API  # For backward compatibility
