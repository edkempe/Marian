"""Test for prohibited library imports."""

import os
import ast
from typing import List, Set


PROHIBITED_LIBRARIES = {
    'alembic': 'Use direct schema verification instead of migrations',
    'django': 'Project uses SQLAlchemy for ORM',
    'flask': 'Project uses FastAPI for web framework',
    'pandas': 'Use built-in data structures for simplicity',
    'tensorflow': 'Use simpler ML libraries when needed',
    'torch': 'Use simpler ML libraries when needed',
}


def get_python_files(start_path: str) -> List[str]:
    """Get all Python files in directory tree."""
    python_files = []
    for root, _, files in os.walk(start_path):
        if 'venv' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files


def get_imports(file_path: str) -> Set[str]:
    """Get all imports from a Python file."""
    with open(file_path, 'r') as file:
        try:
            tree = ast.parse(file.read())
        except SyntaxError:
            print(f"Syntax error in {file_path}")
            return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports


def test_no_prohibited_libraries():
    """Test that no prohibited libraries are imported."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_files = get_python_files(project_root)
    
    violations = []
    for file_path in python_files:
        imports = get_imports(file_path)
        for imp in imports:
            if imp in PROHIBITED_LIBRARIES:
                rel_path = os.path.relpath(file_path, project_root)
                violations.append(
                    f"{rel_path}: uses prohibited library '{imp}'. "
                    f"Reason: {PROHIBITED_LIBRARIES[imp]}"
                )
    
    assert not violations, "\n".join(violations)
