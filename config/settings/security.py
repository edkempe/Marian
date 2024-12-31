"""Security settings configuration."""

import os
from typing import Dict, List, Optional
from enum import Enum

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

class AuthType(str, Enum):
    """Supported authentication types."""
    JWT = "jwt"
    SESSION = "session"
    API_KEY = "api_key"

class SecuritySettings(BaseSettings):
    """Security configuration with validation."""
    
    # Authentication
    AUTH_TYPE: AuthType = Field(
        default=AuthType.JWT,
        description="Authentication type"
    )
    SECRET_KEY: SecretStr = Field(
        ...,  # Required
        description="Secret key for token signing"
    )
    
    # JWT settings
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    JWT_EXPIRATION: int = Field(
        default=3600,  # 1 hour
        description="JWT expiration time in seconds",
        ge=60
    )
    JWT_REFRESH_EXPIRATION: int = Field(
        default=86400,  # 24 hours
        description="JWT refresh token expiration in seconds",
        ge=300
    )
    
    # Password settings
    MIN_PASSWORD_LENGTH: int = Field(
        default=12,
        description="Minimum password length",
        ge=8
    )
    PASSWORD_HASH_ALGORITHM: str = Field(
        default="bcrypt",
        description="Password hashing algorithm"
    )
    PASSWORD_RESET_TIMEOUT: int = Field(
        default=3600,  # 1 hour
        description="Password reset token timeout in seconds",
        ge=300
    )
    
    # Session settings
    SESSION_COOKIE_NAME: str = Field(
        default="session",
        description="Session cookie name"
    )
    SESSION_TIMEOUT: int = Field(
        default=3600,  # 1 hour
        description="Session timeout in seconds",
        ge=60
    )
    SESSION_SECURE: bool = Field(
        default=True,
        description="Require HTTPS for session cookie"
    )
    
    # Rate limiting
    LOGIN_RATE_LIMIT: str = Field(
        default="5/minute",
        description="Login attempt rate limit"
    )
    PASSWORD_RESET_RATE_LIMIT: str = Field(
        default="3/hour",
        description="Password reset rate limit"
    )
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    CORS_METHODS: List[str] = Field(
        default=["*"],
        description="Allowed CORS methods"
    )
    
    # Security headers
    SECURITY_HEADERS: Dict[str, str] = Field(
        default={
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        },
        description="Security headers to include in responses"
    )
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "SECURITY_"
        case_sensitive = True
        env_file = ".env"

# Create settings instance
security_settings = SecuritySettings()
