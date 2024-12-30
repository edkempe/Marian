"""Test suite to detect hardcoded values that should be in constants.

This module scans the codebase for values that should be defined in constants.py
rather than being hardcoded in the source code.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pytest

from shared_lib import constants


def get_constants_from_module() -> Set[str]:
    """Extract all constant values from constants.py."""
    constant_values = set()

    # Get all module attributes that look like constants
    for name, value in vars(constants).items():
        if name.isupper():  # Only look at UPPERCASE names (constant convention)
            if isinstance(value, (str, Path)):
                constant_values.add(str(value))
                # Also add variations of paths
                if isinstance(value, (str, Path)) and "/" in str(value):
                    path = str(value)
                    constant_values.add(path.replace("/", os.sep))
                    constant_values.add(os.path.basename(path))
                    constant_values.add(os.path.dirname(path))

    return constant_values


def find_hardcoded_paths(node: ast.AST, constants: Set[str]) -> List[Tuple[int, str]]:
    """Find hardcoded paths in an AST node."""
    hardcoded = []

    for child in ast.walk(node):
        if isinstance(child, ast.Str):
            value = child.s
            if ("/" in value or "\\" in value) and value not in constants:
                # Ignore certain patterns
                if not any(
                    pattern in value.lower()
                    for pattern in [
                        ".git",
                        "__pycache__",
                        ".pytest_cache",
                        "venv",
                        "http://",
                        "https://",
                        ".com/",
                        ".org/",
                        "/test/",
                        "/tests/",
                        "/archive/",
                    ]
                ):
                    hardcoded.append((child.lineno, value))

    return hardcoded


def find_hardcoded_values(file_path: str, constants: Set[str]) -> List[Tuple[int, str]]:
    """Find hardcoded values in a Python file that should be constants."""
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read(), filename=file_path)
        return find_hardcoded_paths(tree, constants)
    except SyntaxError:
        return []  # Skip files with syntax errors


def test_no_hardcoded_paths():
    """Test that there are no hardcoded paths that should be constants."""
    # Get project root directory
    project_root = Path(__file__).parent.parent

    # Get all constant values
    constant_values = get_constants_from_module()

    # Track all violations
    violations = []

    # Scan all Python files
    for py_file in project_root.rglob("*.py"):
        # Skip certain directories
        if any(
            part in str(py_file)
            for part in [
                "__pycache__",
                ".pytest_cache",
                "venv",
                "/tests/",
                "/archive/",
                "/migrations/",
            ]
        ):
            continue

        # Find hardcoded values
        hardcoded = find_hardcoded_values(str(py_file), constant_values)
        if hardcoded:
            rel_path = py_file.relative_to(project_root)
            violations.extend(
                f"{rel_path}:{line} - Hardcoded path: {value}"
                for line, value in hardcoded
            )

    # Report violations
    if violations:
        pytest.fail(
            "Found hardcoded paths that should be constants:\n" + "\n".join(violations)
        )


if __name__ == "__main__":
    pytest.main([__file__])
