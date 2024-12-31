"""Email settings configuration."""

import os
from typing import Dict, Optional

from pydantic import Field, EmailStr
from pydantic_settings import BaseSettings

class EmailSettings(BaseSettings):
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
        ge=0
    )
    RETRY_DELAY: int = Field(
        default=5,
        description="Delay between retries in seconds",
        ge=1
    )
    
    # Template settings
    TEMPLATE_DIR: str = Field(
        default="templates/email",
        description="Email template directory"
    )
    DEFAULT_TEMPLATE: str = Field(
        default="base.html",
        description="Default email template"
    )
    
    # Size limits
    MAX_RECIPIENTS: int = Field(
        default=100,
        description="Maximum recipients per email",
        ge=1
    )
    MAX_ATTACHMENT_SIZE: int = Field(
        default=25 * 1024 * 1024,  # 25MB
        description="Maximum attachment size in bytes",
        ge=1
    )
    MAX_EMAIL_SIZE: int = Field(
        default=50 * 1024 * 1024,  # 50MB
        description="Maximum total email size in bytes",
        ge=1
    )
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "EMAIL_"
        case_sensitive = True
        env_file = ".env"

# Create settings instance
email_settings = EmailSettings()
