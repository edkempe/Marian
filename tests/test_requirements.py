"""Test requirements for Marian project."""

import os
import re
import sys
from importlib import metadata
from pathlib import Path
from typing import Dict, List, Set, Union

import pytest

from shared_lib.constants import (
    DEV_DEPENDENCIES,
    IMPORT_PATTERNS,
    LOCAL_MODULES,
    PACKAGE_ALIASES,
)


def get_installed_packages() -> Dict[str, str]:
    """Get dictionary of installed packages and their versions."""
    return {dist.metadata['Name']: dist.version for dist in metadata.distributions()}


def get_requirements() -> Dict[str, str]:
    """Get dictionary of required packages and their versions from requirements.txt."""
    requirements = {}
    with open("requirements.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if ">=" in line:
                    pkg, version = line.split(">=")
                elif "==" in line:
                    pkg, version = line.split("==")
                else:
                    continue
                requirements[pkg.strip()] = version.strip()
    return requirements


def get_imports_from_file(file_path: str) -> Set[str]:
    """Extract import statements from a Python file."""
    imports = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract imports using patterns from constants
        for pattern in IMPORT_PATTERNS:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                pkg = (
                    match.group(1)
                    if len(match.groups()) > 0
                    else match.group(0).split()[1]
                )
                if pkg in PACKAGE_ALIASES:
                    pkg = PACKAGE_ALIASES[pkg]
                if not is_local_import(pkg):
                    imports.add(pkg.lower())

    except Exception as e:
        print(f"Warning: Error processing {os.path.basename(file_path)}: {str(e)}")

    return imports


def is_local_import(pkg: str) -> bool:
    """Check if an import is local to the project."""
    return pkg.lower() in LOCAL_MODULES


def get_all_imports() -> Set[str]:
    """Get all imports from Python files in the project."""
    imports = set()
    for root, _, files in os.walk("."):
        if "venv" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                imports.update(get_imports_from_file(path))
    return imports


def analyze_requirements() -> Dict[str, Set[str]]:
    """Analyze requirements for issues."""
    issues = {}

    # Get installed packages
    installed_packages = get_installed_packages()

    # Read requirements.txt
    requirements = get_requirements()

    # Get all imports
    imports = get_all_imports()

    # Check for unused requirements
    unused = set(requirements) - imports - DEV_DEPENDENCIES
    if unused:
        issues["unused_requirements"] = unused

    # Check for missing requirements
    required = set(requirements)
    missing = {imp for imp in imports if imp not in required and imp in installed_packages}
    if missing:
        issues["missing_requirements"] = missing

    # Check for undocumented dependencies
    undocumented = {
        f"{pkg} (installed: {ver})"
        for pkg, ver in installed_packages.items()
        if pkg in imports and pkg not in required
    }
    if undocumented:
        issues["undocumented_dependencies"] = undocumented

    return issues


def test_requirements():
    """Test that requirements.txt is both necessary and sufficient."""
    issues = analyze_requirements()

    # Format error messages
    error_messages = []
    if "unused_requirements" in issues:
        error_messages.append(
            f"Unused requirements in requirements.txt: {', '.join(sorted(issues['unused_requirements']))}"
        )
    if "missing_requirements" in issues:
        error_messages.append(
            f"Missing requirements from requirements.txt: {', '.join(sorted(issues['missing_requirements']))}"
        )
    if "undocumented_dependencies" in issues:
        error_messages.append(
            f"Undocumented dependencies: {', '.join(sorted(issues['undocumented_dependencies']))}"
        )

    # Assert no issues found
    assert not error_messages, "\n".join(error_messages)


def test_required_packages():
    """Test that all required packages are installed."""
    installed = get_installed_packages()
    requirements = get_requirements()

    missing = []
    for pkg, req_version in requirements.items():
        if pkg not in installed:
            missing.append(f"{pkg}>={req_version}")

    assert not missing, f"Missing required packages: {', '.join(missing)}"


def test_python_version():
    """Test Python version meets requirements."""
    min_version = (3, 8)
    current_version = sys.version_info[:2]
    assert current_version >= min_version, (
        f"Python version {'.'.join(map(str, current_version))} is not supported. "
        f"Please use Python {'.'.join(map(str, min_version))} or higher."
    )


def requirements_report():
    """Generate requirements report after tests run."""
    issues = analyze_requirements()
    if issues:
        print("\nRequirements Analysis Report:")
        for issue_type, items in issues.items():
            print(f"\n{issue_type.replace('_', ' ').title()}:")
            for item in sorted(items):
                print(f"  - {item}")


@pytest.fixture(scope="session", autouse=True)
def requirements_report_fixture():
    """Generate requirements report after tests run."""
    yield
    requirements_report()


REQUIRED_TEST_PACKAGES = [
    "pytest>=7.0.0",
    "pytest-cov>=4.1.0",
    "factory-boy>=3.3.0",  # For test data generation
]

def test_requirements_installed():
    """Verify all required test packages are installed."""
    import pkg_resources
    
    for package in REQUIRED_TEST_PACKAGES:
        name = package.split(">=")[0]
        version = package.split(">=")[1]
        pkg_resources.require(f"{name}>={version}")
