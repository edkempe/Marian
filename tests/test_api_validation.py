"""Tests to validate API documentation against actual usage."""

import os
import re
from typing import Dict, Set
import pytest
import markdown
from bs4 import BeautifulSoup
import ast

def parse_api_mappings(doc_path: str) -> Dict[str, Dict]:
    """Parse API mappings from documentation.
    
    Args:
        doc_path: Path to the API mappings markdown file
        
    Returns:
        Dictionary of API names to their endpoints and models
    """
    apis = {}
    current_api = None
    
    with open(doc_path, 'r') as f:
        for line in f:
            # Match API headers (## API Name)
            if line.startswith('## '):
                current_api = line.strip('# ').strip()
                apis[current_api] = {
                    'endpoints': set(),
                    'models': set()
                }
            
            # Match endpoint headers (### Name)
            elif current_api and line.startswith('### '):
                endpoint = line.strip('# ').strip()
                apis[current_api]['endpoints'].add(endpoint)
            
            # Match model mappings (table rows)
            elif current_api and '|' in line and not line.startswith('|--'):
                apis[current_api]['models'].add(line.strip())
    
    return apis

def find_api_imports(code_path: str) -> Set[str]:
    """Find API imports and usage in Python code.
    
    Args:
        code_path: Directory path to search for Python files
        
    Returns:
        Set of API names found in the code
    """
    api_patterns = {
        'Gmail API': r'(googleapiclient\.discovery|gmail_api|GmailAPI)',
        'Asset Catalog API': r'(asset_catalog|CatalogAPI)',
        'Anthropic API (Claude)': r'(anthropic\.Client|anthropic_client|APIClient)'
    }
    
    found_apis = set()
    
    for root, _, files in os.walk(code_path):
        for file in files:
            if not file.endswith('.py'):
                continue
            
            try:
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                
                for api_name, pattern in api_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        found_apis.add(api_name)
            except Exception as e:
                print(f"Error reading {file}: {e}")
    
    return found_apis

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
    # Get project root directory
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Parse API documentation
    doc_path = os.path.join(base_dir, 'docs', 'api_mappings.md')
    documented_apis = parse_api_mappings(doc_path)
    
    # Find APIs used in code
    used_apis = set()
    for code_path in [
        os.path.join(base_dir, 'models'),
        os.path.join(base_dir, 'shared_lib'),
        os.path.join(base_dir, 'src')
    ]:
        used_apis.update(find_api_imports(code_path))
    
    # Validate documentation coverage
    undocumented = used_apis - set(documented_apis.keys())
    assert not undocumented, f"Found APIs in code that are not documented: {undocumented}"
    
    # Validate API usage
    unused = set(documented_apis.keys()) - used_apis
    assert not unused, f"Found documented APIs that are not used in code: {unused}"

def test_model_field_documentation():
    """Test that all model fields are documented in API mappings."""
    # Get project root directory
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Parse API documentation
    doc_path = os.path.join(base_dir, 'docs', 'api_mappings.md')
    documented_apis = parse_api_mappings(doc_path)
    
    # Get actual model fields
    models_path = os.path.join(base_dir, 'models')
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
