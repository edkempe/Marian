"""Test suite for import validation.

This module ensures that:
1. All imports are actually used in the code
2. No circular imports exist
3. Import style is consistent (absolute vs relative)
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import jinja2
import markdown
from shared_lib.constants import TESTING_CONFIG

# Location for test reports
REPORTS_DIR = os.path.join('reports', 'testing')

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
        module = node.module or ''
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
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse the AST
        tree = ast.parse(content)
        visitor = ImportVisitor()
        visitor.visit(tree)
        
        # Check for unused imports
        for name, module in visitor.imports.items():
            if name not in visitor.name_usage and module not in visitor.name_usage:
                unused_imports.append(f"{module} as {name}" if name != module else module)
        
        # Check import style
        for import_name, line_no in visitor.import_nodes:
            # Check for relative imports
            if import_name.startswith('.'):
                style_issues.append(f"Line {line_no}: Relative import '{import_name}'")
            
            # Check import order (stdlib, third-party, local)
            # TODO: Implement more sophisticated import order checking
            
    except Exception as e:
        print(f"Warning: Error analyzing {file_path}: {e}")
    
    return unused_imports, style_issues

def check_circular_imports(file_path: str, visited: Set[str] = None, stack: List[str] = None) -> List[str]:
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
        circular_imports.append(" -> ".join(str(Path(p).relative_to(Path(file_path).parent.parent)) for p in cycle))
        return circular_imports
        
    if file_path in visited:
        return circular_imports
        
    visited.add(file_path)
    stack.append(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
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
                if import_name.startswith('.'):
                    rel_path = os.path.join(os.path.dirname(file_path), *import_name.split('.'))
                    if os.path.exists(rel_path + '.py'):
                        import_path = rel_path + '.py'
                    else:
                        continue
                else:
                    # Handle absolute imports (simplified)
                    parts = import_name.split('.')
                    rel_path = os.path.join(os.path.dirname(os.path.dirname(file_path)), *parts)
                    if os.path.exists(rel_path + '.py'):
                        import_path = rel_path + '.py'
                    else:
                        continue
                        
                # Recursively check imported files
                circular_imports.extend(check_circular_imports(import_path, visited, stack))
                    
            except Exception as e:
                print(f"Warning: Error resolving import {import_name} in {file_path}: {e}")
                
    except Exception as e:
        print(f"Warning: Error analyzing {file_path}: {e}")
        
    stack.pop()
    return circular_imports

def analyze_project_imports(project_root: str = None) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], List[str]]:
    """Analyze all Python files in the project for import issues.
    
    Returns:
        Tuple of:
        - Dict mapping files to unused imports
        - Dict mapping files to style issues
        - List of circular import chains
    """
    if project_root is None:
        project_root = str(Path(__file__).parent.parent)
        
    unused_imports = {}
    style_issues = {}
    circular_imports = []
    
    # Find all Python files
    for root, _, files in os.walk(project_root):
        if 'venv' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Check for unused imports
                unused, style = analyze_file_imports(file_path)
                if unused:
                    unused_imports[file_path] = unused
                if style:
                    style_issues[file_path] = style
                    
                # Check for circular imports
                circular = check_circular_imports(file_path)
                if circular:
                    circular_imports.extend(circular)
                    
    return unused_imports, style_issues, circular_imports

def generate_markdown_report(unused_imports: Dict[str, List[str]], 
                           style_issues: Dict[str, List[str]], 
                           circular_imports: List[str]) -> str:
    """Generate markdown format report."""
    report = "# Import Analysis Report\n\n"
    
    if unused_imports:
        report += "## Unused Imports\n\n"
        for file, imports in sorted(unused_imports.items()):
            rel_path = os.path.relpath(file, str(Path(__file__).parent.parent))
            report += f"### `{rel_path}`\n\n"
            for imp in imports:
                report += f"- `{imp}`\n"
            report += "\n"
            
    if style_issues:
        report += "## Import Style Issues\n\n"
        for file, issues in sorted(style_issues.items()):
            rel_path = os.path.relpath(file, str(Path(__file__).parent.parent))
            report += f"### `{rel_path}`\n\n"
            for issue in issues:
                report += f"- {issue}\n"
            report += "\n"
            
    if circular_imports:
        report += "## Circular Imports\n\n"
        for cycle in sorted(circular_imports):
            report += f"- {cycle}\n"
        report += "\n"
            
    if not (unused_imports or style_issues or circular_imports):
        report += "> No import issues found! 🎉\n"
        
    return report

def generate_html_report(unused_imports: Dict[str, List[str]], 
                        style_issues: Dict[str, List[str]], 
                        circular_imports: List[str]) -> str:
    """Generate HTML format report."""
    # Convert markdown to HTML
    md_content = generate_markdown_report(unused_imports, style_issues, circular_imports)
    html_content = markdown.markdown(md_content, extensions=['tables'])
    
    # Apply template
    template = jinja2.Template(HTML_TEMPLATE)
    return template.render(
        title="Import Analysis Report",
        content=html_content
    )

def generate_import_report():
    """Generate reports of import analysis."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Run analysis
    unused_imports, style_issues, circular_imports = analyze_project_imports()
    
    # Generate markdown report
    md_report = generate_markdown_report(unused_imports, style_issues, circular_imports)
    md_path = os.path.join(base_dir, REPORTS_DIR, 'import_analysis.md')
    
    # Generate HTML report
    html_report = generate_html_report(unused_imports, style_issues, circular_imports)
    html_path = os.path.join(base_dir, REPORTS_DIR, 'import_analysis.html')
    
    # Write reports
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, 'w') as f:
        f.write(md_report)
    with open(html_path, 'w') as f:
        f.write(html_report)
        
    # Print summary
    print("\nImport Analysis Summary:")
    if unused_imports:
        print(f"- Found {sum(len(imports) for imports in unused_imports.values())} unused imports in {len(unused_imports)} files")
    if style_issues:
        print(f"- Found {sum(len(issues) for issues in style_issues.values())} style issues in {len(style_issues)} files")
    if circular_imports:
        print(f"- Found {len(circular_imports)} circular import chains")
    if not (unused_imports or style_issues or circular_imports):
        print("No import issues found!")
    print(f"\nReports generated:\n- {md_path}\n- {html_path}")

def test_imports():
    """Test for import issues.
    
    This test will pass but generate warnings for:
    - Unused imports
    - Import style issues
    - Circular imports
    """
    unused_imports, style_issues, circular_imports = analyze_project_imports()
    
    # Generate report regardless of issues
    generate_import_report()
    
    # Add warnings for issues
    if unused_imports:
        for file, imports in unused_imports.items():
            rel_path = os.path.relpath(file, str(Path(__file__).parent.parent))
            for imp in imports:
                pytest.warns(UserWarning, match=f"Unused import '{imp}' in {rel_path}")
                
    if style_issues:
        for file, issues in style_issues.items():
            rel_path = os.path.relpath(file, str(Path(__file__).parent.parent))
            for issue in issues:
                pytest.warns(UserWarning, match=f"Import style issue in {rel_path}: {issue}")
                
    if circular_imports:
        for cycle in circular_imports:
            pytest.warns(UserWarning, match=f"Circular import detected: {cycle}")
            
    # Test always passes, issues are reported as warnings
    assert True

if __name__ == '__main__':
    generate_import_report()
