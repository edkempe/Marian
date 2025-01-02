"""Environment configuration module."""

import os
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr

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
        description="Environment-specific config files"
    )

    # API Keys
    ANTHROPIC_API_KEY: SecretStr = Field(
        default=SecretStr(""),
        description="Anthropic API key"
    )

    # Semantic Search Configuration
    ENABLE_SEMANTIC: bool = Field(
        default=True,
        description="Enable semantic search functionality"
    )
    MATCH_THRESHOLD: float = Field(
        default=0.85,
        description="Minimum score for a definite match"
    )
    POTENTIAL_MATCH_THRESHOLD: float = Field(
        default=0.70,
        description="Minimum score for a potential match"
    )
    TAG_MATCH_THRESHOLD: float = Field(
        default=0.80,
        description="Minimum score for tag matching"
    )
    RESULTS_PER_PAGE: int = Field(
        default=10,
        description="Number of results per page"
    )
    RELATIONSHIP_TYPES: list[str] = Field(
        default=["parent", "child", "related", "depends_on", "required_by"],
        description="Valid relationship types"
    )
    CATALOG_TABLES: Dict[str, str] = Field(
        default={
            "catalog": "catalog_items",
            "tags": "tags",
            "relationships": "relationships"
        },
        description="Catalog table names"
    )
    ERROR_MESSAGES: Dict[str, str] = Field(
        default={
            "no_matches": "No matches found for the given query.",
            "below_threshold": "The match score is below the required threshold.",
            "invalid_relationship": "Invalid relationship type specified.",
            "tag_not_found": "One or more specified tags were not found.",
            "duplicate_item": "An item with this identifier already exists."
        },
        description="Error message templates"
    )

    class Config:
        """Pydantic model configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        use_enum_values = True

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
