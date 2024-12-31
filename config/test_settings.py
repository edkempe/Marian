"""Test environment settings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class TestSettings(BaseSettings):
    """Test environment settings with minimal configuration."""
    
    ENV: str = Field(default="test")
    DEBUG: bool = Field(default=True)
    DATABASE_URL: str = Field(default="sqlite:///:memory:")
    API_KEY: str = Field(default="test_key_123")
    TEST_MODE: bool = Field(default=True)
    
    class Config:
        env_file = ".env.test"
        env_file_encoding = "utf-8"
        case_sensitive = True

test_settings = TestSettings()
