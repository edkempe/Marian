"""Test that requirements.txt is both necessary and sufficient."""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Union

import pkg_resources
import pytest

def get_installed_packages() -> Dict[str, str]:
    """Get dictionary of installed packages and their versions."""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def get_requirements() -> Dict[str, str]:
    """Get dictionary of required packages and their versions from requirements.txt."""
    requirements = {}
    with open('requirements.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '>=' in line:
                    pkg, version = line.split('>=')
                elif '==' in line:
                    pkg, version = line.split('==')
                else:
                    continue
                requirements[pkg.strip()] = version.strip()
    return requirements

def get_imports_from_file(file_path: str) -> Set[str]:
    """Extract import statements from a Python file."""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract imports
        import_patterns = [
            r'^import\s+(\w+)',  # import foo
            r'^from\s+(\w+)\s+import',  # from foo import ...
            r'^import\s+(\w+)\s+as',  # import foo as ...
            r'^from\s+(\w+)\.',  # from foo.bar import ...
            r'^from\s+google\.oauth2',  # Special case for google-api-python-client
            r'^from\s+google_auth_oauthlib',  # Special case for google-auth-oauthlib
            r'^from\s+googleapiclient',  # Special case for google-api-python-client
        ]
        
        package_aliases = {
            'google': 'google-api-python-client',
            'google_auth_oauthlib': 'google-auth-oauthlib',
            'googleapiclient': 'google-api-python-client',
            'dateutil': 'python-dateutil',
            'dotenv': 'python-dotenv',
            'jose': 'python-jose',
            'prometheus_client': 'prometheus-client',
            'sqlalchemy_utils': 'sqlalchemy-utils',
        }
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                pkg = match.group(1) if len(match.groups()) > 0 else match.group(0).split()[1]
                if pkg in package_aliases:
                    pkg = package_aliases[pkg]
                if not is_local_import(pkg):
                    imports.add(pkg.lower())
                    
    except Exception as e:
        print(f"Warning: Error processing {os.path.basename(file_path)}: {str(e)}")
        
    return imports

def is_local_import(pkg: str) -> bool:
    """Check if an import is local to the project."""
    local_modules = {
        'app_api_client', 'app_catalog', 'app_email_analyzer',
        'app_email_reports', 'app_email_self_log', 'app_get_mail',
        'config', 'constants', 'database', 'database_session_util',
        'gmail_label_id', 'gmail_lib', 'logging_config', 'logging_util',
        'models', 'reporting', 'services', 'shared_lib', 'src', 'tests',
        'utils', 'test_config', 'test_doc_quality', 'test_doc_format',
        'test_doc_hierarchy', 'test_dependencies', 'test_api_validation',
        'test_catalog', 'test_email_analysis', 'test_email_analyzer',
        'test_email_reports', 'test_get_mail', 'test_integration',
        'test_semantic_search', 'test_semantic_search_integration',
        'test_semantic_search_pure', 'test_hardcoded_values',
        'test_requirements', 'test_minimal', 'test_imports',
        'test_config', 'test_doc_quality'
    }
    return pkg.lower() in local_modules

def get_all_imports() -> Set[str]:
    """Get all imports from Python files in the project."""
    imports = set()
    for root, _, files in os.walk('.'):
        if 'venv' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                imports.update(get_imports_from_file(path))
    return imports

def analyze_requirements() -> Dict[str, Set[str]]:
    """Analyze requirements for issues."""
    issues = {}
    
    # Get data
    requirements = get_requirements()
    installed = get_installed_packages()
    imports = get_all_imports()
    
    # Check for unused requirements
    unused = set(requirements) - imports
    if unused:
        issues['unused_requirements'] = unused
        
    # Check for missing requirements
    required = set(requirements)
    missing = {imp for imp in imports 
              if imp not in required and imp in installed}
    if missing:
        issues['missing_requirements'] = missing
        
    # Check for undocumented dependencies
    undocumented = {f"{pkg} (installed: {ver})" 
                   for pkg, ver in installed.items()
                   if pkg in imports and pkg not in required}
    if undocumented:
        issues['undocumented_dependencies'] = undocumented
        
    # Check version mismatches
    mismatches = {f"{pkg} (required: {req_ver}, installed: {installed[pkg]})"
                  for pkg, req_ver in requirements.items()
                  if pkg in installed
                  and installed[pkg] != req_ver}
    if mismatches:
        issues['version_mismatches'] = mismatches
        
    return issues

def test_requirements():
    """Test that requirements.txt is both necessary and sufficient."""
    issues = analyze_requirements()
    
    if issues:
        errors = ["Requirements validation failed!"]
        
        if 'unused_requirements' in issues:
            errors.append("\nPackages in requirements.txt but not imported:")
            for pkg in sorted(issues['unused_requirements']):
                errors.append(f"  - {pkg}")
                
        if 'missing_requirements' in issues:
            errors.append("\nImported packages missing from requirements.txt:")
            for pkg in sorted(issues['missing_requirements']):
                errors.append(f"  - {pkg}")
                
        if 'undocumented_dependencies' in issues:
            errors.append("\nInstalled packages missing from requirements.txt:")
            for pkg in sorted(issues['undocumented_dependencies']):
                errors.append(f"  - {pkg}")
                
        if 'version_mismatches' in issues:
            errors.append("\nVersion mismatches:")
            for pkg in sorted(issues['version_mismatches']):
                errors.append(f"  - {pkg}")
                
        pytest.fail("\n".join(errors))

@pytest.fixture(scope="session", autouse=True)
def requirements_report():
    """Generate requirements report after tests run."""
    yield
    # Add code to generate requirements report here
