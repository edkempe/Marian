"""Test suite for documentation format validation.

This module ensures that our documentation follows consistent formatting:
1. All documents have required headers (Version, Status)
2. Version numbers follow semantic versioning
3. Status values are valid
4. Version history is present and properly formatted
"""

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

import pytest


@dataclass
class DocFormat:
    """Format requirements for a document type."""

    required_headers: Set[str]
    valid_statuses: Set[str]
    requires_version_history: bool


# Document format requirements by type
FORMAT_REQUIREMENTS = {
    "adr": DocFormat(
        required_headers={"Version", "Status"},
        valid_statuses={"Draft", "Review", "Authoritative", "Deprecated"},
        requires_version_history=True,
    ),
    "guide": DocFormat(
        required_headers={"Version", "Status"},
        valid_statuses={"Draft", "Review", "Authoritative", "Deprecated"},
        requires_version_history=True,
    ),
    "core_readme": DocFormat(
        required_headers={"Version", "Status"},
        valid_statuses={"Draft", "Review", "Authoritative", "Deprecated"},
        requires_version_history=True,
    ),
    "simple_readme": DocFormat(
        required_headers={"Version", "Status"},
        valid_statuses={"Draft", "Review", "Authoritative", "Deprecated"},
        requires_version_history=False,
    ),
}

# Directories to exclude from validation
EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    "env",
    "archive",  # Skip archived files
    "node_modules",
    "site-packages",
    "dist-info",
    ".pytest_cache",
}

# Files to exclude from validation
EXCLUDED_FILES = {"CHANGELOG.md", "LICENSE.md", "CONTRIBUTING.md"}

# Core READMEs that require version history
CORE_README_DIRS = {"docs", "models", "services", "shared_lib", "tests"}


def should_validate(file_path: str) -> bool:
    """Check if a file should be validated."""
    # Skip excluded directories
    parts = file_path.split(os.sep)
    if any(part in EXCLUDED_DIRS for part in parts):
        return False

    # Skip excluded files
    if os.path.basename(file_path) in EXCLUDED_FILES:
        return False

    # Only validate .md files
    if not file_path.lower().endswith(".md"):
        return False

    return True


def get_doc_type(file_path: str) -> Optional[str]:
    """Determine document type from path."""
    if "/adr/" in file_path:
        return "adr"
    if file_path.lower().endswith("guide.md"):
        return "guide"
    if file_path.lower().endswith("readme.md"):
        parts = file_path.split(os.sep)
        # Check if this is a core README
        for part in parts:
            if part.lower() in CORE_README_DIRS:
                return "core_readme"
        return "simple_readme"
    return None


def extract_headers(content: str) -> Dict[str, str]:
    """Extract headers from document content."""
    headers = {}
    pattern = r"\*\*([^:]+):\*\*\s*([^\n]+)"
    matches = re.finditer(pattern, content)
    for match in matches:
        key, value = match.groups()
        headers[key.strip()] = value.strip()
    return headers


def validate_version(version: str) -> bool:
    """Validate semantic version number."""
    pattern = r"^\d+\.\d+\.\d+$"
    return bool(re.match(pattern, version))


def check_version_history(content: str) -> bool:
    """Check if document has properly formatted version history."""
    # Look for version history section
    if "## Version History" not in content:
        return False

    # Check for at least one version entry with date
    pattern = r"- \d+\.\d+\.\d+\s*\(\d{4}-\d{2}-\d{2}\):"
    version_match = re.search(pattern, content)
    if not version_match:
        return False

    # Check that entry has description
    version_pos = version_match.end()
    next_section = content.find("\n##", version_pos)
    if next_section == -1:
        next_section = len(content)

    version_content = content[version_pos:next_section].strip()
    return bool(version_content)


def validate_doc_format(file_path: str) -> List[str]:
    """Validate format of a single document.

    Returns:
        List of validation errors, empty if valid
    """
    if not should_validate(file_path):
        return []

    doc_type = get_doc_type(file_path)
    if not doc_type:
        return []  # Skip files without format requirements

    requirements = FORMAT_REQUIREMENTS[doc_type]
    errors = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check headers
    headers = extract_headers(content)
    for required in requirements.required_headers:
        if required not in headers:
            errors.append(f"Missing required header: {required}")

    # Validate version
    if "Version" in headers and not validate_version(headers["Version"]):
        errors.append(f"Invalid version format: {headers['Version']}")

    # Validate status
    if "Status" in headers:
        status = headers["Status"].split("(")[0].strip()  # Remove date if present
        if status not in requirements.valid_statuses:
            errors.append(f"Invalid status: {status}")

    # Check version history
    if requirements.requires_version_history and not check_version_history(content):
        errors.append("Missing or invalid version history section")

    return errors


def test_doc_format():
    """Test that all documentation follows required format."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errors_by_file = {}

    for root, _, files in os.walk(project_root):
        for file in files:
            file_path = os.path.join(root, file)
            errors = validate_doc_format(file_path)
            if errors:
                rel_path = os.path.relpath(file_path, project_root)
                errors_by_file[rel_path] = errors

    if errors_by_file:
        message = ["Documentation format errors found:"]
        for file, errors in errors_by_file.items():
            message.append(f"\n{file}:")
            for error in errors:
                message.append(f"  - {error}")
        pytest.fail("\n".join(message))


if __name__ == "__main__":
    pytest.main([__file__])
