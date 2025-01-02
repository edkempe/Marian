"""API validation mixin for SQLAlchemy models."""

from typing import Dict, Any, Type, Optional
import yaml
from pathlib import Path
from datamodel_code_generator import generate
from pydantic import BaseModel


class APIValidationMixin:
    """Mixin to add API validation to SQLAlchemy models."""
    
    _pydantic_models: Dict[str, Type[BaseModel]] = {}
    
    @classmethod
    def _get_pydantic_model(cls, api: str, version: str, resource: str) -> Type[BaseModel]:
        """Get or generate Pydantic model from API spec."""
        cache_key = f"{api}/{version}/{resource}"
        if cache_key not in cls._pydantic_models:
            # Load API spec
            spec_path = Path("api_specs") / api / version / f"{resource}.yaml"
            if not spec_path.exists():
                raise ValueError(f"API spec not found: {spec_path}")
            
            with spec_path.open() as f:
                spec = yaml.safe_load(f)
            
            # Generate Pydantic model
            model_code = generate(
                yaml.dump(spec),
                input_file_type="openapi",
                target_python_version="3.8"
            )
            
            # Create module with generated code
            module_name = f"{api}_{version}_{resource}"
            exec(model_code, globals(), locals())
            
            # Get main model class (assumes resource name matches class name)
            model_class = locals()[resource.title()]
            cls._pydantic_models[cache_key] = model_class
        
        return cls._pydantic_models[cache_key]
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any], api: str, version: str, resource: str) -> "APIValidationMixin":
        """Create model instance from validated API response."""
        # Get Pydantic model
        pydantic_model = cls._get_pydantic_model(api, version, resource)
        
        # Validate response data
        validated_data = pydantic_model(**response).dict()
        
        # Create SQLAlchemy model instance
        return cls(**validated_data)
    
    def to_api_response(self, api: str, version: str, resource: str) -> Dict[str, Any]:
        """Convert model instance to validated API response."""
        # Get Pydantic model
        pydantic_model = self._get_pydantic_model(api, version, resource)
        
        # Convert SQLAlchemy model to dict
        data = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
        
        # Validate and return response data
        return pydantic_model(**data).dict()
