"""Tests to validate API documentation against actual usage."""

import ast
import os
import re
from typing import Dict, Set

import markdown
import pytest


def parse_api_mappings(doc_path: str) -> Dict[str, Dict]:
    """Parse API mappings from documentation.

    Args:
        doc_path: Path to the API mappings markdown file

    Returns:
        Dictionary of API names to their endpoints and models
    """
    apis = {}
    current_api = None
    current_model = None
    skip_sections = {"Notes"}  # Sections to skip

    with open(doc_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Match API headers (## API Name)
            if line.startswith("## "):
                current_api = line.strip("# ").strip()
                current_model = None
                if current_api not in skip_sections:
                    apis[current_api] = {"endpoints": set(), "models": {}}
                else:
                    current_api = None

            # Only process if we're in a valid API section
            elif current_api:
                # Match model headers (### Name)
                if line.startswith("### "):
                    current_model = line.strip("# ").strip()
                    if current_model.endswith(" Model"):
                        current_model = current_model[:-6]
                    apis[current_api]["models"][current_model] = []

                # Match model fields (table rows)
                elif current_model and "|" in line:
                    # Skip table headers and dividers
                    if not line.startswith("|--") and not line.startswith("API Field"):
                        # Parse table row into field mapping
                        fields = [f.strip() for f in line.split("|")[1:-1]]
                        if len(fields) >= 2:  # At least API field and Model field
                            apis[current_api]["models"][current_model].append(
                                {
                                    "api_field": fields[0],
                                    "model_field": fields[1],
                                    "type": fields[2] if len(fields) > 2 else None,
                                    "notes": fields[3] if len(fields) > 3 else None,
                                }
                            )

    return apis


def find_api_imports(code_path: str) -> Set[str]:
    """Find API imports and usage in Python code.

    Args:
        code_path: Directory path to search for Python files

    Returns:
        Set of API names found in the code
    """
    api_patterns = {
        "Gmail API": r"(googleapiclient\.discovery|gmail_api|GmailAPI)",
        "Asset Catalog API": r"(asset_catalog|CatalogAPI)",
        "Anthropic API (Claude)": r"(anthropic\.Client|anthropic_client|APIClient)",
    }

    found_apis = set()

    for root, _, files in os.walk(code_path):
        for file in files:
            if not file.endswith(".py"):
                continue

            try:
                with open(os.path.join(root, file), "r") as f:
                    content = f.read()

                for api_name, pattern in api_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        found_apis.add(api_name)
            except Exception as e:
                print(f"Error reading {file}: {e}")

    return found_apis


def find_model_fields(models_path: str) -> Dict[str, Set[str]]:
    """Extract field names from SQLAlchemy models.

    Args:
        models_path: Path to models directory

    Returns:
        Dictionary mapping model names to sets of field names
    """
    model_fields = {}

    for root, _, files in os.walk(models_path):
        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)
            with open(file_path, "r") as f:
                tree = ast.parse(f.read(), filename=file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    fields = set()
                    for child in node.body:
                        # Get column definitions
                        if isinstance(child, ast.AnnAssign):
                            fields.add(child.target.id)
                        elif isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name):
                                    fields.add(target.id)

                    if fields:  # Only add if fields were found
                        model_fields[node.name] = fields

    return model_fields


def test_api_documentation_completeness():
    """Test that all APIs are properly documented and used."""
    # Get project root directory
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # Parse API documentation
    doc_path = os.path.join(base_dir, "docs", "api_mappings.md")
    documented_apis = parse_api_mappings(doc_path)

    # Find APIs used in code
    used_apis = set()
    for code_path in [
        os.path.join(base_dir, "models"),
        os.path.join(base_dir, "shared_lib"),
        os.path.join(base_dir, "src"),
    ]:
        used_apis.update(find_api_imports(code_path))

    # Validate documentation coverage
    undocumented = used_apis - set(documented_apis.keys())
    assert (
        not undocumented
    ), f"Found APIs in code that are not documented: {undocumented}"

    # Validate API usage
    unused = set(documented_apis.keys()) - used_apis
    assert not unused, f"Found documented APIs that are not used in code: {unused}"


def test_model_field_documentation():
    """Test that all model fields are documented in API mappings."""
    # Get project root directory
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # Parse API documentation
    doc_path = os.path.join(base_dir, "docs", "api_mappings.md")
    documented_apis = parse_api_mappings(doc_path)

    # Get actual model fields
    models_path = os.path.join(base_dir, "models")
    model_fields = find_model_fields(models_path)

    # Check each documented API's models
    for api_name, api_info in documented_apis.items():
        for model_name, field_mappings in api_info["models"].items():
            # Skip if model doesn't exist (might be response model)
            if model_name not in model_fields:
                continue

            # Get documented model fields
            documented_fields = {mapping["model_field"] for mapping in field_mappings}

            # Get actual model fields
            actual_fields = model_fields[model_name]

            # Check for missing fields in documentation
            missing_fields = actual_fields - documented_fields
            assert (
                not missing_fields
            ), f"Model {model_name} has undocumented fields: {missing_fields}"

            # Check for extra fields in documentation
            extra_fields = documented_fields - actual_fields
            assert (
                not extra_fields
            ), f"Model {model_name} documentation has extra fields: {extra_fields}"


if __name__ == "__main__":
    pytest.main([__file__])
