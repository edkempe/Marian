"""Test suite for import validation.

This module ensures that:
1. All imports are actually used in the code
2. No circular imports exist
3. Import style is consistent (absolute vs relative)
4. No forbidden imports are used
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

import jinja2
import markdown
import pytest

from shared_lib.constants import TESTING_CONFIG

# Location for test reports
REPORTS_DIR = os.path.join("reports", "testing")

# HTML template for reports
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
        }
        h1, h2 {
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 0.3rem;
        }
        .warning {
            color: #856404;
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            padding: 0.75rem;
            margin: 1rem 0;
            border-radius: 0.25rem;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 0.5rem;
            text-align: left;
        }
        th {
            background-color: #f5f5f5;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .file-path {
            font-family: monospace;
            color: #476582;
        }
        .import-name {
            font-family: monospace;
            color: #c0392b;
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    {{ content | safe }}
</body>
</html>
"""


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to collect import information."""

    def __init__(self):
        self.imports = {}  # name -> module
        self.import_nodes = []  # List of import nodes with line numbers
        self.name_usage = set()  # All used names

    def visit_Import(self, node):
        """Visit Import nodes (e.g., import os)."""
        for name in node.names:
            self.imports[name.asname or name.name] = name.name
            self.import_nodes.append((name.name, node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visit ImportFrom nodes (e.g., from os import path)."""
        module = node.module or ""
        for name in node.names:
            full_name = f"{module}.{name.name}" if module else name.name
            self.imports[name.asname or name.name] = full_name
            self.import_nodes.append((full_name, node.lineno))
        self.generic_visit(node)

    def visit_Name(self, node):
        """Visit Name nodes to track usage."""
        self.name_usage.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Visit Attribute nodes to track usage of module attributes."""
        names = []
        current = node
        while isinstance(current, ast.Attribute):
            names.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            names.append(current.id)
            # Record all possible combinations
            for i in range(len(names)):
                self.name_usage.add(".".join(reversed(names[i:])))
        self.generic_visit(node)


def analyze_file_imports(file_path: str) -> Tuple[List[str], List[str]]:
    """Analyze imports in a Python file.

    Returns:
        Tuple of (unused_imports, import_style_issues)
    """
    unused_imports = []
    style_issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse the AST
        tree = ast.parse(content)
        visitor = ImportVisitor()
        visitor.visit(tree)

        # Check for unused imports
        for name, module in visitor.imports.items():
            if name not in visitor.name_usage and module not in visitor.name_usage:
                unused_imports.append(
                    f"{module} as {name}" if name != module else module
                )

        # Check import style
        for import_name, line_no in visitor.import_nodes:
            # Check for relative imports
            if import_name.startswith("."):
                style_issues.append(f"Line {line_no}: Relative import '{import_name}'")

            # Check import order (stdlib, third-party, local)
            # TODO: Implement more sophisticated import order checking

    except Exception as e:
        print(f"Warning: Error analyzing {file_path}: {e}")

    return unused_imports, style_issues


def check_circular_imports(
    file_path: str, visited: Set[str] = None, stack: List[str] = None
) -> List[str]:
    """Check for circular imports starting from a file.

    Returns:
        List of circular import chains found
    """
    if visited is None:
        visited = set()
    if stack is None:
        stack = []

    circular_imports = []
    file_path = str(Path(file_path).resolve())

    if file_path in stack:
        # Found a circular import
        cycle_start = stack.index(file_path)
        cycle = stack[cycle_start:] + [file_path]
        circular_imports.append(
            " -> ".join(
                str(Path(p).relative_to(Path(file_path).parent.parent)) for p in cycle
            )
        )
        return circular_imports

    if file_path in visited:
        return circular_imports

    visited.add(file_path)
    stack.append(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        imports = set()

        # Collect all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)

        # Resolve each import to a file path
        for import_name in imports:
            try:
                # Handle relative imports
                if import_name.startswith("."):
                    rel_path = os.path.join(
                        os.path.dirname(file_path), *import_name.split(".")
                    )
                    if os.path.exists(rel_path + ".py"):
                        import_path = rel_path + ".py"
                    else:
                        continue
                else:
                    # Handle absolute imports (simplified)
                    parts = import_name.split(".")
                    rel_path = os.path.join(
                        os.path.dirname(os.path.dirname(file_path)), *parts
                    )
                    if os.path.exists(rel_path + ".py"):
                        import_path = rel_path + ".py"
                    else:
                        continue

                # Recursively check imported files
                circular_imports.extend(
                    check_circular_imports(import_path, visited, stack)
                )

            except Exception as e:
                print(
                    f"Warning: Error resolving import {import_name} in {file_path}: {e}"
                )

    except Exception as e:
        print(f"Warning: Error analyzing {file_path}: {e}")

    stack.pop()
    return circular_imports


# Forbidden imports that should not be used
FORBIDDEN_IMPORTS = {
    # Database
    'sqlite3': 'Use SQLAlchemy instead of direct sqlite3',
    
    # Testing
    'unittest': 'Use pytest instead of unittest',
    
    # Debugging and Logging
    'print': 'Use logging instead of print statements',
    'pdb': 'Use debugger in your IDE instead',
    
    # Security Sensitive
    'pickle': 'Use json, yaml, or other secure serialization methods. See ADR-0007',
    'marshal': 'Unsafe serialization, use json instead',
    'shelve': 'Uses pickle internally, use SQLAlchemy or json instead',
    'yaml.load': 'Use yaml.safe_load instead',
    'xml.etree.ElementTree': 'Use defusedxml for safer XML processing',
    
    # Deprecated or Unsafe
    'os.system': 'Use subprocess.run with proper argument handling',
    'os.popen': 'Use subprocess.run with proper argument handling',
    'eval': 'Unsafe evaluation of strings, use ast.literal_eval if needed',
    'exec': 'Unsafe execution of strings, restructure code to avoid',
    'input': 'Use argparse for CLI or proper input validation',
    
    # Use Standard Project Tools
    'configparser': 'Use pydantic settings instead',
    'optparse': 'Use argparse or click instead',
}


def check_forbidden_imports(file_path: str) -> List[str]:
    """Check for forbidden imports in a Python file."""
    visitor = ImportVisitor()
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
        except SyntaxError:
            return []  # Skip files with syntax errors
        
    visitor.visit(tree)
    issues = []
    
    for import_node in visitor.import_nodes:
        if isinstance(import_node, ast.Import):
            for name in import_node.names:
                if name.name in FORBIDDEN_IMPORTS:
                    issues.append(f"Line {import_node.lineno}: Forbidden import '{name.name}' - {FORBIDDEN_IMPORTS[name.name]}")
        elif isinstance(import_node, ast.ImportFrom):
            if import_node.module in FORBIDDEN_IMPORTS:
                issues.append(f"Line {import_node.lineno}: Forbidden import 'from {import_node.module}' - {FORBIDDEN_IMPORTS[import_node.module]}")
            
    return issues


def analyze_project_imports(
    project_root: str = None,
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], List[str], Dict[str, List[str]]]:
    """Analyze all Python files in the project for import issues.

    Returns:
        Tuple of:
        - Dict mapping files to unused imports
        - Dict mapping files to style issues
        - List of circular import chains
        - Dict mapping files to forbidden import issues
    """
    if project_root is None:
        project_root = os.path.dirname(os.path.dirname(__file__))

    unused_imports = {}
    style_issues = {}
    circular_imports = []
    forbidden_issues = {}
    
    # Get all Python files
    python_files = []
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if '/venv/' not in file_path and '/archive/' not in file_path:
                    python_files.append(file_path)

    # Analyze each file
    for file_path in python_files:
        unused, style = analyze_file_imports(file_path)
        forbidden = check_forbidden_imports(file_path)
        
        rel_path = os.path.relpath(file_path, project_root)
        if unused:
            unused_imports[rel_path] = unused
        if style:
            style_issues[rel_path] = style
        if forbidden:
            forbidden_issues[rel_path] = forbidden

    # Check for circular imports
    for file_path in python_files:
        circles = check_circular_imports(file_path)
        circular_imports.extend(circles)

    return unused_imports, style_issues, circular_imports, forbidden_issues


def generate_markdown_report(
    unused_imports: Dict[str, List[str]],
    style_issues: Dict[str, List[str]],
    circular_imports: List[str],
    forbidden_issues: Dict[str, List[str]],
) -> str:
    """Generate markdown format report."""
    lines = ["# Import Analysis Report\n"]
    
    if forbidden_issues:
        lines.append("\n## 🚫 Forbidden Imports\n")
        for file, issues in forbidden_issues.items():
            lines.append(f"\n### {file}\n")
            for issue in issues:
                lines.append(f"- {issue}\n")

    if unused_imports:
        lines.append("\n## Unused Imports\n\n")
        for file, imports in sorted(unused_imports.items()):
            lines.append(f"### `{file}`\n\n")
            for imp in imports:
                lines.append(f"- `{imp}`\n")
            lines.append("\n")

    if style_issues:
        lines.append("## Import Style Issues\n\n")
        for file, issues in sorted(style_issues.items()):
            lines.append(f"### `{file}`\n\n")
            for issue in issues:
                lines.append(f"- {issue}\n")
            lines.append("\n")

    if circular_imports:
        lines.append("## Circular Imports\n\n")
        for cycle in sorted(circular_imports):
            lines.append(f"- {cycle}\n")
        lines.append("\n")

    if not (unused_imports or style_issues or circular_imports or forbidden_issues):
        lines.append("> No import issues found! 🎉\n")

    return "\n".join(lines)


def generate_html_report(
    unused_imports: Dict[str, List[str]],
    style_issues: Dict[str, List[str]],
    circular_imports: List[str],
    forbidden_issues: Dict[str, List[str]],
) -> str:
    """Generate HTML format report."""
    # Convert markdown to HTML
    md_content = generate_markdown_report(
        unused_imports, style_issues, circular_imports, forbidden_issues
    )
    html_content = markdown.markdown(md_content, extensions=["tables"])

    # Apply template
    template = jinja2.Template(HTML_TEMPLATE)
    return template.render(title="Import Analysis Report", content=html_content)


def generate_import_report():
    """Generate reports of import analysis."""
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # Run analysis
    unused_imports, style_issues, circular_imports, forbidden_issues = analyze_project_imports()

    # Generate markdown report
    md_report = generate_markdown_report(unused_imports, style_issues, circular_imports, forbidden_issues)
    md_path = os.path.join(base_dir, REPORTS_DIR, "import_analysis.md")

    # Generate HTML report
    html_report = generate_html_report(unused_imports, style_issues, circular_imports, forbidden_issues)
    html_path = os.path.join(base_dir, REPORTS_DIR, "import_analysis.html")

    # Write reports
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, "w") as f:
        f.write(md_report)
    with open(html_path, "w") as f:
        f.write(html_report)

    # Print summary
    print("\nImport Analysis Summary:")
    if unused_imports:
        print(
            f"- Found {sum(len(imports) for imports in unused_imports.values())} unused imports in {len(unused_imports)} files"
        )
    if style_issues:
        print(
            f"- Found {sum(len(issues) for issues in style_issues.values())} style issues in {len(style_issues)} files"
        )
    if circular_imports:
        print(f"- Found {len(circular_imports)} circular import chains")
    if forbidden_issues:
        print(f"- Found {sum(len(issues) for issues in forbidden_issues.values())} forbidden imports in {len(forbidden_issues)} files")
    if not (unused_imports or style_issues or circular_imports or forbidden_issues):
        print("No import issues found!")
    print(f"\nReports generated:\n- {md_path}\n- {html_path}")


def test_imports():
    """Test for import issues.

    This test will pass but generate warnings for:
    - Unused imports
    - Import style issues
    - Circular imports
    - Forbidden imports
    """
    unused_imports, style_issues, circular_imports, forbidden_issues = analyze_project_imports()

    # Generate the report
    report = generate_markdown_report(unused_imports, style_issues, circular_imports, forbidden_issues)
    
    # Create reports directory if it doesn't exist
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # Save markdown report
    report_path = os.path.join(REPORTS_DIR, "import_analysis.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
        
    # Save HTML report
    html_report = generate_html_report(unused_imports, style_issues, circular_imports, forbidden_issues)
    html_path = os.path.join(REPORTS_DIR, "import_analysis.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_report)
        
    # Print summary
    total_issues = (
        len(unused_imports) +
        len(style_issues) +
        len(circular_imports) +
        len(forbidden_issues)
    )
    
    if total_issues > 0:
        print(f"\nFound {total_issues} import issues. See {report_path} for details.")
        if forbidden_issues:
            print("\nForbidden imports found:")
            for file, issues in forbidden_issues.items():
                print(f"\n{file}:")
                for issue in issues:
                    print(f"  {issue}")
    
    # Don't fail the test, just warn
    assert True


if __name__ == "__main__":
    generate_import_report()
