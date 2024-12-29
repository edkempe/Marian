"""Test suite for API documentation and standards.

This module ensures that our API documentation and implementation
maintain high quality standards across the project.
"""

import os
import yaml
import pytest
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class APIEndpoint:
    """Represents an API endpoint definition."""
    path: str
    method: str
    description: Optional[str]
    parameters: List[Dict]
    responses: Dict[str, Dict]
    examples: List[Dict]

def get_openapi_spec() -> Dict:
    """Load OpenAPI specification."""
    project_root = Path(__file__).parent.parent
    api_spec_path = project_root / 'api' / 'openapi.yaml'
    
    if not api_spec_path.exists():
        return {}
    
    with open(api_spec_path) as f:
        return yaml.safe_load(f)

def get_implemented_endpoints() -> List[APIEndpoint]:
    """Extract implemented API endpoints from code."""
    project_root = Path(__file__).parent.parent
    endpoints = []
    
    # Search through route definitions
    for py_file in project_root.rglob('*.py'):
        if py_file.name.startswith('_'):
            continue
            
        try:
            with open(py_file) as f:
                content = f.read()
                
            # Look for route decorators
            for line in content.split('\n'):
                if '@app.route' in line or '@blueprint.route' in line:
                    endpoint = APIEndpoint(
                        path=line.split('"')[1],
                        method='GET',  # Default method
                        description=None,
                        parameters=[],
                        responses={},
                        examples=[]
                    )
                    endpoints.append(endpoint)
                    
        except Exception:
            continue
            
    return endpoints

def test_api_documentation():
    """Verify API documentation completeness and accuracy."""
    spec = get_openapi_spec()
    implemented = get_implemented_endpoints()
    
    # All implemented endpoints should be documented
    implemented_paths = {e.path for e in implemented}
    documented_paths = set(spec.get('paths', {}).keys())
    
    undocumented = implemented_paths - documented_paths
    assert not undocumented, f"Found undocumented endpoints: {undocumented}"
    
    # All documented endpoints should have:
    # 1. Description
    # 2. Parameters (if any)
    # 3. Response schemas
    # 4. Examples
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            assert details.get('description'), f"Missing description for {method} {path}"
            
            if details.get('parameters'):
                for param in details['parameters']:
                    assert param.get('description'), f"Missing parameter description in {method} {path}"
                    
            assert details.get('responses'), f"Missing response schemas for {method} {path}"
            
            # At least one example per 2XX response
            success_responses = {k: v for k, v in details.get('responses', {}).items() 
                              if k.startswith('2')}
            for status, response in success_responses.items():
                assert response.get('examples') or response.get('example'), \
                    f"Missing examples for {status} response in {method} {path}"
