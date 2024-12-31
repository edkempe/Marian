"""Environment configuration module."""

import os
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from pydantic_settings import BaseSettings
from pydantic import Field

class Environment(str, Enum):
    """Valid deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"

class Settings(BaseSettings):
    """Environment settings."""
    
    # Environment
    ENV: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Deployment environment"
    )
    DEBUG: bool = Field(
        default=False,
        description="Debug mode"
    )
    TESTING: bool = Field(
        default=False,
        description="Testing mode"
    )
    
    # Paths
    BASE_DIR: Path = Field(
        default=Path(__file__).parent.parent,
        description="Base directory of the project"
    )
    CONFIG_DIR: Path = Field(
        default=Path(__file__).parent,
        description="Configuration directory"
    )
    
    # Environment files
    ENV_FILE: str = Field(
        default=".env",
        description="Default environment file"
    )
    ENV_FILES: Dict[Environment, str] = Field(
        default={
            Environment.DEVELOPMENT: ".env.development",
            Environment.STAGING: ".env.staging",
            Environment.PRODUCTION: ".env.production",
            Environment.TEST: ".env.test"
        },
        description="Environment-specific .env files"
    )

def load_environment() -> Settings:
    """Load environment settings based on current environment.
    
    Returns:
        Settings: Validated environment settings
    """
    # Get environment
    env = os.getenv("ENV", Environment.DEVELOPMENT)
    
    # Create settings
    settings = Settings(ENV=env)
    
    # Load environment-specific .env file
    env_file = settings.ENV_FILES.get(env)
    if env_file and Path(env_file).exists():
        settings = Settings(ENV=env, _env_file=env_file)
    
    return settings

# Create environment settings instance
env_settings = load_environment()
