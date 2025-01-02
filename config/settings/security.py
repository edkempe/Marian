"""Security settings configuration."""

import os
from typing import Dict, List, Optional
from enum import Enum

from pydantic import Field, SecretStr

from config.settings.base import Settings

class AuthType(str, Enum):
    """Supported authentication types."""
    JWT = "jwt"
    SESSION = "session"
    API_KEY = "api_key"

class SecuritySettings(Settings):
    """Security configuration with validation."""
    
    # Authentication
    AUTH_TYPE: AuthType = Field(
        default=AuthType.JWT,
        description="Authentication type"
    )
    SECRET_KEY: SecretStr = Field(
        default="your-secret-key-for-testing-only",
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
    PASSWORD_SALT_ROUNDS: int = Field(
        default=12,
        description="Number of salt rounds for password hashing",
        ge=10
    )
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        description="Maximum requests per window",
        ge=1
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=3600,  # 1 hour
        description="Rate limit window in seconds",
        ge=60
    )
    
    # Session settings
    SESSION_TIMEOUT: int = Field(
        default=1800,  # 30 minutes
        description="Session timeout in seconds",
        ge=300
    )
    SESSION_COOKIE_NAME: str = Field(
        default="session",
        description="Session cookie name"
    )
    SESSION_COOKIE_SECURE: bool = Field(
        default=True,
        description="Require HTTPS for session cookie"
    )
    
    # CORS settings
    CORS_ENABLED: bool = Field(
        default=True,
        description="Enable CORS"
    )
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "SECURITY_"
        case_sensitive = True
        env_file = ".env"

# Create settings instance
security_settings = SecuritySettings()
