"""Test suite for Python package requirements validation.

This module ensures that our requirements.txt is both necessary and sufficient:
1. All listed packages are actually used in the code
2. All imported packages are listed in requirements.txt
3. Version constraints are appropriate
"""

import os
import ast
import sys
import pkg_resources
import importlib.util
from typing import Dict, Set, List, Tuple
from collections import defaultdict
import re

def get_installed_packages() -> Dict[str, str]:
    """Get all installed Python packages and their versions."""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def get_requirements_txt() -> Dict[str, str]:
    """Parse requirements.txt into a dictionary of package names and version specs."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_path = os.path.join(project_root, 'requirements.txt')
    
    if not os.path.exists(requirements_path):
        return {}
    
    requirements = {}
    with open(requirements_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle different requirement formats
                if '>=' in line or '<=' in line or '==' in line:
                    parts = re.split(r'(>=|<=|==)', line, 1)
                    package = parts[0].strip()
                    version_spec = parts[1] + parts[2].strip()
                else:
                    package = line
                    version_spec = None
                requirements[package.lower()] = version_spec
    
    return requirements

class ImportCollector(ast.NodeVisitor):
    """Collect all package imports from Python files."""
    
    def __init__(self):
        self.imports = set()
        self.from_imports = set()
        
    def visit_Import(self, node):
        for name in node.names:
            self.imports.add(name.name.split('.')[0])
            
    def visit_ImportFrom(self, node):
        if node.module:
            self.from_imports.add(node.module.split('.')[0])

def get_imported_packages() -> Set[str]:
    """Get all packages imported in the project's Python files."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    imported_packages = set()
    
    for root, _, files in os.walk(project_root):
        if any(exclude in root for exclude in ['.git', '__pycache__', 'venv', 'env']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        tree = ast.parse(f.read())
                    collector = ImportCollector()
                    collector.visit(tree)
                    imported_packages.update(collector.imports)
                    imported_packages.update(collector.from_imports)
                except Exception as e:
                    print(f"Warning: Error processing {file}: {e}")
    
    # Remove standard library packages
    stdlib_packages = set(sys.stdlib_module_names)
    return {pkg for pkg in imported_packages if pkg.lower() not in stdlib_packages}

def analyze_requirements() -> Dict[str, List[str]]:
    """Analyze requirements for issues."""
    installed = get_installed_packages()
    required = get_requirements_txt()
    imported = get_imported_packages()
    
    issues = defaultdict(list)
    
    # Check for packages in requirements.txt but not imported
    for package in required:
        if package not in imported:
            issues['unused_requirements'].append(package)
    
    # Check for imported packages not in requirements.txt
    for package in imported:
        if package.lower() not in required:
            issues['missing_requirements'].append(package)
    
    # Check for installed packages not in requirements.txt
    for package in installed:
        if package not in required and package in imported:
            issues['undocumented_dependencies'].append(
                f"{package} (installed: {installed[package]})"
            )
    
    # Check version constraints
    for package, version_spec in required.items():
        if version_spec and package in installed:
            installed_version = installed[package]
            if not pkg_resources.require(f"{package}{version_spec}"):
                issues['version_mismatches'].append(
                    f"{package} (required: {version_spec}, installed: {installed_version})"
                )
    
    return dict(issues)

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

def print_requirements_report():
    """Generate requirements analysis report."""
    installed = get_installed_packages()
    required = get_requirements_txt()
    imported = get_imported_packages()
    issues = analyze_requirements()
    
    report_data = {
        'stats': {
            'installed_count': len(installed),
            'required_count': len(required),
            'imported_count': len(imported)
        },
        'issues': issues,
        'details': {
            'installed': installed,
            'required': required,
            'imported': list(imported)
        }
    }
    
    from .reporting import ReportManager
    report_manager = ReportManager()
    report_manager.write_requirements_report(report_data)

@pytest.fixture(scope="session", autouse=True)
def requirements_report():
    """Generate requirements report after tests run."""
    yield
    print_requirements_report()
