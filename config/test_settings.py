"""Test environment settings."""

from pathlib import Path
from typing import Optional, Dict, Union
from datetime import timedelta

from pydantic import Field, SecretStr, AnyUrl, validator, model_validator
from pydantic.types import PositiveInt, constr

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
    DATABASE_MIN_CONNECTIONS: PositiveInt = Field(
        default=1,
        description="Minimum test database connections"
    )
    DATABASE_MAX_CONNECTIONS: PositiveInt = Field(
        default=5,
        description="Maximum test database connections"
    )
    DATABASE_TIMEOUT: PositiveInt = Field(
        default=30,
        description="Database connection timeout in seconds"
    )
    DATABASE_POOL_RECYCLE: PositiveInt = Field(
        default=3600,
        description="Database connection pool recycle time in seconds"
    )
    
    # API Configuration
    API_KEYS: Dict[str, SecretStr] = Field(
        default={
            "openai": SecretStr("test-openai-key"),
            "anthropic": SecretStr("test-anthropic-key"),
            "google": SecretStr("test-google-key")
        },
        description="Test API keys"
    )
    API_TIMEOUT: PositiveInt = Field(
        default=30,
        description="API request timeout in seconds"
    )
    API_RETRY_COUNT: PositiveInt = Field(
        default=3,
        description="Number of API request retries"
    )
    API_RETRY_DELAY: PositiveInt = Field(
        default=1,
        description="Delay between API retries in seconds"
    )
    
    # Email Configuration
    SMTP_HOST: str = Field(
        default="localhost",
        description="Test SMTP host"
    )
    SMTP_PORT: PositiveInt = Field(
        default=1025,
        description="Test SMTP port"
    )
    IMAP_HOST: str = Field(
        default="localhost",
        description="Test IMAP host"
    )
    IMAP_PORT: PositiveInt = Field(
        default=1143,
        description="Test IMAP port"
    )
    EMAIL_TIMEOUT: PositiveInt = Field(
        default=30,
        description="Email operation timeout in seconds"
    )
    
    # Logging
    LOG_LEVEL: constr(pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$") = Field(
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
    LOG_MAX_SIZE: PositiveInt = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum log file size in bytes"
    )
    LOG_BACKUP_COUNT: PositiveInt = Field(
        default=5,
        description="Number of log file backups to keep"
    )
    
    # Test Timeouts
    TEST_TIMEOUT: PositiveInt = Field(
        default=60,
        description="Default test timeout in seconds"
    )
    TEST_CLEANUP_TIMEOUT: PositiveInt = Field(
        default=30,
        description="Test cleanup timeout in seconds"
    )
    
    @validator("DATABASE_MAX_CONNECTIONS")
    def validate_max_connections(cls, v: int, values: Dict) -> int:
        """Validate max connections is greater than min connections."""
        min_conn = values.get("DATABASE_MIN_CONNECTIONS")
        if min_conn and v <= min_conn:
            raise ValueError("Max connections must be greater than min connections")
        return v

    @validator("DATABASE_URLS")
    def validate_database_urls(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate database URLs."""
        required_dbs = {"default", "email", "analysis", "catalog"}
        if not all(db in v for db in required_dbs):
            raise ValueError(f"Missing required database URLs: {required_dbs - v.keys()}")
        return v

    @model_validator(mode='after')
    def validate_directories(cls, model):
        """Validate and create required directories."""
        # Access attributes directly from model
        test_data_dir = model.TEST_DATA_DIR
        test_log_dir = model.TEST_LOG_DIR
        log_file = model.LOG_FILE
        
        if test_data_dir:
            test_data_dir.mkdir(parents=True, exist_ok=True)
        if test_log_dir:
            test_log_dir.mkdir(parents=True, exist_ok=True)
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
        return model
    
    def __init__(self, **data):
        """Initialize test settings and create test directories."""
        super().__init__(**data)
        self.validate_directories(self)
    
    class Config:
        """Pydantic config."""
        env_prefix = "TEST_"
        case_sensitive = True
        validate_assignment = True
        arbitrary_types_allowed = True


# Create test settings instance
test_settings = TestSettings()
