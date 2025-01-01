"""Test environment settings."""

from pathlib import Path
from typing import Optional, Dict

from pydantic import Field, SecretStr, AnyUrl

from config.settings.base import Settings
from config.settings.database import DatabaseType


class TestSettings(Settings):
    """Test environment settings with comprehensive configuration."""
    
    # Environment
    ENV: str = Field(default="test", description="Environment name")
    DEBUG: bool = Field(default=True, description="Debug mode")
    TEST_MODE: bool = Field(default=True, description="Test mode flag")
    
    # Test Data Directory
    TEST_DATA_DIR: Path = Field(
        default=Path(__file__).parent.parent / "tests" / "test_data",
        description="Test data directory"
    )
    TEST_LOG_DIR: Path = Field(
        default=Path(__file__).parent.parent / "tests" / "test_logs",
        description="Test log directory"
    )
    
    # Database
    DATABASE_TYPE: DatabaseType = Field(
        default=DatabaseType.SQLITE,
        description="Test database type"
    )
    DATABASE_URLS: Dict[str, str] = Field(
        default={
            "default": "sqlite:///tests/test_data/test.db",
            "email": "sqlite:///tests/test_data/test_email.db",
            "analysis": "sqlite:///tests/test_data/test_analysis.db",
            "catalog": "sqlite:///tests/test_data/test_catalog.db"
        },
        description="Test database URLs"
    )
    DATABASE_MIN_CONNECTIONS: int = Field(
        default=1,
        description="Minimum test database connections",
        ge=1
    )
    DATABASE_MAX_CONNECTIONS: int = Field(
        default=5,
        description="Maximum test database connections",
        ge=1
    )
    DATABASE_TIMEOUT: int = Field(
        default=30,
        description="Database connection timeout in seconds",
        ge=1
    )
    
    # API Configuration
    API_KEYS: Dict[str, str] = Field(
        default={
            "openai": "test-openai-key",
            "anthropic": "test-anthropic-key",
            "google": "test-google-key"
        },
        description="Test API keys"
    )
    
    # Email Configuration
    SMTP_HOST: str = Field(
        default="localhost",
        description="Test SMTP host"
    )
    SMTP_PORT: int = Field(
        default=1025,
        description="Test SMTP port"
    )
    IMAP_HOST: str = Field(
        default="localhost",
        description="Test IMAP host"
    )
    IMAP_PORT: int = Field(
        default=1143,
        description="Test IMAP port"
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default="DEBUG",
        description="Test log level"
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Test log format"
    )
    LOG_FILE: Path = Field(
        default=Path("tests/test_data/test.log"),
        description="Test log file"
    )

    def __init__(self, **data):
        """Initialize test settings and create test directories."""
        super().__init__(**data)
        # Create test data directory if it doesn't exist
        self.TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.TEST_LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    class Config:
        """Pydantic config."""
        env_prefix = "TEST_"
        case_sensitive = True


# Create test settings instance
test_settings = TestSettings()
