"""Tests to validate API documentation against actual usage."""

import os
import re
import ast
from typing import Dict, List, Set
import pytest
import markdown
from bs4 import BeautifulSoup

def parse_api_mappings(doc_path: str) -> Dict[str, Dict]:
    """Parse the API mappings markdown file.
    
    Returns:
        Dict mapping API names to their details including:
        - version: API version
        - documentation: Documentation URL
        - models: List of models using this API
        - endpoints: Set of documented endpoints
    """
    with open(doc_path, 'r') as f:
        content = f.read()
    
    # Convert markdown to HTML for easier parsing
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, 'html.parser')
    
    apis = {}
    current_api = None
    
    for elem in soup.find_all(['h2', 'p', 'table']):
        if elem.name == 'h2':
            # New API section
            current_api = elem.text.strip()
            apis[current_api] = {
                'version': None,
                'documentation': None,
                'models': [],
                'endpoints': set()
            }
        elif elem.name == 'p' and current_api:
            # Look for version and documentation
            text = elem.text.strip()
            if 'API Version:' in text:
                apis[current_api]['version'] = text.split('API Version:')[1].strip()
            elif 'Documentation:' in text:
                apis[current_api]['documentation'] = text.split('Documentation:')[1].strip()
        elif elem.name == 'table' and current_api:
            # Add model name from preceding h3
            model_header = elem.find_previous('h3')
            if model_header:
                model_name = model_header.text.strip().split(' Model')[0]
                apis[current_api]['models'].append(model_name)
            
            # Extract endpoints from table
            for row in elem.find_all('tr'):
                cells = row.find_all('td')
                if cells and 'Source:' in cells[0].text:
                    endpoint = cells[0].text.split('Source:')[1].strip()
                    apis[current_api]['endpoints'].add(endpoint)
    
    return apis

def find_api_imports(code_path: str) -> Set[str]:
    """Find all API imports and usages in Python code.
    
    Returns:
        Set of API names found in imports
    """
    api_patterns = {
        'Gmail API': r'googleapiclient.*gmail',
        'Asset Catalog API': r'asset_catalog_api'  # Add actual import pattern
    }
    
    apis_found = set()
    
    for root, _, files in os.walk(code_path):
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check each API's import pattern
            for api_name, pattern in api_patterns.items():
                if re.search(pattern, content):
                    apis_found.add(api_name)
    
    return apis_found

def find_model_fields(models_path: str) -> Dict[str, Set[str]]:
    """Extract field names from SQLAlchemy models.
    
    Returns:
        Dict mapping model names to sets of field names
    """
    model_fields = {}
    
    for root, _, files in os.walk(models_path):
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a SQLAlchemy model
                    if any(base.id == 'Base' for base in node.bases 
                          if isinstance(base, ast.Name)):
                        fields = set()
                        for child in node.body:
                            if isinstance(child, ast.AnnAssign):
                                # Get field name from type annotation
                                if isinstance(child.target, ast.Name):
                                    fields.add(child.target.id)
                        if fields:
                            model_fields[node.name] = fields
    
    return model_fields

def test_api_documentation_completeness():
    """Test that all APIs are properly documented and used."""
    # Paths
    base_dir = os.path.dirname(os.path.dirname(__file__))
    doc_path = os.path.join(base_dir, 'docs', 'api_mappings.md')
    code_path = os.path.join(base_dir, 'models')
    
    # Get documented APIs
    documented_apis = parse_api_mappings(doc_path)
    
    # Get APIs actually used in code
    used_apis = find_api_imports(code_path)
    
    # Check for undocumented APIs
    undocumented = used_apis - set(documented_apis.keys())
    assert not undocumented, f"Found APIs in code that are not documented: {undocumented}"
    
    # Check for unused APIs
    unused = set(documented_apis.keys()) - used_apis
    assert not unused, f"Found documented APIs that are not used in code: {unused}"

def test_model_field_documentation():
    """Test that all model fields are documented in API mappings."""
    # Paths
    base_dir = os.path.dirname(os.path.dirname(__file__))
    doc_path = os.path.join(base_dir, 'docs', 'api_mappings.md')
    models_path = os.path.join(base_dir, 'models')
    
    # Get documented APIs and their models
    documented_apis = parse_api_mappings(doc_path)
    
    # Get actual model fields
    model_fields = find_model_fields(models_path)
    
    # Check each documented API's models
    for api_name, api_info in documented_apis.items():
        for model_name in api_info['models']:
            # Skip if model doesn't exist
            if model_name not in model_fields:
                pytest.fail(f"Documented model {model_name} not found in code")
                continue
            
            actual_fields = model_fields[model_name]
            documented_fields = set()  # TODO: Extract fields from markdown tables
            
            # Check for undocumented fields
            undocumented = actual_fields - documented_fields
            assert not undocumented, \
                f"Model {model_name} has fields that are not documented: {undocumented}"
            
            # Check for documented fields that don't exist
            nonexistent = documented_fields - actual_fields
            assert not nonexistent, \
                f"API documentation mentions non-existent fields for {model_name}: {nonexistent}"

if __name__ == '__main__':
    pytest.main([__file__])
