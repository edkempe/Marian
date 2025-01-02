"""Base settings configuration."""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Base settings class with common configuration."""
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from env file
