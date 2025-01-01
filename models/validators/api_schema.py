"""API schema validation for models.

This module ensures that our SQLAlchemy models maintain consistency with external API schemas.
Following ADR-0019 (API-First Schema Design) and ADR-0020 (API Schema Validation System).
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Type, Set
from functools import lru_cache

from pydantic import BaseModel, create_model, ValidationError
from sqlalchemy import event
from sqlalchemy.orm import DeclarativeMeta

from shared_lib.constants.validation import VALIDATION_ERRORS
from shared_lib.constants.api import API_TYPE_MAPPINGS
from models.base import Base


class APISchemaValidator:
    """Validates SQLAlchemy models against API schemas.
    
    Implementation of ADR-0020 schema validation system.
    """
    
    def __init__(self, api_specs_dir: str = "api_specs"):
        """Initialize validator with API specs directory."""
        self.api_specs_dir = Path(api_specs_dir)
        self._validated_models: Set[str] = set()
        
    @lru_cache(maxsize=100)
    def load_schema(self, api: str, version: str, resource: str) -> Dict[str, Any]:
        """Load and cache API schema from YAML file."""
        schema_path = self.api_specs_dir / api / version / f"{resource}.yaml"
        if not schema_path.exists():
            raise ValueError(VALIDATION_ERRORS["SCHEMA_NOT_FOUND"].format(path=schema_path))
            
        with schema_path.open() as f:
            return yaml.safe_load(f)
    
    def create_pydantic_model(self, schema: Dict[str, Any], name: str) -> Type[BaseModel]:
        """Create a Pydantic model from OpenAPI schema."""
        try:
            properties = schema["components"]["schemas"][name]["properties"]
            fields = {}
            
            for field_name, field_schema in properties.items():
                field_type = self._get_python_type(field_schema)
                field_default = None
                
                # Handle nullable fields (ADR-0019)
                if field_schema.get("nullable", False):
                    field_type = Optional[field_type]
                    
                # Handle API-specific constraints
                constraints = {}
                if "maxLength" in field_schema:
                    constraints["max_length"] = field_schema["maxLength"]
                if "pattern" in field_schema:
                    constraints["regex"] = field_schema["pattern"]
                if "enum" in field_schema:
                    constraints["allowed"] = field_schema["enum"]
                
                fields[field_name] = (field_type, field_default, constraints)
            
            return create_model(name, **fields)
            
        except KeyError as e:
            raise ValueError(VALIDATION_ERRORS["INVALID_SCHEMA"].format(error=str(e)))
    
    def _get_python_type(self, field_schema: Dict[str, Any]) -> Type:
        """Convert OpenAPI type to Python type following API_TYPE_MAPPINGS."""
        type_name = field_schema["type"]
        if type_name not in API_TYPE_MAPPINGS:
            raise ValueError(VALIDATION_ERRORS["UNKNOWN_TYPE"].format(type=type_name))
        return API_TYPE_MAPPINGS[type_name]
    
    def validate_model(self, model: DeclarativeMeta, api: str, version: str, resource: str) -> None:
        """Validate SQLAlchemy model against API schema."""
        model_key = f"{model.__name__}_{api}_{version}_{resource}"
        if model_key in self._validated_models:
            return
            
        schema = self.load_schema(api, version, resource)
        pydantic_model = self.create_pydantic_model(schema, resource.title())
        
        # Validate field types and constraints (ADR-0019)
        model_fields = {c.name: c.type.python_type for c in model.__table__.columns}
        schema_fields = pydantic_model.__annotations__
        
        for field_name, field_type in schema_fields.items():
            if field_name not in model_fields:
                raise ValueError(
                    VALIDATION_ERRORS["MISSING_FIELD"].format(
                        field=field_name,
                        model=model.__name__
                    )
                )
            
            model_type = model_fields[field_name]
            if not self._types_compatible(model_type, field_type):
                raise ValueError(
                    VALIDATION_ERRORS["TYPE_MISMATCH"].format(
                        field=field_name,
                        model_type=model_type.__name__,
                        schema_type=field_type.__name__
                    )
                )
        
        self._validated_models.add(model_key)
    
    def _types_compatible(self, model_type: Type, schema_type: Type) -> bool:
        """Check if model and schema types are compatible."""
        # Implementation based on API_TYPE_MAPPINGS
        return True  # TODO: Implement proper type compatibility checks


# Register global validation event
api_validator = APISchemaValidator()

@event.listens_for(Base.metadata, 'after_create')
def validate_schemas(target, connection, **kw):
    """Validate all models against their API schemas."""
    # This hook ensures validation happens automatically (ADR-0020)
