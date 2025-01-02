"""API-related constants."""

from dataclasses import dataclass, field
from typing import Dict, Any, Type, Union
from datetime import datetime

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
    
    # API type mappings
    TYPE_MAPPINGS: Dict[str, Type[Union[str, int, float, bool, datetime, list, dict]]] = field(
        default_factory=lambda: {
            # Gmail API types
            "gmail.message.id": str,
            "gmail.message.threadId": str,
            "gmail.message.labelIds": list,
            "gmail.message.snippet": str,
            "gmail.message.historyId": str,
            "gmail.message.internalDate": datetime,
            "gmail.message.sizeEstimate": int,
            "gmail.message.raw": str,
            "gmail.message.payload": dict,
            
            # Anthropic API types
            "anthropic.analysis.id": str,
            "anthropic.analysis.email_id": str,
            "anthropic.analysis.summary": str,
            "anthropic.analysis.sentiment": str,
            "anthropic.analysis.categories": list,
            "anthropic.analysis.key_points": list,
            "anthropic.analysis.action_items": list,
            "anthropic.analysis.priority_score": int,
            "anthropic.analysis.confidence_score": float,
            "anthropic.analysis.metadata": dict,
            "anthropic.analysis.model_version": str,
            "anthropic.analysis.created_at": datetime,
            "anthropic.analysis.updated_at": datetime,
        }
    )
    
    def __getitem__(self, key: str) -> Any:
        """Make the class subscriptable."""
        if key in self.CONFIG:
            return self.CONFIG[key]
        return getattr(self, key)


# Singleton instance
API = ApiConstants()

# Re-export constants
API_CONFIG = API.CONFIG
API_ENDPOINTS = API.ENDPOINTS
API_METHODS = API.METHODS
API_RESPONSE_CODES = API.RESPONSE_CODES
API_TYPE_MAPPINGS = API.TYPE_MAPPINGS
