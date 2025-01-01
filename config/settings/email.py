"""Email settings configuration."""

import os
from typing import Dict, Optional

from pydantic import Field, EmailStr

from config.settings.base import Settings

class EmailSettings(Settings):
    """Email configuration with validation."""
    
    # SMTP settings
    SMTP_HOST: str = Field(
        default="smtp.gmail.com",
        description="SMTP server hostname"
    )
    SMTP_PORT: int = Field(
        default=587,
        description="SMTP server port"
    )
    SMTP_USERNAME: str = Field(
        default="",
        description="SMTP username"
    )
    SMTP_PASSWORD: str = Field(
        default="",
        description="SMTP password"
    )
    USE_TLS: bool = Field(
        default=True,
        description="Use TLS for SMTP connection"
    )
    
    # Email defaults
    DEFAULT_FROM_EMAIL: EmailStr = Field(
        default="noreply@example.com",
        description="Default from email address"
    )
    DEFAULT_FROM_NAME: str = Field(
        default="Jexi",
        description="Default from name"
    )
    
    # Processing settings
    BATCH_SIZE: int = Field(
        default=100,
        description="Email batch processing size",
        ge=1
    )
    MAX_RETRIES: int = Field(
        default=3,
        description="Maximum retry attempts",
        ge=1
    )
    RETRY_DELAY: int = Field(
        default=5,
        description="Delay between retries in seconds",
        ge=1
    )
    
    # Logging
    LOG_EMAILS: bool = Field(
        default=True,
        description="Log email operations"
    )
    
    # Rate limiting
    RATE_LIMIT: int = Field(
        default=100,
        description="Maximum emails per hour",
        ge=1
    )
    
    # Attachments
    MAX_ATTACHMENT_SIZE: int = Field(
        default=10_485_760,  # 10MB
        description="Maximum attachment size in bytes",
        ge=1
    )
    ALLOWED_ATTACHMENT_TYPES: list[str] = Field(
        default=["pdf", "doc", "docx", "txt", "png", "jpg", "jpeg"],
        description="Allowed attachment file types"
    )
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "EMAIL_"
        case_sensitive = True
        env_file = ".env"

# Create settings instance
email_settings = EmailSettings()
