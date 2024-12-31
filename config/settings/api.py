"""API settings configuration."""

import os
from typing import Dict, List, Optional
from enum import Enum

from pydantic import Field, HttpUrl, SecretStr

from config.settings.base import Settings

class ApiVersion(str, Enum):
    """Valid API versions."""
    V1 = "v1"

class ApiSettings(Settings):
    """API configuration with validation."""
    
    # API versioning
    VERSION: ApiVersion = Field(
        default=ApiVersion.V1,
        description="Current API version"
    )
    SUPPORTED_VERSIONS: List[ApiVersion] = Field(
        default=[ApiVersion.V1],
        description="List of supported API versions"
    )
    
    # External API Keys
    ANTHROPIC_API_KEY: SecretStr = Field(
        default=None,
        description="Anthropic API key for Claude access"
    )
    
    # Endpoints
    BASE_URL: HttpUrl = Field(
        default="http://localhost:8000",
        description="Base URL for the API"
    )
    PREFIX: str = Field(
        default="/api",
        description="API endpoint prefix"
    )
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    RATE_LIMIT: str = Field(
        default="100/minute",
        description="Default rate limit (requests/timeunit)"
    )
    
    # Timeouts
    REQUEST_TIMEOUT: int = Field(
        default=30,
        description="Default request timeout in seconds"
    )
    LONG_POLLING_TIMEOUT: int = Field(
        default=300,
        description="Long polling timeout in seconds"
    )
    
    # Documentation
    DOCS_URL: str = Field(
        default="/docs",
        description="API documentation URL"
    )
    REDOC_URL: str = Field(
        default="/redoc",
        description="ReDoc documentation URL"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    CORS_METHODS: List[str] = Field(
        default=["*"],
        description="Allowed CORS methods"
    )
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "API_"
        case_sensitive = True
        env_file = ".env"

# Create settings instance
api_settings = ApiSettings()
