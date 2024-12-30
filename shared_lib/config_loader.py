"""Configuration loader for database schema and other settings.

This module provides utilities to load and validate configuration from YAML files.
It supports environment-specific configurations and schema validation.
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel, Field


class ColumnConfig(BaseModel):
    """Configuration for a database column."""
    size: int = Field(gt=0, description="Column size must be positive")
    type: str = Field(pattern="^(string|text|integer|float|boolean|datetime)$")
    description: str = Field(min_length=1)


class TableDefaults(BaseModel):
    """Default values for table columns."""
    # Email defaults
    subject: str = ""
    has_attachments: bool = False
    is_read: bool = False
    is_important: bool = False
    api_response: str = "{}"
    
    # Analysis defaults
    sentiment: str = "neutral"
    category: str = "uncategorized"
    
    # Label defaults
    type: str = "user"
    is_system: bool = False


class ValidationConfig(BaseModel):
    """Validation rules for table data."""
    # Analysis validation
    valid_sentiments: list[str] = ["positive", "negative", "neutral", "mixed"]
    valid_priorities: list[str] = ["high", "medium", "low"]
    max_summary_length: int = Field(gt=0, default=1000)
    
    # Email validation
    max_subject_length: int = Field(gt=0, default=500)
    max_snippet_length: int = Field(gt=0, default=500)
    
    # Label validation
    valid_types: list[str] = ["system", "user"]
    max_name_length: int = Field(gt=0, default=100)


class TableConfig(BaseModel):
    """Configuration for a database table."""
    columns: Dict[str, ColumnConfig]
    defaults: TableDefaults = Field(default_factory=TableDefaults)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)


class SchemaConfig(BaseModel):
    """Complete database schema configuration."""
    email: TableConfig
    analysis: TableConfig
    label: TableConfig


def load_schema_config() -> SchemaConfig:
    """Load schema configuration from YAML file.
    
    The configuration file is looked up in the following order:
    1. Path specified in SCHEMA_CONFIG_PATH environment variable
    2. config/schema.yaml in the project root
    3. config/schema.{environment}.yaml where environment is from ENV variable
    
    Returns:
        SchemaConfig: Validated schema configuration
        
    Raises:
        FileNotFoundError: If no configuration file is found
        ValidationError: If configuration is invalid
    """
    # Determine config file location
    config_path = os.getenv("SCHEMA_CONFIG_PATH")
    if not config_path:
        project_root = Path(__file__).parent.parent
        env = os.getenv("ENV", "development")
        
        # Try environment-specific config first
        config_path = project_root / "config" / f"schema.{env}.yaml"
        if not config_path.exists():
            config_path = project_root / "config" / "schema.yaml"
    
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Schema configuration not found at {config_path}")
    
    # Load and validate configuration
    with open(config_path) as f:
        config_dict = yaml.safe_load(f)
    
    return SchemaConfig(**config_dict)


# Global schema configuration instance
_schema_config: SchemaConfig | None = None


def get_schema_config() -> SchemaConfig:
    """Get the schema configuration, loading it if necessary.
    
    Returns:
        SchemaConfig: Validated schema configuration
    """
    global _schema_config
    if _schema_config is None:
        _schema_config = load_schema_config()
    return _schema_config
