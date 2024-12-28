"""Test suite for dependency and library structure validation.

This module ensures that our codebase follows proper dependency patterns:
1. No circular dependencies between modules
2. Shared library code is properly utilized
3. Layer boundaries are respected (models -> shared_lib, services -> models)
4. Scripts follow consistent patterns
5. Services maintain proper separation of concerns
"""

import os
import ast
import sys
import pytest
from typing import Dict, Set, List, Tuple
from collections import defaultdict
import networkx as nx
from pathlib import Path

class ImportVisitor(ast.NodeVisitor):
    """AST visitor to collect import statements."""
    
    def __init__(self):
        self.imports = set()
        self.from_imports = defaultdict(set)
        
    def visit_Import(self, node):
        for name in node.names:
            self.imports.add(name.name)
            
    def visit_ImportFrom(self, node):
        if node.module:
            module = node.module
            for name in node.names:
                self.from_imports[module].add(name.name)

def get_module_imports(file_path: str) -> Tuple[Set[str], Dict[str, Set[str]]]:
    """Extract all imports from a Python file."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    visitor = ImportVisitor()
    visitor.visit(tree)
    return visitor.imports, visitor.from_imports

def get_python_files(directory: str) -> List[str]:
    """Get all Python files in a directory recursively."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('_'):
                python_files.append(os.path.join(root, file))
    return python_files

def build_dependency_graph() -> nx.DiGraph:
    """Build a directed graph of module dependencies."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    graph = nx.DiGraph()
    
    # Map absolute paths to module names
    path_to_module = {}
    for directory in ['models', 'services', 'shared_lib', 'scripts']:
        dir_path = os.path.join(project_root, directory)
        if os.path.exists(dir_path):
            for file_path in get_python_files(dir_path):
                rel_path = os.path.relpath(file_path, project_root)
                module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
                path_to_module[file_path] = module_name
                graph.add_node(module_name, type=directory)
    
    # Add edges for imports
    for file_path, module_name in path_to_module.items():
        imports, from_imports = get_module_imports(file_path)
        
        # Add direct imports
        for imp in imports:
            if imp in path_to_module.values():
                graph.add_edge(module_name, imp)
        
        # Add from imports
        for from_module, names in from_imports.items():
            if from_module in path_to_module.values():
                graph.add_edge(module_name, from_module)
    
    return graph

def find_circular_dependencies(graph: nx.DiGraph) -> List[List[str]]:
    """Find all circular dependencies in the graph."""
    try:
        cycles = list(nx.simple_cycles(graph))
        return [cycle for cycle in cycles if len(cycle) > 1]
    except nx.NetworkXNoCycle:
        return []

def check_layer_violations(graph: nx.DiGraph) -> List[Tuple[str, str]]:
    """Check for violations of layering rules."""
    violations = []
    
    for source, target in graph.edges():
        source_type = graph.nodes[source]['type']
        target_type = graph.nodes[target]['type']
        
        # Models should only import from shared_lib
        if source_type == 'models' and target_type not in ['shared_lib']:
            violations.append((source, target))
        
        # Services can import from models and shared_lib
        if source_type == 'services' and target_type not in ['models', 'shared_lib']:
            violations.append((source, target))
        
        # Scripts can import from anywhere
        # shared_lib should not import from other layers
        if source_type == 'shared_lib' and target_type != 'shared_lib':
            violations.append((source, target))
    
    return violations

def find_unused_shared_lib(graph: nx.DiGraph) -> Set[str]:
    """Find shared_lib modules that aren't imported anywhere."""
    shared_lib_modules = {node for node, attrs in graph.nodes(data=True)
                         if attrs['type'] == 'shared_lib'}
    used_modules = {target for _, target in graph.edges()
                   if target in shared_lib_modules}
    return shared_lib_modules - used_modules

def check_script_patterns(graph: nx.DiGraph) -> List[str]:
    """Check scripts for consistent patterns and potential issues."""
    issues = []
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts_dir = os.path.join(project_root, 'scripts')
    
    if not os.path.exists(scripts_dir):
        return issues
    
    for script_file in get_python_files(scripts_dir):
        with open(script_file, 'r') as f:
            content = f.read()
            
        # Check for main guard
        if '__main__' not in content:
            issues.append(f"{script_file}: Missing if __name__ == '__main__' guard")
        
        # Check for proper argument parsing
        if 'argparse' not in content and 'click' not in content:
            issues.append(f"{script_file}: No argument parsing found")
        
        # Check for proper error handling
        if 'try:' not in content:
            issues.append(f"{script_file}: No error handling found")
    
    return issues

def check_service_patterns(graph: nx.DiGraph) -> List[str]:
    """Check services for proper patterns and separation of concerns."""
    issues = []
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    services_dir = os.path.join(project_root, 'services')
    
    if not os.path.exists(services_dir):
        return issues
    
    for service_file in get_python_files(services_dir):
        with open(service_file, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
        
        # Check for class-based services
        has_class = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
        if not has_class:
            issues.append(f"{service_file}: No service class found")
        
        # Check for direct database access (should go through models)
        if 'session.' in content and 'model.' not in content:
            issues.append(f"{service_file}: Direct database access without model")
        
        # Check for proper error handling
        if 'Exception' not in content:
            issues.append(f"{service_file}: No exception handling found")
    
    return issues

def test_no_circular_dependencies():
    """Test that there are no circular dependencies between modules."""
    graph = build_dependency_graph()
    cycles = find_circular_dependencies(graph)
    
    if cycles:
        message = ["Circular dependencies found:"]
        for cycle in cycles:
            message.append("  " + " -> ".join(cycle + [cycle[0]]))
        pytest.fail("\n".join(message))

def test_layer_boundaries():
    """Test that layer boundaries are respected."""
    graph = build_dependency_graph()
    violations = check_layer_violations(graph)
    
    if violations:
        message = ["Layer boundary violations found:"]
        for source, target in violations:
            message.append(f"  {source} imports {target}")
        pytest.fail("\n".join(message))

def test_shared_lib_usage():
    """Test that shared library code is properly utilized."""
    graph = build_dependency_graph()
    unused = find_unused_shared_lib(graph)
    
    if unused:
        message = ["Unused shared library modules found:"]
        message.extend(f"  - {module}" for module in sorted(unused))
        pytest.fail("\n".join(message))

def test_script_patterns():
    """Test that scripts follow proper patterns."""
    graph = build_dependency_graph()
    issues = check_script_patterns(graph)
    
    if issues:
        message = ["Script pattern violations found:"]
        message.extend(f"  - {issue}" for issue in issues)
        pytest.fail("\n".join(message))

def test_service_patterns():
    """Test that services follow proper patterns."""
    graph = build_dependency_graph()
    issues = check_service_patterns(graph)
    
    if issues:
        message = ["Service pattern violations found:"]
        message.extend(f"  - {issue}" for issue in issues)
        pytest.fail("\n".join(message))

def print_dependency_report():
    """Generate dependency analysis report."""
    graph = build_dependency_graph()
    
    # Module statistics
    module_types = defaultdict(int)
    for _, attrs in graph.nodes(data=True):
        module_types[attrs['type']] += 1
    
    # Get all analysis data
    cycles = find_circular_dependencies(graph)
    violations = check_layer_violations(graph)
    unused = find_unused_shared_lib(graph)
    script_issues = check_script_patterns(graph)
    service_issues = check_service_patterns(graph)
    
    report_data = {
        'module_stats': dict(module_types),
        'cycles': cycles,
        'violations': violations,
        'unused_libs': unused,
        'script_issues': script_issues,
        'service_issues': service_issues
    }
    
    from .reporting import ReportManager
    report_manager = ReportManager()
    report_manager.write_dependency_report(report_data)

@pytest.fixture(scope="session", autouse=True)
def dependency_report():
    """Print dependency report after tests run."""
    yield
    print_dependency_report()

if __name__ == '__main__':
    pytest.main([__file__])
