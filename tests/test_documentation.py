"""Test suite for documentation validation.

This module ensures that our documentation is consistent and complete:
1. All referenced documents and folders exist
2. All existing documents and folders are referenced somewhere
3. No broken links or references
4. Documentation follows project standards
"""

import fnmatch
import os
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path

import pytest
from tools.doc_standards import (
    REQUIRED_DOCS,
    REQUIRED_SECTIONS,
    CODE_DOCUMENTATION,
    validate_doc,
    get_doc_type,
    validate_code_doc
)


def get_all_docs_and_folders() -> Tuple[Set[str], Set[str]]:
    """Get all documentation files and folders in the project.

    Returns:
        Tuple of (doc_paths, folder_paths) relative to project root
    """
    docs = set()
    folders = set()

    # Get project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Files to exclude from documentation checks
    excluded_patterns = [
        "*.egg-info/**/*",  # Package metadata
        "reports/**/*",  # Generated reports
        "reports/*.md",  # Root reports directory files
        "venv/**/*",  # Virtual environment
        ".git/**/*",  # Git files
        ".pytest_cache/**/*",  # Pytest cache
        ".pytest_cache/*.md",  # Pytest cache root markdown files
        "**/__pycache__/**/*",  # Python cache
        "backup/YYYYMMDD/**/*",  # Backup files with date format
        "**/archive/ARCHIVED_*.md",  # Archived files
        "**/archive/README.md",  # Archive directory READMEs
    ]

    for root, dirs, files in os.walk(project_root):
        # Skip excluded directories
        dirs[:] = [
            d
            for d in dirs
            if not any(
                fnmatch.fnmatch(os.path.join(root, d), p) for p in excluded_patterns
            )
        ]

        rel_root = os.path.relpath(root, project_root)
        if rel_root != "." and not any(
            fnmatch.fnmatch(rel_root, p) for p in excluded_patterns
        ):
            folders.add(rel_root)

        for file in files:
            if file.endswith(".md"):
                rel_path = os.path.join(rel_root, file)
                if rel_root == ".":
                    rel_path = file  # Don't add ./ prefix for root files
                if not any(fnmatch.fnmatch(rel_path, p) for p in excluded_patterns):
                    docs.add(rel_path)

    return docs, folders


def extract_doc_references(file_path: str) -> Set[str]:
    """Extract references to other documents from a file.

    Looks for:
    - Markdown links: [text](path)
    - Direct path references: '/path/to/doc.md'
    - Include statements: {% include "path/to/doc" %}
    - Directory references: docs/, infrastructure/
    """
    references = set()

    with open(file_path, "r") as f:
        content = f.read()

    # Find markdown links
    markdown_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
    references.update(
        ref for _, ref in markdown_links if not ref.startswith(("http", "#"))
    )

    # Find quoted paths
    quoted_paths = re.findall(r'[\'"]([^\'"\s]+(?:\.(md|rst|txt)|/))[\'"]', content)
    references.update(path for path, _ in quoted_paths)

    # Find include statements
    includes = re.findall(r'{%\s*include\s*[\'"]([^\'"]+)[\'"]', content)
    references.update(includes)

    # Find direct path references (including directories)
    path_refs = re.findall(r'(?<=[\'"\s])/[^\s\'"]+(?:\.(md|rst|txt)|/)', content)
    references.update(path_refs)

    # Find directory references in markdown links only
    dir_refs = re.findall(r"\[([^\]]+)\]\(([^)]+/)\)", content)
    references.update(
        ref for _, ref in dir_refs if not ref.startswith(("http", "git", "ftp", "#"))
    )

    # Clean up references
    references = {
        ref.strip("`").lstrip("/")
        for ref in references
        if not any(
            ref.startswith(p) for p in ["http", "git", "ftp", "#", "venv", ".git"]
        )
        and not ref.startswith("`/")  # Skip backtick-quoted absolute paths
    }

    return references


def get_all_doc_references() -> Dict[str, Set[str]]:
    """Get all document references from all documentation files.

    Returns:
        Dict mapping source files to sets of referenced paths
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    doc_paths, _ = get_all_docs_and_folders()

    references = {}
    for doc in doc_paths:
        abs_path = os.path.join(project_root, doc)
        try:
            refs = extract_doc_references(abs_path)
            if refs:
                references[doc] = refs
        except Exception as e:
            print(f"Warning: Error processing {doc}: {e}")

    return references


def normalize_path(base_path: str, ref_path: str) -> str:
    """Normalize a referenced path relative to the base path."""
    # Get project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Remove leading slash and normalize path
    if ref_path.startswith("/"):
        ref_path = ref_path.lstrip("/")

    # Handle directory references
    if ref_path.endswith("/"):
        return ref_path.rstrip("/")

    # Handle base path
    if base_path.startswith("./"):
        base_path = base_path[2:]  # Remove ./ prefix
    base_dir = os.path.dirname(os.path.join(project_root, base_path))
    normalized = os.path.normpath(os.path.join(base_dir, ref_path))
    normalized = os.path.relpath(normalized, project_root)

    # Handle fragment identifiers
    if "#" in normalized:
        normalized = normalized.split("#")[0]

    return normalized


def check_doc_references():
    """Check all documentation references.

    Returns:
        Tuple of (broken_refs, unreferenced_docs) where:
        - broken_refs: Dict mapping source docs to sets of broken references
        - unreferenced_docs: Set of existing docs that aren't referenced anywhere
    """
    existing_docs, existing_folders = get_all_docs_and_folders()
    all_references = get_all_doc_references()

    print("\nDebug - Existing docs:")
    for doc in sorted(existing_docs):
        print(f"  - {doc}")

    print("\nDebug - Existing folders:")
    for folder in sorted(existing_folders):
        print(f"  - {folder}")

    # Track broken and valid references
    broken_refs: Dict[str, Set[str]] = {}
    referenced_docs: Set[str] = set()

    # Check each reference
    for source, refs in all_references.items():
        print(f"\nDebug - Checking references in {source}:")
        invalid_refs = set()
        for ref in refs:
            normalized_ref = normalize_path(source, ref)
            print(f"  Reference: {ref}")
            print(f"  Normalized: {normalized_ref}")

            # Try variations of the path
            variations = [
                normalized_ref,
                normalized_ref + ".md",  # Add .md extension
                normalized_ref.replace("-", "_"),  # Replace hyphens with underscores
                normalized_ref.replace("_", "-"),  # Replace underscores with hyphens
                os.path.splitext(normalized_ref)[0],  # Remove extension
            ]
            print(f"  Variations: {variations}")

            # Check if any variation exists
            if not any(v in existing_docs or v in existing_folders for v in variations):
                invalid_refs.add(ref)
                print(f"  Result: Invalid - no variation exists")
            else:
                # Add all variations to referenced docs
                referenced_docs.update(v for v in variations if v in existing_docs)
                print(f"  Result: Valid - found matching variation")

        if invalid_refs:
            broken_refs[source] = invalid_refs

    # Find unreferenced docs
    unreferenced_docs = existing_docs - referenced_docs

    return broken_refs, unreferenced_docs


def print_documentation_report():
    """Generate documentation analysis report."""
    docs, folders = get_all_docs_and_folders()
    all_references = get_all_doc_references()
    broken_refs, unreferenced = check_doc_references()

    # Convert sets to lists for JSON serialization
    broken_refs_json = {src: sorted(list(refs)) for src, refs in broken_refs.items()}
    unreferenced_json = sorted(list(unreferenced))

    report_data = {
        "stats": {
            "doc_count": len(docs),
            "folder_count": len(folders),
            "ref_count": sum(len(refs) for refs in all_references.values()),
        },
        "broken_refs": broken_refs_json,
        "unreferenced": unreferenced_json,
    }

    from .reporting import ReportManager

    report_manager = ReportManager()
    report_manager.write_documentation_report(report_data)


def test_documentation_references():
    """Test that all documentation references are valid and all docs are referenced."""
    broken_refs, unreferenced = check_doc_references()

    # Format error messages
    errors = []

    if broken_refs:
        errors.append("\nBroken document references found:")
        for source, invalid_refs in broken_refs.items():
            errors.append(f"\nIn {source}:")
            for ref in sorted(invalid_refs):
                errors.append(f"  - {ref}")

    if unreferenced:
        errors.append("\nUnreferenced documentation files found:")
        for doc in sorted(unreferenced):
            errors.append(f"  - {doc}")

    if errors:
        errors.insert(0, "Documentation validation failed!")
        pytest.fail("\n".join(errors))


def test_doc_standards():
    """Verify documentation standards compliance."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(project_root, "docs")

    # Check required docs exist and have required sections
    for doc_file in REQUIRED_DOCS:
        doc_path = os.path.join(docs_dir, doc_file)
        assert os.path.exists(doc_path), f"Missing {doc_file}"
        
        if os.path.exists(doc_path):
            doc_type = get_doc_type(Path(doc_path))
            errors = validate_doc(Path(doc_path), doc_type, float('inf'))  # No line limit in tests
            assert not errors, f"Validation errors in {doc_file}:\n" + "\n".join(errors)


def test_code_doc_standards():
    """Verify code documentation standards."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check Python files
    for root, _, files in os.walk(project_root):
        if "tests" in root.split(os.sep) or "venv" in root.split(os.sep):
            continue
            
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                with open(path) as f:
                    content = f.read()
                    errors = validate_code_doc(content)
                    assert not errors, f"Documentation errors in {path}:\n" + "\n".join(errors)


@pytest.fixture(scope="session", autouse=True)
def documentation_report():
    """Print documentation report after tests run."""
    yield
    print_documentation_report()


if __name__ == "__main__":
    pytest.main([__file__])
