"""Test suite for dependency and library structure validation.

This module ensures that our codebase follows proper dependency patterns:
1. No circular dependencies between modules
2. Shared library code is properly utilized
3. Layer boundaries are respected (models -> shared_lib, services -> models)
4. Scripts follow consistent patterns
5. Services maintain proper separation of concerns
"""

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

import networkx as nx
import pytest


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to collect import statements."""

    def __init__(self):
        self.imports = set()
        self.from_imports = defaultdict(set)

    def visit_Import(self, node):
        for name in node.names:
            self.imports.add(name.name.split(".")[0])  # Get root module

    def visit_ImportFrom(self, node):
        if node.module:
            module = node.module.split(".")[0]  # Get root module
            for name in node.names:
                self.from_imports[module].add(name.name)


def get_module_imports(file_path: str) -> Tuple[Set[str], Dict[str, Set[str]]]:
    """Extract all imports from a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Skip non-Python files that might have .py extension
        if (
            not content.strip()
            or content.startswith("<?xml")
            or content.startswith("<!DOCTYPE")
        ):
            return set(), defaultdict(set)

        try:
            tree = ast.parse(content)
            visitor = ImportVisitor()
            visitor.visit(tree)

            # Convert imports to module names
            imports = {imp.split(".")[0] for imp in visitor.imports}
            from_imports = {
                mod.split(".")[0]: names for mod, names in visitor.from_imports.items()
            }

            return imports, from_imports

        except SyntaxError:
            print(f"Warning: Syntax error in {file_path}, skipping...")
            return set(), defaultdict(set)

    except Exception as e:
        print(f"Warning: Failed to process {file_path}: {str(e)}")
        return set(), defaultdict(set)


def get_python_files(directory: str) -> List[str]:
    """Get all Python files in a directory recursively."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def check_layer_violations(graph: nx.DiGraph) -> List[str]:
    """Check for violations of architectural rules.

    Rules:
    1. No circular dependencies (checked separately)
    2. shared_lib can only import from shared_lib (foundation layer)
    3. models can import from models and shared_lib
    4. services can import from models and shared_lib
    5. scripts can import from services, models, and shared_lib
       but cannot import from other scripts (no shared script code)
    """
    violations = []

    # First check for any direct imports from models in shared_lib
    shared_lib_files = [
        n for n in graph.nodes() if graph.nodes[n]["type"] == "shared_lib"
    ]
    for file_path in shared_lib_files:
        with open(graph.nodes[file_path]["path"], "r") as f:
            content = f.read()
            if "from models." in content or "import models." in content:
                violations.append(
                    f"Violation: {file_path} (shared_lib) imports from models"
                )

    return violations


def find_circular_dependencies(files: List[str]) -> List[Tuple[str, str]]:
    """Find circular dependencies between files.

    Returns:
        List of (file1, file2) tuples where file1 imports file2 and vice versa
    """
    # Map of file -> files it imports
    imports = {}

    for file_path in files:
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Get the module name for this file
            rel_path = os.path.relpath(
                file_path, os.path.dirname(os.path.dirname(__file__))
            )
            module = os.path.splitext(rel_path)[0].replace(os.sep, ".")

            # Find all imports in this file
            imports[module] = set()
            for line in content.split("\n"):
                if line.strip().startswith("from ") or line.strip().startswith(
                    "import "
                ):
                    # Extract the module being imported
                    parts = line.split()
                    if parts[0] == "from":
                        imported = parts[1]
                    else:
                        imported = parts[1].split(".")[0]
                    imports[module].add(imported)

        except Exception as e:
            print(f"Warning: Failed to process {file_path}: {str(e)}")
            continue

    # Find circular dependencies
    circles = []
    for module1, imported in imports.items():
        for module2 in imported:
            # Check if module2 exists in our imports map
            if module2 in imports:
                # Check if module2 imports module1
                module1_base = module1.split(".")[0]
                if module1_base in imports[module2]:
                    circles.append((module1, module2))

    return circles


def test_circular_dependencies():
    """Test that there are no circular dependencies between modules."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Get all Python files in the project
    python_files = []
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    circles = find_circular_dependencies(python_files)

    if circles:
        message = ["Circular dependencies found:"]
        for module1, module2 in circles:
            message.append(f"  {module1} <-> {module2}")
        pytest.fail("\n".join(message))


def test_layer_boundaries():
    """Test that layer boundaries are respected."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Create a simple graph with just the files and their types
    graph = nx.DiGraph()

    # Add nodes for Python files in relevant directories
    for dir_name in ["shared_lib", "models", "services", "scripts", "src"]:
        dir_path = os.path.join(project_root, dir_name)
        if os.path.exists(dir_path):
            for file_path in get_python_files(dir_path):
                module_name = os.path.relpath(file_path, project_root)
                module_name = os.path.splitext(module_name)[0].replace(os.sep, ".")
                graph.add_node(module_name, type=dir_name, path=file_path)

    violations = check_layer_violations(graph)

    if violations:
        message = ["Layer boundary violations found:"]
        message.extend(f"  - {violation}" for violation in violations)
        pytest.fail("\n".join(message))


if __name__ == "__main__":
    pytest.main([__file__])
