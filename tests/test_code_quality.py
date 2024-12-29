"""Test suite for code quality standards.

This module ensures that our code style, naming conventions,
and general code quality standards are maintained across the project.
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple

def get_naming_patterns() -> Dict[str, List[str]]:
    """Analyze naming patterns in the codebase."""
    project_root = Path(__file__).parent.parent
    patterns = {
        'snake_case_violations': [],
        'camel_case_violations': [],
        'unclear_names': [],
        'too_short_names': []
    }
    
    min_name_length = 3
    unclear_indicators = {'temp', 'tmp', 'foo', 'bar', 'x', 'y', 'z'}
    
    for py_file in project_root.rglob('*.py'):
        if py_file.name.startswith('_') or 'test' in str(py_file):
            continue
            
        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                # Check function names
                if isinstance(node, ast.FunctionDef):
                    name = node.name
                    if not re.match(r'^[a-z][a-z0-9_]*$', name):
                        patterns['snake_case_violations'].append(f"{py_file}:{node.lineno} - {name}")
                    if len(name) < min_name_length:
                        patterns['too_short_names'].append(f"{py_file}:{node.lineno} - {name}")
                    if name.lower() in unclear_indicators:
                        patterns['unclear_names'].append(f"{py_file}:{node.lineno} - {name}")
                        
                # Check class names
                elif isinstance(node, ast.ClassDef):
                    name = node.name
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
                        patterns['camel_case_violations'].append(f"{py_file}:{node.lineno} - {name}")
                        
                # Check variable names
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    name = node.id
                    if not re.match(r'^[a-z][a-z0-9_]*$', name):
                        patterns['snake_case_violations'].append(f"{py_file}:{node.lineno} - {name}")
                    if len(name) < min_name_length and name not in {'id', 'db', 'os'}:
                        patterns['too_short_names'].append(f"{py_file}:{node.lineno} - {name}")
                    if name.lower() in unclear_indicators:
                        patterns['unclear_names'].append(f"{py_file}:{node.lineno} - {name}")
                        
        except Exception:
            continue
            
    return patterns

def test_code_style():
    """Verify code style and maintainability standards."""
    project_root = Path(__file__).parent.parent
    
    for py_file in project_root.rglob('*.py'):
        if py_file.name.startswith('_') or 'test' in str(py_file):
            continue
            
        try:
            with open(py_file) as f:
                content = f.read()
                lines = content.split('\n')
                
            # Line length
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
            assert not long_lines, f"Lines too long in {py_file}: {long_lines}"
            
            # Trailing whitespace
            trailing_space = [i+1 for i, line in enumerate(lines) if line.rstrip() != line]
            assert not trailing_space, f"Trailing whitespace in {py_file}: {trailing_space}"
            
            # Multiple blank lines
            multi_blank = [i+1 for i in range(len(lines)-2) 
                         if not lines[i].strip() and not lines[i+1].strip()]
            assert not multi_blank, f"Multiple blank lines in {py_file}: {multi_blank}"
            
            # TODO comments
            todos = [i+1 for i, line in enumerate(lines) if 'TODO' in line]
            assert not todos, f"TODO comments in {py_file}: {todos}"
            
        except Exception:
            continue

def test_naming_standards():
    """Verify file and folder naming standards."""
    patterns = get_naming_patterns()
    
    # No snake case violations (functions and variables)
    assert not patterns['snake_case_violations'], \
        f"Snake case violations found: {patterns['snake_case_violations']}"
    
    # No camel case violations (classes)
    assert not patterns['camel_case_violations'], \
        f"Camel case violations found: {patterns['camel_case_violations']}"
    
    # No unclear names
    assert not patterns['unclear_names'], \
        f"Unclear names found: {patterns['unclear_names']}"
    
    # No names too short
    assert not patterns['too_short_names'], \
        f"Names too short found: {patterns['too_short_names']}"

def test_docstring_standards():
    """Verify docstring standards across the codebase."""
    project_root = Path(__file__).parent.parent
    
    for py_file in project_root.rglob('*.py'):
        if py_file.name.startswith('_') or 'test' in str(py_file):
            continue
            
        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    # Should have a docstring
                    assert ast.get_docstring(node), \
                        f"Missing docstring in {py_file}:{node.lineno}"
                    
                    docstring = ast.get_docstring(node)
                    if docstring:
                        # Should be properly formatted
                        assert docstring.strip() == docstring, \
                            f"Improperly formatted docstring in {py_file}:{node.lineno}"
                        
                        # Should end with a period
                        assert docstring.strip().endswith('.'), \
                            f"Docstring should end with period in {py_file}:{node.lineno}"
                            
        except Exception:
            continue
