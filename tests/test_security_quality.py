"""Test suite for security and data privacy standards.

This module ensures that our security practices, error handling,
and data privacy standards are maintained across the project.
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple

def get_security_issues() -> List[Dict]:
    """Scan for potential security issues."""
    project_root = Path(__file__).parent.parent
    issues = []
    
    # Skip virtual environment and test files
    def should_check_file(file_path: Path) -> bool:
        return not any(part in str(file_path) for part in ['venv', '.env', '__pycache__', '.git', 'tests'])
    
    security_patterns = {
        'hardcoded_secret': r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
        'sql_injection': r'execute\([\'"].*?\%.*?[\'"]\s*%',
        'unsafe_pickle': r'pickle\.loads\(',
        'unsafe_yaml': r'yaml\.load\(',
        'command_injection': r'subprocess\.call\([\'"].*?\%.*?[\'"]\s*%',
    }
    
    for py_file in project_root.rglob('*.py'):
        if not should_check_file(py_file):
            continue
            
        try:
            with open(py_file) as f:
                content = f.read()
                
            for issue_type, pattern in security_patterns.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    issues.append({
                        'type': issue_type,
                        'file': str(py_file),
                        'line': content.count('\n', 0, match.start()) + 1,
                        'snippet': match.group(0)
                    })
                    
        except Exception:
            continue
            
    return issues

def get_error_handlers() -> List[Dict]:
    """Check error handling practices in the codebase."""
    project_root = Path(__file__).parent.parent
    handlers = []
    
    # Skip virtual environment and test files
    def should_check_file(file_path: Path) -> bool:
        return not any(part in str(file_path) for part in ['venv', '.env', '__pycache__', '.git', 'tests'])
    
    for py_file in project_root.rglob('*.py'):
        if not should_check_file(py_file):
            continue
            
        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    handlers.append({
                        'file': str(py_file),
                        'line': node.lineno,
                        'exception': node.type.id if node.type else 'all',
                        'has_logging': any('logging' in ast.dump(n) for n in ast.walk(node))
                    })
                    
        except Exception:
            continue
            
    return handlers

def get_data_handling_patterns() -> Dict[str, List[str]]:
    """Analyze code for data handling patterns."""
    project_root = Path(__file__).parent.parent
    patterns = {
        'pii_fields': [],
        'data_validation': [],
        'data_sanitization': [],
        'encryption_usage': []
    }
    
    pii_indicators = {'email', 'password', 'phone', 'address', 'name', 'ssn', 'dob'}
    
    for py_file in project_root.rglob('*.py'):
        if py_file.name.startswith('_') or 'test' in str(py_file):
            continue
            
        try:
            with open(py_file) as f:
                content = f.read()
                tree = ast.parse(content)
                
            # Look for PII fields
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and any(pii in node.id.lower() for pii in pii_indicators):
                    patterns['pii_fields'].append(f"{py_file}:{node.lineno} - {node.id}")
                    
            # Look for data validation
            if 'validator' in content.lower() or 'schema' in content.lower():
                patterns['data_validation'].append(str(py_file))
                
            # Look for data sanitization
            if 'sanitize' in content.lower() or 'escape' in content.lower():
                patterns['data_sanitization'].append(str(py_file))
                
            # Look for encryption usage
            if 'encrypt' in content.lower() or 'decrypt' in content.lower():
                patterns['encryption_usage'].append(str(py_file))
                
        except Exception:
            continue
            
    return patterns

def test_security_compliance():
    """Validate security practices."""
    issues = get_security_issues()
    
    # No hardcoded secrets
    secret_issues = [i for i in issues if i['type'] == 'hardcoded_secret']
    assert not secret_issues, f"Found hardcoded secrets: {secret_issues}"
    
    # No SQL injection vulnerabilities
    sql_issues = [i for i in issues if i['type'] == 'sql_injection']
    assert not sql_issues, f"Found potential SQL injection: {sql_issues}"
    
    # No unsafe deserialization
    unsafe_deser = [i for i in issues if i['type'] in ('unsafe_pickle', 'unsafe_yaml')]
    assert not unsafe_deser, f"Found unsafe deserialization: {unsafe_deser}"
    
    # No command injection vulnerabilities
    cmd_issues = [i for i in issues if i['type'] == 'command_injection']
    assert not cmd_issues, f"Found potential command injection: {cmd_issues}"

def test_error_handling():
    """Verify error handling practices."""
    handlers = get_error_handlers()
    
    # No bare except clauses
    bare_excepts = [h for h in handlers if h['exception'] == 'all']
    assert not bare_excepts, f"Found bare except clauses: {bare_excepts}"
    
    # All error handlers should include logging
    no_logging = [h for h in handlers if not h['has_logging']]
    assert not no_logging, f"Error handlers missing logging: {no_logging}"

def test_data_privacy():
    """Verify data privacy and compliance standards."""
    patterns = get_data_handling_patterns()
    
    # All PII fields should be in validated/sanitized files
    pii_files = {p.split(':')[0] for p in patterns['pii_fields']}
    validated_files = set(patterns['data_validation'])
    unvalidated_pii = pii_files - validated_files
    assert not unvalidated_pii, f"PII fields in files without validation: {unvalidated_pii}"
    
    # Files with PII should use encryption
    encrypted_files = set(patterns['encryption_usage'])
    unencrypted_pii = pii_files - encrypted_files
    assert not unencrypted_pii, f"PII fields in files without encryption: {unencrypted_pii}"
    
    # Files with PII should use data sanitization
    sanitized_files = set(patterns['data_sanitization'])
    unsanitized_pii = pii_files - sanitized_files
    assert not unsanitized_pii, f"PII fields in files without sanitization: {unsanitized_pii}"
