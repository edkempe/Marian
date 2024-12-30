"""Test schema configuration loading and validation."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from shared_lib.config_loader import (
    ColumnConfig,
    SchemaConfig,
    TableConfig,
    get_schema_config,
    load_schema_config,
)


def test_column_config_validation():
    """Test column configuration validation."""
    # Valid configuration
    valid_config = {
        "size": 100,
        "type": "string",
        "description": "Test column"
    }
    column = ColumnConfig(**valid_config)
    assert column.size == 100
    assert column.type == "string"
    
    # Invalid size
    with pytest.raises(ValidationError):
        ColumnConfig(size=-1, type="string", description="Invalid size")
    
    # Missing required field
    with pytest.raises(ValidationError):
        ColumnConfig(size=100, description="Missing type")


def test_table_config_validation():
    """Test table configuration validation."""
    valid_config = {
        "columns": {
            "test_column": {
                "size": 100,
                "type": "string",
                "description": "Test column"
            }
        }
    }
    table = TableConfig(**valid_config)
    assert table.columns["test_column"].size == 100
    
    # Test defaults
    assert table.defaults.subject == ""
    assert not table.defaults.has_attachments
    
    # Test validation rules
    assert "neutral" in table.validation.valid_sentiments
    assert len(table.validation.valid_priorities) == 3


def test_schema_config_loading():
    """Test schema configuration loading from file."""
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as temp_config:
        config_data = {
            "email": {
                "columns": {
                    "subject": {
                        "size": 500,
                        "type": "string",
                        "description": "Email subject"
                    }
                }
            },
            "analysis": {
                "columns": {
                    "sentiment": {
                        "size": 50,
                        "type": "string",
                        "description": "Sentiment analysis"
                    }
                }
            },
            "label": {
                "columns": {
                    "name": {
                        "size": 200,
                        "type": "string",
                        "description": "Label name"
                    }
                }
            }
        }
        yaml.dump(config_data, temp_config)
        temp_config.flush()
        
        # Set environment variable to use our temp config
        os.environ["SCHEMA_CONFIG_PATH"] = temp_config.name
        
        # Load configuration
        config = load_schema_config()
        
        # Verify configuration
        assert isinstance(config, SchemaConfig)
        assert config.email.columns["subject"].size == 500
        assert config.analysis.columns["sentiment"].size == 50
        assert config.label.columns["name"].size == 200


def test_get_schema_config_caching():
    """Test that get_schema_config caches the configuration."""
    config1 = get_schema_config()
    config2 = get_schema_config()
    
    # Should return the same object
    assert config1 is config2


def test_environment_specific_config():
    """Test loading environment-specific configuration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config directory
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir()
        
        # Create default config
        default_config = {
            "email": {
                "columns": {
                    "subject": {
                        "size": 500,
                        "type": "string",
                        "description": "Default config"
                    }
                }
            },
            "analysis": {"columns": {}},
            "label": {"columns": {}}
        }
        
        # Create test config
        test_config = {
            "email": {
                "columns": {
                    "subject": {
                        "size": 200,
                        "type": "string",
                        "description": "Test config"
                    }
                }
            },
            "analysis": {"columns": {}},
            "label": {"columns": {}}
        }
        
        # Write configs
        with open(config_dir / "schema.yaml", 'w') as f:
            yaml.dump(default_config, f)
        
        with open(config_dir / "schema.test.yaml", 'w') as f:
            yaml.dump(test_config, f)
        
        # Test default config
        os.environ["ENV"] = "development"
        os.environ["SCHEMA_CONFIG_PATH"] = str(config_dir / "schema.yaml")
        config = load_schema_config()
        assert config.email.columns["subject"].size == 500
        
        # Test environment-specific config
        os.environ["ENV"] = "test"
        os.environ["SCHEMA_CONFIG_PATH"] = str(config_dir / "schema.test.yaml")
        config = load_schema_config()
        assert config.email.columns["subject"].size == 200
